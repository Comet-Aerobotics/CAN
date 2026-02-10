#!/usr/bin/env python3
"""
Depositor action server stub.

NOTE: This is a placeholder implementation without ROS 2 ActionServer.
For full ROS 2 integration, use action_types dataclasses with proper
ROS 2 ActionServer implementation.

This demonstrates the data structures and logic flow for deposition operations.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from cometbot_control.action_types import DepositGoal, DepositResult, DepositFeedback


class DepositorState(Enum):
    IDLE = auto()
    DEPOSITING = auto()
    STOPPED = auto()


class DepositorActionServer(Node):
    def __init__(self):
        super().__init__('depositor_action_server')

        # Parameters
        self.declare_parameter('deposit_rate_kg_per_sec', 1.5)
        self.declare_parameter('max_deposit_time_sec', 10.0)
        self.declare_parameter('simulation_mode', True)

        self.deposit_rate = float(self.get_parameter('deposit_rate_kg_per_sec').value)
        self.max_deposit_time = float(self.get_parameter('max_deposit_time_sec').value)
        self.simulation_mode = bool(self.get_parameter('simulation_mode').value)

        # State
        self.state = DepositorState.IDLE

        # Callback group for thread-safe action handling
        self.callback_group = ReentrantCallbackGroup()

        # Action server
        self.action_server = ActionServer(
            self,
            Deposit,
            '/depositor/deposit',
            execute_callback=self.execute_deposit_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )

        # Status publisher (for visualization/debugging)
        self.status_pub = self.create_publisher(String, '/depositor/status', 10)

        self.get_logger().info('Depositor action server initialized')

    def goal_callback(self, goal_request):
        """Handle incoming deposit goal."""
        self.get_logger().info(
            f'Received deposit goal: material_to_deposit={goal_request.material_to_deposit_kg}kg'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Handle deposit cancellation."""
        self.get_logger().info('Deposit cancelled')
        return CancelResponse.ACCEPT

    def execute_deposit_callback(self, goal_handle):
        """Execute deposit action."""
        self.get_logger().info('Starting deposit action')
        self.state = DepositorState.DEPOSITING

        goal = goal_handle.request
        target_amount = goal.material_to_deposit_kg
        start_time = time.monotonic()
        material_deposited = 0.0

        feedback = Deposit.Feedback()

        try:
            while self.state == DepositorState.DEPOSITING:
                elapsed = time.monotonic() - start_time

                # Check if goal is cancelled
                if goal_handle.is_cancel_requested():
                    self.get_logger().info('Deposit cancelled during execution')
                    self.state = DepositorState.STOPPED
                    goal_handle.canceled()
                    return Deposit.Result(
                        material_deposited_kg=material_deposited, success=False
                    )

                # Simulate material deposition
                material_deposited = min(target_amount, self.deposit_rate * elapsed)

                # Calculate time to complete
                if self.deposit_rate > 0:
                    time_to_complete = (target_amount - material_deposited) / self.deposit_rate
                else:
                    time_to_complete = 0

                # Check if deposit exceeds maximum time
                if elapsed > self.max_deposit_time:
                    self.get_logger().warn('Deposit exceeded maximum time limit')
                    self.state = DepositorState.STOPPED
                    goal_handle.abort()
                    return Deposit.Result(
                        material_deposited_kg=material_deposited, success=False
                    )

                # Publish feedback
                if target_amount > 0:
                    progress_pct = (material_deposited / target_amount) * 100.0
                else:
                    progress_pct = 0.0

                feedback.deposit_progress_percentage = progress_pct
                feedback.estimated_time_remaining = max(0, int(time_to_complete))
                goal_handle.publish_feedback(feedback)

                status_msg = String()
                status_msg.data = f'Depositing... {progress_pct:.1f}% complete ({material_deposited:.2f}kg/{target_amount:.2f}kg)'
                self.status_pub.publish(status_msg)

                self.get_logger().info(
                    f'Depositing... {progress_pct:.1f}%, {time_to_complete:.1f}s remaining'
                )

                # Check if deposit is complete
                if material_deposited >= target_amount:
                    self.get_logger().info(
                        f'Deposit complete. Deposited {material_deposited:.2f}kg'
                    )
                    break

                time.sleep(0.1)  # Update frequency

        except Exception as e:
            self.get_logger().error(f'Error during deposit: {e}')
            self.state = DepositorState.STOPPED
            goal_handle.abort()
            return Deposit.Result(material_deposited_kg=0.0, success=False)

        # Set result
        result = Deposit.Result()
        result.material_deposited_kg = material_deposited
        result.success = True

        self.state = DepositorState.IDLE
        goal_handle.succeed()

        return result


def main(args=None):
    rclpy.init(args=args)

    # Use MultiThreadedExecutor for better action handling
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
