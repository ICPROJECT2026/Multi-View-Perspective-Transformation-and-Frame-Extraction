#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
================================================================================
Project Name: Three-Perspective Rectification & Object Detection Verification System (Persistent Window Edition)
Function Description:
1. Automatically generates 3 synthetic desktop images from different angles (left-skewed, right-skewed, high top-down view).
2. Uniformly transforms them into standard top-down perspective views and performs coordinate consistency checking.
3. Adds an infinite keyboard loop (waitKey(0)) to ensure the three comparison views remain persistently displayed.
================================================================================
"""

import cv2
import numpy as np
import time

# ==============================================================================
# 1. Basic Configuration Parameters
# ==============================================================================
TABLE_REAL_WIDTH = 100.0   # Real desktop width (cm)
TABLE_REAL_HEIGHT = 60.0   # Real desktop height (cm)

WARP_WIDTH = 500           # Uniform width of transformed top-down view (pixels)
WARP_HEIGHT = 300          # Uniform height of transformed top-down view (pixels)

# ==============================================================================
# 2. Core Algorithm Utility Classes
# ==============================================================================
class PerspectiveCalibrator:
    @staticmethod
    def order_points(pts):
        """Sorts 4 vertices clockwise as [top-left, top-right, bottom-right, bottom-left]"""
        pts = np.array(pts, dtype=np.float32)
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        return np.array([
            pts[np.argmin(s)],
            pts[np.argmin(diff)],
            pts[np.argmax(s)],
            pts[np.argmax(diff)]
        ], dtype=np.float32)

    @classmethod
    def auto_detect_table(cls, frame):
        """Automatically extracts the four corners of the desktop contour"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 50, 150)

        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        best_quad = None
        max_area = 0

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 3000:
                peri = cv2.arcLength(cnt, True)
                approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
                if len(approx) == 4 and area > max_area:
                    max_area = area
                    best_quad = approx.reshape(4, 2)

        return cls.order_points(best_quad) if best_quad is not None else None

    @classmethod
    def warp_to_topdown(cls, frame, corners):
        """Performs perspective transformation from any view to standard top-down view"""
        src_pts = cls.order_points(corners)
        dst_pts = np.array([
            [0, 0],
            [WARP_WIDTH - 1, 0],
            [WARP_WIDTH - 1, WARP_HEIGHT - 1],
            [0, WARP_HEIGHT - 1]
        ], dtype=np.float32)

        M = cv2.getPerspectiveTransform(src_pts, dst_pts)
        warped = cv2.warpPerspective(frame, M, (WARP_WIDTH, WARP_HEIGHT))
        return warped, M

    @staticmethod
    def detect_red_object(frame):
        """Identifies prominent red reference objects in the top-down view and returns pixel coordinates"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
        mask2 = cv2.inRange(hsv, np.array([170, 120, 70]), np.array([180, 255, 255]))
        mask = cv2.bitwise_or(mask1, mask2)
        
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if cv2.contourArea(cnt) > 50:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    return (cx, cy)
        return None

# ==============================================================================
# 3. Simulate generating 3 desktop images from different angles
# ==============================================================================
def generate_3_perspective_images():
    frames = []
    real_target = (40.0, 25.0)

    perspectives = [
        np.array([[80, 120], [450, 80], [580, 420], [120, 380]], dtype=np.float32),
        np.array([[180, 70], [540, 110], [480, 400], [60, 420]], dtype=np.float32),
        np.array([[100, 60], [540, 60], [540, 420], [100, 420]], dtype=np.float32)
    ]

    for idx, corners in enumerate(perspectives):
        img = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.fillPoly(img, [corners.astype(int)], (150, 180, 200))
        cv2.polylines(img, [corners.astype(int)], True, (255, 255, 255), 2)

        dst_pts = np.array([[0,0], [WARP_WIDTH,0], [WARP_WIDTH,WARP_HEIGHT], [0,WARP_HEIGHT]], dtype=np.float32)
        H_inv = cv2.getPerspectiveTransform(dst_pts, corners)
        
        target_pixel_warp = np.array([[[
            real_target[0] / TABLE_REAL_WIDTH * WARP_WIDTH,
            real_target[1] / TABLE_REAL_HEIGHT * WARP_HEIGHT
        ]]], dtype=np.float32)
        
        target_pixel_orig = cv2.perspectiveTransform(target_pixel_warp, H_inv)[0][0]
        
        cv2.circle(img, tuple(target_pixel_orig.astype(int)), 12, (0, 0, 255), -1)
        cv2.putText(img, f"View {idx+1}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        frames.append(img)
        
    return frames

# ==============================================================================
# 4. Transformation and Cross-Comparison Pipeline (Persistent Windows)
# ==============================================================================
def process_and_compare_views(frames):
    print("\n" + "="*60)
    print("🚀 [Perspective Transformation & Converted View Comparison]")
    print("="*60)

    real_coords = []

    for i, frame in enumerate(frames):
        corners = PerspectiveCalibrator.auto_detect_table(frame)
        if corners is None:
            print(f"❌ View {i+1}: Failed to detect the 4 corners of the desktop!")
            continue

        warped, _ = PerspectiveCalibrator.warp_to_topdown(frame, corners)
        obj_center = PerspectiveCalibrator.detect_red_object(warped)
        
        if obj_center:
            real_x = (obj_center[0] / WARP_WIDTH) * TABLE_REAL_WIDTH
            real_y = (obj_center[1] / WARP_HEIGHT) * TABLE_REAL_HEIGHT
            real_coords.append((real_x, real_y))
            
            cv2.circle(warped, obj_center, 6, (0, 255, 0), -1)
            cv2.putText(warped, f"({real_x:.1f},{real_y:.1f})cm", (obj_center[0]+8, obj_center[1]-8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        # Real-time display of original image and corresponding top-down rectified image
        cv2.imshow(f"Original Perspective {i+1}", frame)
        cv2.imshow(f"Converted Top-Down View {i+1}", warped)

    if len(real_coords) == 3:
        p1, p2, p3 = np.array(real_coords[0]), np.array(real_coords[1]), np.array(real_coords[2])
        err12 = np.linalg.norm(p1 - p2)
        err23 = np.linalg.norm(p2 - p3)
        err13 = np.linalg.norm(p1 - p3)
        max_err = max(err12, err23, err13)

        print(f"📊 Converted Coordinate Comparison:")
        print(f"   - View 1 Converted Coordinates: ({p1[0]:.2f}, {p1[1]:.2f}) cm")
        print(f"   - View 2 Converted Coordinates: ({p2[0]:.2f}, {p2[1]:.2f}) cm")
        print(f"   - View 3 Converted Coordinates: ({p3[0]:.2f}, {p3[1]:.2f}) cm")
        print(f"   - Max Relative Rectification Error across 3 Images: {max_err:.2f} cm")

        if max_err <= 2.0:
            print("✅ 【Verification Result: PASS】 3 images successfully normalized to uniform top-down view, consistency > 90%!")
        else:
            print("❌ 【Verification Result: FAIL】 Normalized view coordinate deviation is too large.")

    print("\n👉 All comparison windows have been generated and remain persistently displayed. Please observe the windows on screen and press the 'q' key to safely exit the program.")
    
    # Core infinite loop: keeps windows persistent until user presses 'q'
    while True:
        key = cv2.waitKey(100) & 0xFF
        if key == ord('q'):
            break
    cv2.destroyAllWindows()

# ==============================================================================
# 5. Camera Three-Shot Verification Mode
# ==============================================================================
def run_camera_three_shots():
    print("\n" + "="*60)
    print("📷 [Starting Camera 3-Shot Verification Mode]")
    print("Please point at the desktop and press 'c' sequentially to capture 3 photos from different angles...")
    print("="*60)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open local camera.")
        return

    captured_frames = []
    
    while len(captured_frames) < 3:
        ret, frame = cap.read()
        if not ret:
            break

        display = frame.copy()
        cv2.putText(display, f"Captured: {len(captured_frames)}/3  (Press 'c' to Capture)", 
                    (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow("Camera Live Stream", display)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            captured_frames.append(frame.copy())
            print(f"Successfully captured physical photo #{len(captured_frames)}!")
            time.sleep(0.5)
        elif key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if len(captured_frames) == 3:
        process_and_compare_views(captured_frames)

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    print("Please select functional mode:")
    print("1 = Run 3-perspective synthetic image rectification & comparison sample (windows stay open)")
    print("2 = Call camera to capture 3 physical photos sequentially for comparison testing (windows stay open)")
    choice = input("Please enter your option (1 or 2): ").strip()

    if choice == "2":
        run_camera_three_shots()
    else:
        sample_frames = generate_3_perspective_images()
        process_and_compare_views(sample_frames)