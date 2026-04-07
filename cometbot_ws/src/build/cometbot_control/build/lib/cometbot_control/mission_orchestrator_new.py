#!/usr/bin/env python3
import time
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Float32, Bool

class MissionState(Enum):
    STARTUP = auto()
    NAV_TO_MINE = auto()
    EXCAVATE = auto()
    NAV_TO_DEPOSIT = auto()
    DEPOSIT = auto()
    NAV_HOME = auto()
    IDLE = auto()

from dataclasses import dataclass

@dataclass
class ExcavateGoal:
    dig_duration_sec: float = 10.0

class MissionOrchestrator(Node):
    def __init__(self):
        super().__init__('mission_orchestrator')
        self.declare_parameter('target_material_kg', 10.0)
        self.declare_parameter('dig_rate_kg_per_sec', 1.0)
        self.declare_parameter('dig_duration_sec', 10.0)
        self.state = MissionState.STARTUP
        self.total_material_collected = 0.0
        self.current_bucket_weight = 0.0
        self.target = float(self.get_parameter('target_material_kg').value)
        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.dig_duration = float(self.get_parameter('dig_duration_sec').value)
        self.cmd_vel_sub = self.create_subscription(Twist, '/cmd_vel', self.cmd_vel_callback, 10)
        self.weight_sub = self.create_subscription(Float32, '/load_sensor/weight', self.weight_callback, 10)
        self.bucket_full_sub = self.create_subscription(Bool, '/load_sensor/bucket_full', self.bucket_full_callback, 10)
        self.state_pub = self.create_publisher(String, '/fsm/state', 10)
        self.material_pub = self.create_publisher(Float32, '/fsm/material_total', 10)
        self.get_logger().info(f'Mission orchestrator initialized (target={self.target}kg)')
        self.timer = self.create_timer(0.5, self.update)

    def cmd_vel_callback(self, msg): pass
    def weight_callback(self, msg): self.current_bucket_weight = msg.data
    def bucket_full_callback(self, msg): pass

    def update(self):
        if self.state == MissionState.STARTUP:
            self.get_logger().info('Mission started')
            self.state = MissionState.NAV_TO_MINE
        elif self.state == MissionState.NAV_TO_MINE:
            self.get_logger().info('At mine site')
            self.state = MissionState.EXCAVATE
        elif self.state == MissionState.EXCAVATE:
            if self.total_material_collected < self.target:
                collected = min(5.0, self.dig_rate * self.dig_duration)
                self.total_material_collected += collected
                self.get_logger().info(f'Excavated {collected:.2f}kg (total: {self.total_material_collected:.2f}kg)')
                if self.total_material_collected >= self.target:
                    self.state = MissionState.NAV_TO_DEPOSIT
            else:
                self.state = MissionState.NAV_TO_DEPOSIT
        elif self.state == MissionState.NAV_TO_DEPOSIT:
            self.get_logger().info('At deposit site')
            self.state = MissionState.DEPOSIT
        elif self.state == MissionState.DEPOSIT:
            self.get_logger().info(f'Deposited {self.total_material_collected:.2f}kg')
            self.total_material_collected = 0.0
            self.state = MissionState.NAV_HOME
        elif self.state == MissionState.NAV_HOME:
            self.get_logger().info('Returning home')
            self.state = MissionState.IDLE
        
        state_msg = String()
        state_msg.data = self.state.name
        self.state_pub.publish(state_msg)
        material_msg = Float32()
        material_msg.data = self.total_material_collected
        self.material_pub.publish(material_msg)

def main(args=None):
    rclpy.init(args=args)
    executor = MultiThreadedExecutor()
    node = MissionOrchestrator()
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
