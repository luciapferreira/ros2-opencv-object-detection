import rclpy
import cv2
import numpy as np
import os, ament_index_python, yaml, image_geometry

from rclpy.node import Node
from sensor_msgs.msg import Image, CameraInfo

from cv_bridge import CvBridge

class CameraRectifier(Node):

    def __init__(self):
        super().__init__('camera_rectifier')

        self.bridge = CvBridge()
        self.pub_image_rect = self.create_publisher(Image, '/camera/image_rect', 10)
        self.sub_image_raw = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.rectifier_callback,
            10
        )

        self.camera_model=image_geometry.PinholeCameraModel()

        # Select the ost.yaml file to get the camera calibration parameters
        ost_file = os.path.join(ament_index_python.get_package_share_directory('opencv_object_detection'), 'calibration','ost.yaml')
        self.load_camera_calibration(ost_file)

        self.camera_model.fromCameraInfo(self.camera_info)
    
    def load_camera_calibration(self, calibration_path):
        self.camera_info = CameraInfo()
        with open(os.path.join(calibration_path), 'r') as f:
            calibration_file = yaml.safe_load(f)
        self.camera_info.width = calibration_file['image_width']
        self.camera_info.height = calibration_file['image_height']
        self.camera_info.distortion_model = calibration_file['distortion_model']
        self.camera_info.d = calibration_file['distortion_coefficients']['data']
        self.camera_info.k = calibration_file['camera_matrix']['data']
        self.camera_info.r = calibration_file['rectification_matrix']['data']
        self.camera_info.p = calibration_file['projection_matrix']['data']

    def rectifier_callback(self, msg):
        # Load the image and apply the Rectification
        cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        cv_image_rect = cv_image.copy()
        
        self.camera_model.rectifyImage(cv_image, cv_image_rect)

        # Create the msg and publish
        cv_msg = self.bridge.cv2_to_imgmsg(cv_image_rect, "bgr8")
        self.pub_image_rect.publish(cv_msg)
        
def main(args=None):
    rclpy.init(args=args)

    camera_rectifier = CameraRectifier()

    rclpy.spin(camera_rectifier)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
