#!/usr/bin/env python3
"""
Depositor action server stub.

Simulates material deposition without requiring hardware.
"""
import time
import threading
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from cometbot_msgs.action import Deposit
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle
from std_msgs.msg import Float32
from cometbot_msgs.msg import RobotStatusMessage


def _extract_currents(msg):
    """Return (excavator_current, depositor_current) from different message shapes."""
    exc = None
    dep = None
    if hasattr(msg, 'excavator_current'):
        try:
            exc = float(msg.excavator_current)
        except Exception:
            exc = None
    if hasattr(msg, 'depositor_current'):
        try:
            dep = float(msg.depositor_current)
        except Exception:
            dep = None

    if exc is None:
        for name in ('excavator', 'left_drivebase'):
            nested = getattr(msg, name, None)
            if nested is not None and hasattr(nested, 'current'):
                try:
                    exc = float(nested.current)
                    break
                except Exception:
                    pass
    if dep is None:
        for name in ('depositor', 'right_drivebase'):
            nested = getattr(msg, name, None)
            if nested is not None and hasattr(nested, 'current'):
                try:
                    dep = float(nested.current)
                    break
                except Exception:
                    pass
    return exc, dep


class DepositorState(Enum):
    IDLE = auto()
    DEPOSITING = auto()
    STOPPED = auto()


class DepositorActionServer(Node):
    def __init__(self):
        super().__init__('depositor_action_server')
        # Parameters
        self.declare_parameter('deposit_rate_kg_per_sec', 1.5)
        self.declare_parameter('max_deposit_time_sec', 30.0)
        self.declare_parameter('simulation_mode', True)

        self.deposit_rate = float(self.get_parameter('deposit_rate_kg_per_sec').value)
        self.max_time = float(self.get_parameter('max_deposit_time_sec').value)

        # Publishers / subscriptions
        self.motor_command_pub = self.create_publisher(Float32, '/depositor/status', 10)
        self.create_subscription(RobotStatusMessage, 'robot_data', self.robot_data_callback, 10)

        self._action_server = ActionServer(
            self,
            Deposit,
            'deposit',
            execute_callback=self.execute_callback,
        )

        self.latest_motor_data = None
        self._latest_excavator_current = None
        self._latest_depositor_current = None
        self.state = DepositorState.IDLE
        self.get_logger().info('Depositor initialized')

    def robot_data_callback(self, msg: RobotStatusMessage):
        # store original message and parsed current values (supports multiple message shapes)
        self.latest_motor_data = msg
        exc, dep = _extract_currents(msg)
        if exc is not None:
            self._latest_excavator_current = exc
        if dep is not None:
            self._latest_depositor_current = dep

    def stop_motor(self):
        cmd = Float32()
        cmd.data = 0.0
        self.motor_command_pub.publish(cmd)

    def execute_callback(self, goal_handle: ServerGoalHandle):
        result = Deposit.Result()
        feedback = Deposit.Feedback()

        material_goal = float(goal_handle.request.material_to_deposit_kg)
        self.get_logger().info(f'Executing deposit: target {material_goal:.3f} kg')

        start_time = self.get_clock().now()
        total_deposited = 0.0
        time_step = 0.1

        done = threading.Event()

        def timer_cb():
            nonlocal total_deposited
            if not rclpy.ok():
                done.set()
                return

            if goal_handle.is_cancel_requested:
                self.stop_motor()
                goal_handle.canceled()
                result.success = False
                result.material_deposited_kg = float(total_deposited)
                done.set()
                return

            elapsed = (self.get_clock().now() - start_time).nanoseconds / 1e9
            if elapsed > self.max_time:
                self.get_logger().warning('Exceeded max deposit time; aborting')
                done.set()
                return

            deposit_amount = self.deposit_rate * time_step
            total_deposited += deposit_amount

            # Publish a simulated motor command (0..1)
            cmd = Float32()
            cmd.data = float(min(1.0, total_deposited / material_goal)) if material_goal > 0 else 0.0
            self.motor_command_pub.publish(cmd)

            # Feedback
            progress = min(100.0, (total_deposited / material_goal) * 100.0) if material_goal > 0 else 100.0
            feedback.deposit_progress_percentage = float(progress)
            remaining = max(0.0, (material_goal - total_deposited) / self.deposit_rate) if self.deposit_rate > 0 else 0.0
            feedback.estimated_time_remaining = int(remaining)
            goal_handle.publish_feedback(feedback)

            if total_deposited >= material_goal:
                done.set()

        timer = self.create_timer(time_step, timer_cb)
        done.wait()
        try:
            self.destroy_timer(timer)
        except Exception:
            pass

        self.stop_motor()
        goal_handle.succeed()
        result.success = True
        result.material_deposited_kg = float(total_deposited)
        return result


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
