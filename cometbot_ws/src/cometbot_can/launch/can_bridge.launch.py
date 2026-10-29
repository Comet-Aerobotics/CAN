"""Start the can_bridge node with config/can_bridge.yaml.

    ros2 launch cometbot_can can_bridge.launch.py
    ros2 launch cometbot_can can_bridge.launch.py can_interface:=vcan0   # no hardware
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('cometbot_can'), 'config', 'can_bridge.yaml')

    return LaunchDescription([
        DeclareLaunchArgument(
            'can_interface', default_value='can0',
            description='can0 for the real adapter, vcan0 for a virtual test bus'),
        Node(
            package='cometbot_can',
            executable='can_bridge',
            name='can_bridge',
            output='screen',
            parameters=[config, {'can_interface': LaunchConfiguration('can_interface')}],
            # If the adapter is unplugged the node exits; this restarts it
            # (the ESP32 version rebooted itself instead).
            respawn=True,
            respawn_delay=2.0,
        ),
    ])
