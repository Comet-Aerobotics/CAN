#!/usr/bin/env python3
"""
Simple mock hardware simulator for testing the excavator action server.
Publishes `/laser_sensor/status` and `robot_data`, and listens to actuator commands.
"""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, Float32
from cometbot_msgs.msg import RobotStatusMessage


class MockHardware(Node):
    def __init__(self):
        super().__init__('mock_hardware')
        self.laser_pub = self.create_publisher(Bool, '/laser_sensor/status', 10)
        self.robot_pub = self.create_publisher(RobotStatusMessage, 'robot_data', 10)
        self.voltage_sub = self.create_subscription(Float32, '/hardware/actuator_voltage', self.voltage_cb, 10)
        
        self.current = 0.0
        self.timer = self.create_timer(0.2, self.timer_cb)
        self.get_logger().info('MockHardware started')

    def voltage_cb(self, msg: Float32):
        # increase current when actuator is powered, otherwise decay
        if msg.data > 1.0:
            # simulate current draw ramp-up
            self.current = min(10.0, self.current + 0.6)
        else:
            # decay toward zero
            self.current = max(0.0, self.current - 0.8)


    def timer_cb(self):
        # publish laser tripped when current is high (simulates bucket full or obstacle)
        laser = Bool()
        laser.data = self.current > 3.0
        self.laser_pub.publish(laser)

        rmsg = RobotStatusMessage()
        rmsg.enabled = True
        rmsg.excavator_current = float(self.current)
        rmsg.depositor_current = 0.0
        self.robot_pub.publish(rmsg)


def main():
    rclpy.init()
    node = MockHardware()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
