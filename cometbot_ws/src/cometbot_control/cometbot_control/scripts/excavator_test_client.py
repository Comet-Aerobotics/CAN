#!/usr/bin/env python3
"""
Simple action client to test the `excavate` action server.
Usage: excavator_test_client.py [duration_sec]
"""
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from cometbot_msgs.action import Excavate


class ExcavatorTestClient(Node):
    def __init__(self):
        super().__init__('excavator_test_client')
        self._client = ActionClient(self, Excavate, 'excavate')
        self._done = False

    def send_goal(self, duration_sec: int = 8):
        if not self._client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Action server not available')
            self._done = True
            return
        goal = Excavate.Goal()
        goal.dig_duration_sec = int(duration_sec)
        send_goal_future = self._client.send_goal_async(goal, feedback_callback=self._feedback_cb)
        send_goal_future.add_done_callback(self._goal_response_cb)

    def _goal_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            self._done = True
            return
        self.get_logger().info('Goal accepted')
        get_result_future = goal_handle.get_result_async()
        get_result_future.add_done_callback(self._get_result_cb)

    def _feedback_cb(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'Feedback: laser_tripped={fb.laser_tripped} remaining={fb.estimated_time_remaining}')

    def _get_result_cb(self, future):
        result = future.result().result
        self.get_logger().info(f'Result: success={result.success} is_full={result.is_full} time_spent={result.time_spent}')
        self._done = True


def main(argv=None):
    rclpy.init(args=argv)
    node = ExcavatorTestClient()
    try:
        duration = 8
        if len(sys.argv) > 1:
            try:
                duration = int(sys.argv[1])
            except Exception:
                pass
        node.send_goal(duration)
        while rclpy.ok() and not node._done:
            rclpy.spin_once(node, timeout_sec=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main(sys.argv)
