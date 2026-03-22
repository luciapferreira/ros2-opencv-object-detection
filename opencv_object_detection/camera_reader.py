import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
from sensor_msgs.msg import Image


class CameraReader(Node):

    def __init__(self):
        super().__init__('camera_reader')
        self.bridge = CvBridge()
        # Subcribe the /camera/image_raw topic
        self.sub_image_og = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.og_reader_callback,
            10
        )
        self.sub_image_rect = self.create_subscription(
            Image,
            "/camera/image_rect",
            self.rect_reader_callback,
            10
        )
        self.sub_image_processed = self.create_subscription(
            Image,
            "/camera/image_processed",
            self.proc_reader_callback,
            10
        )

        self.sub_image_object = self.create_subscription(
            Image, 
            '/camera/object_detection', 
            self.obj_reader_callback, 
            10
        )

    def og_reader_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg)
        cv2.imshow("Camera Raw Feed", cv_image)
        cv2.waitKey(3)
    
    def rect_reader_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg)
        cv2.imshow("Camera Rectifier Feed", cv_image)
        cv2.waitKey(3)

    def proc_reader_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg)
        cv2.imshow("Camera Processed Feed", cv_image)
        cv2.waitKey(3)

    def obj_reader_callback(self, msg):
        cv_image = self.bridge.imgmsg_to_cv2(msg)
        cv2.imshow('Object Detected', cv_image)  
        cv2.waitKey(3)


def main(args=None):
    rclpy.init(args=args)

    camera_reader = CameraReader()

    rclpy.spin(camera_reader)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
