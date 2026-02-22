#!/usr/bin/env python3
"""
Load sensor node that publishes material weight/load data.
Simulates a load cell that measures the excavator bucket weight.

Topics:
  Publish: /load_sensor/weight (std_msgs/Float32) - weight in kg
  Publish: /load_sensor/bucket_full (std_msgs/Bool) - whether bucket is full
"""
import time
import math
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, Bool


class LoadSensorNode(Node):
    def __init__(self):
        super().__init__('load_sensor')

        # Parameters
        self.declare_parameter('bucket_capacity_kg', 5.0)
        self.declare_parameter('max_weight_kg', 5.0)
        self.declare_parameter('sensor_noise_sigma', 0.1)
        self.declare_parameter('publish_rate_hz', 10.0)

        self.bucket_capacity = float(self.get_parameter('bucket_capacity_kg').value)
        self.max_weight = float(self.get_parameter('max_weight_kg').value)
        self.sensor_noise = float(self.get_parameter('sensor_noise_sigma').value)
        self.publish_rate = float(self.get_parameter('publish_rate_hz').value)

        # Publishers
        self.weight_pub = self.create_publisher(Float32, '/load_sensor/weight', 10)
        self.bucket_full_pub = self.create_publisher(Bool, '/load_sensor/bucket_full', 10)

        # Internal state
        self._current_weight = 0.0  # kg
        self._time_started = time.monotonic()
        self._bucket_emptied_time = self._time_started

        # Timer for publishing
        self.timer = self.create_timer(1.0 / self.publish_rate, self.publish_callback)

        self.get_logger().info(
            f'LoadSensor initialized (capacity={self.bucket_capacity}kg, noise={self.sensor_noise}kg)'
        )

    def set_weight(self, weight_kg: float):
        """External interface to update the bucket weight (used by excavator/depositor)."""
        self._current_weight = max(0.0, min(weight_kg, self.max_weight))

    def get_weight(self) -> float:
        """Get current bucket weight."""
        return self._current_weight

    def is_bucket_full(self) -> bool:
        """Check if bucket has reached capacity."""
        return self._current_weight >= self.bucket_capacity * 0.95  # 95% threshold

    def empty_bucket(self):
        """Called when depositing material."""
        self._current_weight = 0.0
        self._bucket_emptied_time = time.monotonic()
        self.get_logger().info('Bucket emptied')

    def publish_callback(self):
        """Publish current sensor readings with simulated noise."""
        import numpy as np

        # Add gaussian noise to simulate real sensor
        noise = np.random.normal(0, self.sensor_noise)
        noisy_weight = self._current_weight + noise
        noisy_weight = max(0.0, noisy_weight)

        # Publish weight
        weight_msg = Float32()
        weight_msg.data = noisy_weight
        self.weight_pub.publish(weight_msg)

        # Publish bucket full status
        bucket_full_msg = Bool()
        bucket_full_msg.data = self.is_bucket_full()
        self.bucket_full_pub.publish(bucket_full_msg)


def main(args=None):
    rclpy.init(args=args)
    node = LoadSensorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
