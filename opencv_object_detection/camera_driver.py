#!/usr/bin/env python3
import os
import time
import rclpy
import cv2
import ament_index_python
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge


class CameraDriver(Node):
    def __init__(self):
        super().__init__('camera_driver')

        # declare & read parameter
        self.declare_parameter('camera_type', '/dev/video0')
        camera_param = self.get_parameter('camera_type').value

        # packaged videos directory
        video_dir = os.path.join(
            ament_index_python.get_package_share_directory('opencv_object_detection'),
            'video'
        )

        # Accept only 'video0', 'video1', or '/dev/...'
        if camera_param == 'video0':
            self.src = os.path.join(video_dir, 'test.mov')
        elif camera_param == 'video1':
            self.src = os.path.join(video_dir, 'test1.mov')
        elif isinstance(camera_param, str) and camera_param.startswith('/dev/'):
            self.src = camera_param
        else:
            self.get_logger().warn(
                f"Invalid camera_type '{camera_param}', defaulting to /dev/video0"
            )
            self.src = '/dev/video0'

        self.get_logger().info(f"Camera source -> {self.src}")

        self.cap = None
        self.bridge = CvBridge()
        # Use a relative topic name to avoid accidental absolute remapping
        self.pub = self.create_publisher(Image, 'camera/image_raw', 10)

        self.timer = self.create_timer(0.03, self.timer_cb)

        # Try open at start
        self.openCamera()

    def openCamera(self):
        """
        Try to open video or device.
        For /dev devices try V4L2 + MJPG.
        """
        try:
            if isinstance(self.src, str) and self.src.startswith('/dev/'):
                # Open with V4L2 backend first
                cap = cv2.VideoCapture(self.src, cv2.CAP_V4L2)

                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_FPS, 30)

            else:
                # File path or packaged video
                cap = cv2.VideoCapture(self.src)
        except Exception as e:
            self.get_logger().warning(f"open err: {e}")
            return False

        if not cap or not cap.isOpened():
            try:
                cap.release()
            except Exception:
                pass
            self.get_logger().warning(f"Failed to open: {self.src}")
            return False

        # warm-up read
        time.sleep(0.05)
        ok, frame = cap.read()
        if not ok or frame is None:
            try:
                cap.release()
            except Exception:
                pass

            if isinstance(self.src, str) and self.src.startswith('/dev/'):
                try:
                    cap = cv2.VideoCapture(self.src)
                    time.sleep(0.05)
                    ok, frame = cap.read()
                except Exception:
                    ok, frame = False, None
            else:
                ok, frame = False, None

            if not ok or frame is None:
                try:
                    cap.release()
                except Exception:
                    pass
                self.get_logger().warning(f"Cannot read first frame from {self.src}")
                return False

        self.cap = cap
        self.get_logger().info("Camera opened successfully")
        return True

    def timer_cb(self):
        # Ensure camera is open
        if not self.cap or not self.cap.isOpened():
            if not self.openCamera():
                return

        try:
            ret, frame = self.cap.read()
        except Exception as e:
            self.get_logger().warning(f"read err: {e}")
            ret, frame = False, None

        if not ret or frame is None:
            try:
                if self.cap:
                    self.cap.release()
            except Exception:
                pass
            self.cap = None
            return

        try:
            img_msg = self.bridge.cv2_to_imgmsg(frame, encoding="bgr8")
        except Exception:
            try:
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
                img_msg = self.bridge.cv2_to_imgmsg(frame_bgr, encoding="bgr8")
            except Exception as e:
                self.get_logger().warning(f"cv2_to_imgmsg failed: {e}")
                return

        img_msg.header.stamp = self.get_clock().now().to_msg()
        img_msg.header.frame_id = 'camera'
        self.pub.publish(img_msg)

def main(args=None):
    rclpy.init(args=args)

    camera_driver = CameraDriver()

    rclpy.spin(camera_driver)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
