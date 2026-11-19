import time
import cv2


def main():
  # Open default camera (index 0)
  cap = cv2.VideoCapture(0)
  if not cap.isOpened():
    print("Error: Could not open camera.")
    return

  interval = 5  # Extract every 5th frame to save performance
  duration = 5  # Capture duration in seconds
  extracted_frames = []

  print(
      f"--- Phase 1: Capturing live feed for {duration} seconds (In-memory"
      " only, no disk saving) ---"
  )

  start_time = time.time()
  frame_count = 0

  while True:
    ret, frame = cap.read()
    if not ret:
      print("Error: Failed to grab frame from camera.")
      break

    # Show input live feed window
    cv2.imshow("Input Window (Capturing...) - Press 'q' to abort", frame)

    # Frame extraction and storage in RAM
    if frame_count % interval == 0:
      extracted_frames.append(frame.copy())

    frame_count += 1

    # Stop automatically after 5 seconds
    if time.time() - start_time >= duration:
      print(
          f"\n5 seconds reached! Captured {len(extracted_frames)} extracted"
          " frames into memory."
      )
      break

    # Allow early exit if user presses 'q' during capture
    if cv2.waitKey(1) & 0xFF == ord("q"):
      print("\nCapture aborted by user.")
      break

  # Release camera and close input window
  cap.release()
  cv2.destroyAllWindows()

  if not extracted_frames:
    print("No frames were extracted.")
    return

  print(
      "\n--- Phase 2: Playing extracted video output ---"
      "\n(Press 'q' in the output window to finally exit)"
  )

  # Playback settings (e.g., 10 frames per second for smooth viewing)
  playback_fps = 10
  delay_ms = int(1000 / playback_fps)

  # Loop playback until user presses 'q'
  while True:
    for frame in extracted_frames:
      cv2.imshow("Output Window (Extracted Frames)", frame)

      # Check for 'q' key press to exit
      if cv2.waitKey(delay_ms) & 0xFF == ord("q"):
        print("\nExiting program as requested.")
        cv2.destroyAllWindows()
        return


if __name__ == "__main__":
  main()


  