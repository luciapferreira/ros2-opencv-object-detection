from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
   camera_type = LaunchConfiguration('camera_type')
    
   return LaunchDescription([
        DeclareLaunchArgument(
            'camera_type',
            default_value='video1',  # matches camera_driver mapping -> video1 => test1.mov
            description='Device ID (/dev/video0), "video0"/"video1" to use packaged samples, or a video file path'
        ),

        Node(
            package='opencv_object_detection',
            executable='camera_driver',
            name='camera_driver',
            output='screen',
            parameters=[{'camera_type': camera_type}]
        ),
        Node(
            package='opencv_object_detection',
            executable='camera_rectifier',
            output='screen',
            name='camera_rectifier'
        ),
        Node(
            package='opencv_object_detection',
            executable='image_convert',
            output='screen',
            name='image_convert'
        ),
        Node(
            package='opencv_object_detection',
            executable='object_detection',
            output='screen',
            name='object_detection'
        ),
        Node(
            package='opencv_object_detection',
            executable='camera_reader',
            output='screen',
            name='camera_reader'
        ),
   ])
