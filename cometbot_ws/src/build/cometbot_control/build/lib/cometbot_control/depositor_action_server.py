#!/usr/bin/env python3
"""
Depositor action server stub.

This is a simplified placeholder that simulates material deposition.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor

from std_msgs.msg import String


class DepositorState(Enum):
    IDLE = auto()
    DEPOSITING = auto()
    STOPPED = auto()


class DepositorActionServer(Node):
    """Stub depositor node that simulates material deposit."""

    def __init__(self):
        super().__init__('depositor_action_server')

        # Parameters
        self.declare_parameter('deposit_rate_kg_per_sec', 1.5)
        self.declare_parameter('max_deposit_time_sec', 10.0)
        self.declare_parameter('simulation_mode', True)

        self.deposit_rate = float(self.get_parameter('deposit_rate_kg_per_sec').value)
        self.max_deposit_time = float(self.get_parameter('max_deposit_time_sec').value)

        # State
        self.state = DepositorState.IDLE

        # Status publisher (for visualization/debugging)
        self.status_pub = self.create_publisher(String, '/depositor/status', 10)

        self.get_logger().info('Depositor stub initialized (simulation mode)')

def main(args=None):
    rclpy.init(args=args)

    executor = MultiThreadedExecutor()
    node = DepositorActionServer()
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
