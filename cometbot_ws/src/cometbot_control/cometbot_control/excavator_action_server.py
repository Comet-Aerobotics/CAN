#!/usr/bin/env python3
"""
Excavator action server stub.

NOTE: This is a placeholder implementation without ROS 2 ActionServer.
For full ROS 2 integration, use action_types dataclasses with proper
ROS 2 ActionServer implementation.

This demonstrates the data structures and logic flow for excavator operations.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32
from cometbot_control.action_types import ExcavateGoal, ExcavateResult, ExcavateFeedback


class ExcavatorState(Enum):
    IDLE = auto()
    DIGGING = auto()
    STOPPED = auto()


class ExcavatorActionServer(Node):
    def __init__(self):
        super().__init__('excavator_action_server')

        # Parameters
        self.declare_parameter('dig_rate_kg_per_sec', 1.0)
        self.declare_parameter('bucket_capacity_kg', 5.0)
        self.declare_parameter('simulation_mode', True)

        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.bucket_capacity = float(self.get_parameter('bucket_capacity_kg').value)
        self.simulation_mode = bool(self.get_parameter('simulation_mode').value)

        # State
        self.state = ExcavatorState.IDLE
        self._current_weight = 0.0

        # Callback group for thread-safe action handling
        self.callback_group = ReentrantCallbackGroup()

        # Action server
        self.action_server = ActionServer(
            self,
            Excavate,
            '/excavator/excavate',
            execute_callback=self.execute_excavate_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group,
        )

        # Subscriber to load sensor
        self.weight_sub = self.create_subscription(
            Float32,
            '/load_sensor/weight',
            self.weight_callback,
            10,
            callback_group=self.callback_group,
        )

        self.get_logger().info('Excavator action server initialized')

    def weight_callback(self, msg: Float32):
        """Track current bucket weight from load sensor."""
        self._current_weight = msg.data

    def goal_callback(self, goal_request):
        """Handle incoming excavation goal."""
        self.get_logger().info(
            f'Received excavation goal: dig_duration={goal_request.dig_duration_sec}s'
        )
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        """Handle excavation cancellation."""
        self.get_logger().info('Excavation cancelled')
        return CancelResponse.ACCEPT

    def execute_excavate_callback(self, goal_handle):
        """Execute excavation action."""
        self.get_logger().info('Starting excavation action')
        self.state = ExcavatorState.DIGGING

        goal = goal_handle.request
        dig_duration = goal.dig_duration_sec
        start_time = time.monotonic()
        material_collected = 0.0

        feedback = Excavate.Feedback()

        try:
            while self.state == ExcavatorState.DIGGING:
                elapsed = time.monotonic() - start_time

                # Check if goal is cancelled
                if goal_handle.is_cancel_requested():
                    self.get_logger().info('Excavation cancelled during execution')
                    self.state = ExcavatorState.STOPPED
                    goal_handle.canceled()
                    return Excavate.Result(material_collected_kg=material_collected, success=False)

                # Simulate material collection
                if elapsed < dig_duration:
                    # Collect material at specified rate (sigmoid curve for realism)
                    collection_rate = self.dig_rate * (1.0 - (self._current_weight / self.bucket_capacity))
                    material_collected = min(
                        self.bucket_capacity,
                        self.dig_rate * elapsed,
                    )

                    # Publish feedback
                    bucket_fill_pct = (self._current_weight / self.bucket_capacity) * 100.0
                    time_remaining = max(0, dig_duration - elapsed)

                    feedback.bucket_fill_percentage = bucket_fill_pct
                    feedback.estimated_time_remaining = int(time_remaining)
                    goal_handle.publish_feedback(feedback)

                    self.get_logger().info(
                        f'Excavating... {bucket_fill_pct:.1f}% full, {time_remaining:.1f}s remaining'
                    )

                    # If bucket is full, stop early
                    if self._current_weight >= self.bucket_capacity * 0.95:
                        self.get_logger().info('Bucket full! Stopping excavation')
                        material_collected = self._current_weight
                        break

                    time.sleep(0.1)  # Update frequency
                else:
                    # Dig time complete
                    material_collected = self._current_weight
                    self.get_logger().info(f'Excavation complete. Collected {material_collected:.2f}kg')
                    break

        except Exception as e:
            self.get_logger().error(f'Error during excavation: {e}')
            self.state = ExcavatorState.STOPPED
            goal_handle.abort()
            return Excavate.Result(material_collected_kg=0.0, success=False)

        # Set result
        result = Excavate.Result()
        result.material_collected_kg = material_collected
        result.success = True

        self.state = ExcavatorState.IDLE
        goal_handle.succeed()

        return result


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
