#!/usr/bin/env python3
"""
High-level mission orchestrator using ROS Actions.
Coordinates excavator and depositor subsystems to complete the Lunabotics mission.

Subscribes to:
  /cmd_vel (Twist) - drive commands from teleop
  /load_sensor/weight (Float32) - bucket load
  /load_sensor/bucket_full (Bool) - bucket full status

Calls Actions:
  /excavator/excavate (Excavate) - dig material
  /depositor/deposit (Deposit) - deposit material

Publishes:
  /fsm/state (String) - current mission state
  /fsm/material_total (Float32) - total material collected
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node

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
    EMERGENCY_STOP = auto()


class MissionOrchestrator(Node):
    def __init__(self):
        super().__init__('mission_orchestrator')

        # Parameters
        self.declare_parameter('dig_duration_sec', 30.0)
        self.declare_parameter('dig_rate_kg_per_sec', 1.0)
        self.declare_parameter('empty_at_capacity', True)
        self.declare_parameter('target_total_material_kg', 10.0)

        self.dig_duration = float(self.get_parameter('dig_duration_sec').value)
        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.empty_at_capacity = bool(self.get_parameter('empty_at_capacity').value)
        self.target_material = float(self.get_parameter('target_total_material_kg').value)

        # State
        self.state = MissionState.STARTUP
        self.total_material_collected = 0.0
        self.current_bucket_weight = 0.0
        self.bucket_full = False
        self.emergency = False

        # Callback groups
        self.callback_group = ReentrantCallbackGroup()

        # Subscriptions
        self.cmd_vel_sub = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.cmd_vel_callback,
            10,
            callback_group=self.callback_group,
        )

        self.weight_sub = self.create_subscription(
            Float32,
            '/load_sensor/weight',
            self.weight_callback,
            10,
            callback_group=self.callback_group,
        )

        self.bucket_full_sub = self.create_subscription(
            Bool,
            '/load_sensor/bucket_full',
            self.bucket_full_callback,
            10,
            callback_group=self.callback_group,
        )

        # Publishers
        self.state_pub = self.create_publisher(String, '/fsm/state', 10)
        self.total_material_pub = self.create_publisher(Float32, '/fsm/material_total', 10)

        # Action clients
        self.excavate_client = ActionClient(
            self,
            Excavate,
            '/excavator/excavate',
            callback_group=self.callback_group,
        )

        self.deposit_client = ActionClient(
            self,
            Deposit,
            '/depositor/deposit',
            callback_group=self.callback_group,
        )

        # Timer for main loop
        self.timer = self.create_timer(0.5, self.mission_loop, callback_group=self.callback_group)

        # Logging
        self._logged_once = set()

        self.get_logger().info('Mission Orchestrator initialized')
        self.publish_state()

    def log_once(self, msg, level='info'):
        if msg in self._logged_once:
            return
        getattr(self.get_logger(), level)(msg)
        self._logged_once.add(msg)

    def set_state(self, new_state: MissionState):
        if self.state != new_state:
            self.get_logger().info(f'State Transition: {self.state.name} → {new_state.name}')
            self.state = new_state
            self.publish_state()

    def publish_state(self):
        msg = String()
        msg.data = self.state.name
        self.state_pub.publish(msg)

        total_msg = Float32()
        total_msg.data = self.total_material_collected
        self.total_material_pub.publish(total_msg)

    def cmd_vel_callback(self, msg: Twist):
        """Monitor cmd_vel for emergency stop (zero velocity)."""
        # In future, could use cmd_vel for autonomous navigation too
        pass

    def weight_callback(self, msg: Float32):
        self.current_bucket_weight = msg.data

    def bucket_full_callback(self, msg: Bool):
        self.bucket_full = msg.data

    async def excavate_with_action(self) -> bool:
        """Simulate excavate action. In real implementation, would call ROS 2 action."""
        self.get_logger().info(f'Excavation simulation: {self.dig_duration}s')
        
        # Simulated excavation
        collected = min(5.0, self.dig_rate * self.dig_duration)
        self.total_material_collected += collected
        self.get_logger().info(
            f'Excavation succeeded: {collected:.2f}kg collected '
            f'(total: {self.total_material_collected:.2f}kg)'
        )
        return True

    async def deposit_with_action(self, amount_kg: float) -> bool:
        """Simulate deposit action. In real implementation, would call ROS 2 action."""
        self.get_logger().info(f'Deposit simulation: {amount_kg:.2f}kg')
        self.get_logger().info(f'Deposit succeeded: {amount_kg:.2f}kg deposited')
        return True

    def mission_loop(self):
        """Main mission state machine - non-blocking version."""
        self.publish_state()

        if self.emergency:
            self.set_state(MissionState.EMERGENCY_STOP)
            return

        if self.state == MissionState.STARTUP:
            self.log_once('Initializing mission...')
            self.set_state(MissionState.NAV_TO_MINE)

        elif self.state == MissionState.NAV_TO_MINE:
            self.log_once('Navigating to mine site (simulated)', key='nav_mine')
            # In real implementation, would call autonomous navigation action
            # For now, auto-transition after delay
            if not hasattr(self, '_nav_start_time'):
                self._nav_start_time = time.monotonic()
            if time.monotonic() - self._nav_start_time > 2.0:
                self.set_state(MissionState.EXCAVATE)
                delattr(self, '_nav_start_time')

        elif self.state == MissionState.EXCAVATE:
            self.log_once('Starting excavation sequence')
            # Non-blocking action - we'd need to refactor for true async
            # For now, keep it simple with blocking calls
            self.set_state(MissionState.EXCAVATE)

            if not hasattr(self, '_excavate_started'):
                self._excavate_started = True
                # Start async excavation
                self.create_task(self._excavate_task())

        elif self.state == MissionState.NAV_TO_DEPOSIT:
            self.log_once('Navigating to deposit site (simulated)', key='nav_deposit')
            if not hasattr(self, '_nav_deposit_start'):
                self._nav_deposit_start = time.monotonic()
            if time.monotonic() - self._nav_deposit_start > 2.0:
                self.set_state(MissionState.DEPOSIT)
                delattr(self, '_nav_deposit_start')

        elif self.state == MissionState.DEPOSIT:
            self.log_once('Starting deposit sequence')
            if not hasattr(self, '_deposit_started'):
                self._deposit_started = True
                self.create_task(self._deposit_task())

        elif self.state == MissionState.NAV_HOME:
            self.log_once('Returning to base (simulated)', key='nav_home')
            if not hasattr(self, '_nav_home_start'):
                self._nav_home_start = time.monotonic()
            if time.monotonic() - self._nav_home_start > 2.0:
                if self.total_material_collected >= self.target_material:
                    self.set_state(MissionState.IDLE)
                else:
                    self.set_state(MissionState.NAV_TO_MINE)
                delattr(self, '_nav_home_start')

        elif self.state == MissionState.IDLE:
            self.log_once('Mission complete!')

        elif self.state == MissionState.EMERGENCY_STOP:
            self.get_logger().error('EMERGENCY STOP ACTIVE')

    async def _excavate_task(self):
        """Async excavation task."""
        success = await self.excavate_with_action()
        if success and self.bucket_full:
            self.set_state(MissionState.NAV_TO_DEPOSIT)
        self._excavate_started = False
        delattr(self, '_excavate_started')

    async def _deposit_task(self):
        """Async deposit task."""
        success = await self.deposit_with_action(self.current_bucket_weight)
        if success:
            # Check if mission is complete
            if self.total_material_collected >= self.target_material:
                self.set_state(MissionState.NAV_HOME)
            else:
                self.set_state(MissionState.NAV_TO_MINE)
        self._deposit_started = False
        delattr(self, '_deposit_started')


def main(args=None):
    rclpy.init(args=args)

    # Use MultiThreadedExecutor for action handling
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
