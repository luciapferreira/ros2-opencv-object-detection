from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'opencv_object_detection'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'video'), glob('video/*.mov')),
        (os.path.join('share', package_name, 'calibration/images'), glob('calibration/images/*')),
        (os.path.join('share', package_name, 'calibration'), glob(os.path.join('calibration', '*ost.[pxy][yma]*'))),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Lucia Ferreira',
    maintainer_email='ana.lucia.piferreira@gmail.com',
    description='A ROS 2 package implementing a 2D image processing and object detection pipeline using OpenCV, including camera calibration, rectification, edge detection, and contour-based object detection.',
    license='MIT',
    entry_points={
        'console_scripts': [
            'camera_driver = opencv_object_detection.camera_driver:main',
            'camera_reader = opencv_object_detection.camera_reader:main',
            'camera_rectifier = opencv_object_detection.camera_rectifier:main',
            'camera_calibration_pub = opencv_object_detection.camera_calibration_pub:main',
            'image_convert = opencv_object_detection.image_convert:main',
            'object_detection = opencv_object_detection.object_detection:main',
        ],
    },
)
