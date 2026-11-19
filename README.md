# Computer-Vision-Project

A Python computer-vision project containing two independent programs based on the
uploaded source files. The original algorithms and program logic are preserved;
the source files have only been renamed for clarity.

## Project contents

| File | Description |
|---|---|
| `camera_frame_capture.py` | Opens the default camera, captures for 5 seconds, stores every 5th frame in memory, then repeatedly plays the extracted frames at 10 FPS until `q` is pressed. |
| `perspective_rectification.py` | Demonstrates three-view perspective rectification and red-object coordinate comparison. It supports synthetic sample images and a camera mode that captures three physical views. |
| `requirements.txt` | Python package dependencies. |

## Requirements

- Python 3
- A webcam for camera-based modes
- A desktop environment that supports OpenCV display windows

## Installation

Create and activate a virtual environment (recommended), then install dependencies:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\\Scripts\\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install packages:

```bash
python -m pip install -r requirements.txt
```

## Run

### 1. Camera frame capture

```bash
python camera_frame_capture.py
```

The program captures for 5 seconds, extracts every 5th frame in memory, and loops
the extracted frames at 10 FPS. Press `q` to exit.

### 2. Perspective rectification and object-coordinate comparison

```bash
python perspective_rectification.py
```

Choose:

- `1` — generate three synthetic perspective views, rectify them to a top-down
  view, and compare the detected red-object coordinates.
- `2` — use the camera to capture three physical views. Press `c` to capture each
  view; after all three are captured, the program processes and compares them.

Press `q` in the OpenCV windows to exit.

## Notes

- The two Python scripts are separate entry points; run them independently.
- The camera scripts use camera device index `0` by default.
- The perspective script's synthetic mode generates demonstration images. Its
  physical-camera mode depends on the camera seeing a desktop/table boundary that
  the contour-based detector can identify.
- OpenCV GUI windows require a graphical desktop session; they may not work in a
  headless environment.

## GitHub

When creating the repository, use the name `Computer-Vision-Project` and set
**Visibility** to **Private** before uploading.
