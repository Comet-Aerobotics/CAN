#!/usr/bin/env python3
"""
Excavator action server stub.

This is a simplified placeholder that simulates excavator control.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import Float32


class ExcavatorState(Enum):
    IDLE = auto()
    DIGGING = auto()
    STOPPED = auto()


class ExcavatorActionServer(Node):
    """Stub excavator node that simulates excavation."""

    def __init__(self):
        super().__init__('excavator_action_server')

        # Parameters
        self.declare_parameter('dig_rate_kg_per_sec', 1.0)
        self.declare_parameter('bucket_capacity_kg', 5.0)
        self.declare_parameter('simulation_mode', True)

        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.bucket_capacity = float(self.get_parameter('bucket_capacity_kg').value)

        # State
        self.state = ExcavatorState.IDLE
        self._current_weight = 0.0

        # Subscriber to load sensor
        self.weight_sub = self.create_subscription(
            Float32,
            '/load_sensor/weight',
            self.weight_callback,
            10,
        )

        self.get_logger().info('Excavator stub initialized (simulation mode)')

    def weight_callback(self, msg: Float32):
        """Track current bucket weight from load sensor."""
        self._current_weight = msg.data


def main(args=None):
    rclpy.init(args=args)

    # Use MultiThreadedExecutor for better action handling
    executor = MultiThreadedExecutor()
    node = ExcavatorActionServer()
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
