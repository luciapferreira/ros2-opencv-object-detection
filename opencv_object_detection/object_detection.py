import rclpy
import cv2
import os, ament_index_python
from message_filters import Subscriber, TimeSynchronizer
from rclpy.node import Node
from sensor_msgs.msg import Image
from matplotlib import pyplot as plt 

from cv_bridge import CvBridge

class ObjectDetection(Node):

    def __init__(self):
        super().__init__('object_detection')

        self.bridge = CvBridge()
        self.sub_image_rect = self.create_subscription(Image,'/camera/image_rect', self.rect_listener_callback,10)
        self.sub_image_processed = self.create_subscription(Image,'/camera/image_processed', self.processed_listener_callback,10)
        self.pub_object_detection = self.create_publisher(Image, '/camera/object_detection', 10)
        
        self.processed_image = None

    def processed_listener_callback(self, msg):
        self.processed_image = self.bridge.imgmsg_to_cv2(msg)
    
    def rect_listener_callback(self, msg):
        rect_image = self.bridge.imgmsg_to_cv2(msg)

        if self.processed_image is not None:
            # Creating Contours
            contours, _ = cv2.findContours(self.processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            bound_image = rect_image.copy()

            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 1000 or area > 1000000:
                    continue

                # Get the bounding box for the contour
                x, y, w, h = cv2.boundingRect(contour)

                # Draw the bounding box on the rectified image
                bound_image = cv2.rectangle(bound_image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Publish the object detection result
            self.pub_object_detection.publish(self.bridge.cv2_to_imgmsg(bound_image))

def main(args=None):
    rclpy.init(args=args)

    object_detection = ObjectDetection()

    rclpy.spin(object_detection)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    rclpy.shutdown()


if __name__ == '__main__':
    main()
