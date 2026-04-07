#!/usr/bin/env python3
"""
Launch file for action-based mission orchestration system.
Starts all required nodes for testing the mission in simulation.

Usage:
  ros2 launch cometbot_control mission_sim.launch.py
  
With custom parameters:
  ros2 launch cometbot_control mission_sim.launch.py \
    dig_rate:=10.0 \
    target_material:=2.0
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare arguments
    dig_rate_arg = DeclareLaunchArgument(
        'dig_rate',
        default_value='1.0',
        description='Excavation rate in kg/s'
    )
    deposit_rate_arg = DeclareLaunchArgument(
        'deposit_rate',
        default_value='1.5',
        description='Deposit rate in kg/s'
    )
    dig_duration_arg = DeclareLaunchArgument(
        'dig_duration',
        default_value='30.0',
        description='How long to excavate (seconds)'
    )
    target_material_arg = DeclareLaunchArgument(
        'target_material',
        default_value='10.0',
        description='Target material to collect (kg)'
    )

    # Create nodes
    load_sensor_node = Node(
        package='cometbot_control',
        executable='load_sensor',
        name='load_sensor',
        output='screen',
        parameters=[
            {'bucket_capacity_kg': 5.0},
            {'sensor_noise_sigma': 0.1},
            {'publish_rate_hz': 10.0},
        ],
    )

    excavator_server_node = Node(
        package='cometbot_control',
        executable='excavator_action_server',
        name='excavator_action_server',
        output='screen',
        parameters=[
            {'dig_rate_kg_per_sec': LaunchConfiguration('dig_rate')},
            {'bucket_capacity_kg': 5.0},
            {'simulation_mode': True},
        ],
    )

    depositor_server_node = Node(
        package='cometbot_control',
        executable='depositor_action_server',
        name='depositor_action_server',
        output='screen',
        parameters=[
            {'deposit_rate_kg_per_sec': LaunchConfiguration('deposit_rate')},
            {'max_deposit_time_sec': 10.0},
            {'simulation_mode': True},
        ],
    )

    mission_orchestrator_node = Node(
        package='cometbot_control',
        executable='mission_orchestrator',
        name='mission_orchestrator',
        output='screen',
        parameters=[
            {'dig_duration_sec': LaunchConfiguration('dig_duration')},
            {'empty_at_capacity': True},
            {'target_total_material_kg': LaunchConfiguration('target_material')},
        ],
    )

    return LaunchDescription([
        dig_rate_arg,
        deposit_rate_arg,
        dig_duration_arg,
        target_material_arg,
        load_sensor_node,
        excavator_server_node,
        depositor_server_node,
        mission_orchestrator_node,
    ])
