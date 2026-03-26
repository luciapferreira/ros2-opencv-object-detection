# ros2-opencv-object-detection

![ROS 2](https://img.shields.io/badge/ROS2-Humble-blue) ![Python](https://img.shields.io/badge/Python-3.10-blue) ![License](https://img.shields.io/badge/License-MIT-green)

A ROS 2 (Humble) package implementing a complete 2D image processing and object detection pipeline, developed as a university assignment. The pipeline covers camera driving, calibration, rectification, edge-based image processing, and contour-based object detection — all built with OpenCV and integrated into the ROS 2 ecosystem.

## Package Structure

```
ros2-opencv-object-detection/
├── opencv_object_detection/
│   ├── camera_driver.py          # Publishes frames from webcam or video file
│   ├── camera_reader.py          # Displays all image topics via OpenCV windows
│   ├── camera_calibration_pub.py # Streams calibration images for cameracalibrator
│   ├── camera_rectifier.py       # Undistorts frames using a calibration YAML
│   ├── image_convert.py          # Grayscale → Gaussian blur → Canny edge detection
│   └── object_detection.py       # Contour-based bounding box object detection
├── launch/
│   └── launch.py                 # Launches the full pipeline
├── calibration/
│   ├── ost.yaml                  # Camera calibration parameters
│   └── images/                   # Chessboard snapshots for calibration
├── video/
│   ├── test.mov                  # Sample video (video0)
│   └── test1.mov                 # Sample video (video1)
├── package.xml
├── setup.py
└── setup.cfg
```

## Pipeline Overview

```
camera_driver  →  /camera/image_raw
                        │
               camera_rectifier  →  /camera/image_rect
                                            │
                                    image_convert  →  /camera/image_processed
                                            │                    │
                                    object_detection  ←──────────┘
                                            │
                                   /camera/object_detection
                                            │
                                    camera_reader  (displays all feeds)
```

## Nodes

| Node | Subscribes | Publishes | Description |
|------|-----------|-----------|-------------|
| `camera_driver` | — | `/camera/image_raw` | Reads from webcam or `.mov` file |
| `camera_rectifier` | `/camera/image_raw` | `/camera/image_rect` | Undistorts using `ost.yaml` |
| `image_convert` | `/camera/image_rect` | `/camera/image_processed` | Grayscale → Blur → Canny → Dilate/Erode |
| `object_detection` | `/camera/image_rect`, `/camera/image_processed` | `/camera/object_detection` | Contour-based bounding boxes |
| `camera_reader` | all image topics | — | Displays all feeds via `cv2.imshow` |
| `camera_calibration_pub` | — | `/camera/image_raw` | Streams saved chessboard images for calibration |

## Requirements

- ROS 2 Humble
- Ubuntu 22.04
- Python packages: `opencv-python`, `cv_bridge`, `image_geometry`, `PyYAML`, `numpy<2`
- ROS packages: `sensor_msgs`, `message_filters`

Install the camera calibration tool:
```bash
sudo apt install ros-humble-camera-calibration
```

## Build & Install

```bash
cd ~/ros2_ws
colcon build --packages-select opencv_object_detection
source install/setup.bash
```

## Usage

### Launch the full pipeline

```bash
ros2 launch opencv_object_detection launch.py
```

By default this uses `test1.mov`. To use a different source:

```bash
# Packaged sample video
ros2 launch opencv_object_detection launch.py camera_type:=video0

# Live webcam
ros2 launch opencv_object_detection launch.py camera_type:=/dev/video0
```

### Run nodes individually

```bash
ros2 run opencv_object_detection camera_driver
ros2 run opencv_object_detection camera_rectifier
ros2 run opencv_object_detection image_convert
ros2 run opencv_object_detection object_detection
ros2 run opencv_object_detection camera_reader
```

### Camera Calibration

Stream the bundled chessboard images and run the calibrator:

```bash
# Terminal 1
ros2 run opencv_object_detection camera_calibration_pub

# Terminal 2
ros2 run camera_calibration cameracalibrator \
  --size 8x6 --square 0.0745 \
  --ros-args -r image:=/camera/image_raw -r camera:=/camera
```

When the CALIBRATE button activates, click it, then SAVE. Move the resulting `ost.yaml` to the `calibration/` folder and rebuild.

## Image Processing Details

The `image_convert` node applies the following sequence to each rectified frame:

1. Convert BGR → Grayscale
2. Iterative Gaussian Blur (kernels 1×1 to 21×21, odd steps)
3. Canny Edge Detection (low=30, high=50)
4. Dilation (5 iterations, 2×2 kernel)
5. Erosion (2 iterations, 2×2 kernel)

## Known Issues

- **OpenCV GUI on WSL** — `cv2.imshow` requires a display server. Make sure `DISPLAY` is set correctly and `opencv-python` (not `opencv-python-headless`) is installed.
- **NumPy compatibility** — OpenCV may conflict with NumPy 2.x. If you encounter import errors, downgrade with `pip install "numpy<2"`.
