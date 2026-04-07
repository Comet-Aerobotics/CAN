#!/usr/bin/env python3
"""
Cycle test: run an excavate goal then a deposit goal sequentially.
Usage: cycle_test_client.py [dig_duration_sec] [deposit_kg]
"""
import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from cometbot_msgs.action import Excavate, Deposit


class CycleTestClient(Node):
    def __init__(self):
        super().__init__('cycle_test_client')
        self.excavator_client = ActionClient(self, Excavate, 'excavate')
        self.depositor_client = ActionClient(self, Deposit, 'deposit')
        self.done = False

    def run_cycle(self, dig_duration=10, deposit_kg=5.0):
        # Wait for servers
        if not self.excavator_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Excavator action server not available')
            return
        if not self.depositor_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('Depositor action server not available')
            return

        # Send excavate goal
        goal = Excavate.Goal()
        goal.dig_duration_sec = int(dig_duration)
        self.get_logger().info(f'Sending excavate goal: {dig_duration}s')
        send_goal_future = self.excavator_client.send_goal_async(goal, feedback_callback=self.excavator_feedback)
        send_goal_future.add_done_callback(lambda fut: self._excavator_response_cb(fut, deposit_kg))

    def excavator_feedback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'Excavator feedback: laser_tripped={fb.laser_tripped} remaining={fb.estimated_time_remaining}')

    def _excavator_response_cb(self, future, deposit_kg):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Excavate goal rejected')
            self.done = True
            return
        self.get_logger().info('Excavate goal accepted')
        get_result = goal_handle.get_result_async()
        get_result.add_done_callback(lambda fut: self._on_excavate_result(fut, deposit_kg))

    def _on_excavate_result(self, future, deposit_kg):
        result = future.result().result
        self.get_logger().info(f'Excavate result: success={result.success} is_full={result.is_full} time_spent={result.time_spent}')

        # Now send deposit goal
        goal = Deposit.Goal()
        goal.material_to_deposit_kg = float(deposit_kg)
        self.get_logger().info(f'Sending deposit goal: {deposit_kg} kg')
        send_goal_future = self.depositor_client.send_goal_async(goal, feedback_callback=self.depositor_feedback)
        send_goal_future.add_done_callback(self._depositor_response_cb)

    def depositor_feedback(self, feedback_msg):
        fb = feedback_msg.feedback
        self.get_logger().info(f'Depositor feedback: progress={fb.deposit_progress_percentage:.1f}% remaining={fb.estimated_time_remaining}s')

    def _depositor_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Deposit goal rejected')
            self.done = True
            return
        self.get_logger().info('Deposit goal accepted')
        get_result = goal_handle.get_result_async()
        get_result.add_done_callback(self._on_deposit_result)

    def _on_deposit_result(self, future):
        result = future.result().result
        self.get_logger().info(f'Deposit result: success={result.success} deposited={result.material_deposited_kg:.3f}kg')
        self.done = True


def main(argv=None):
    rclpy.init(args=argv)
    node = CycleTestClient()
    try:
        dig = 12
        deposit = 5.0
        if len(sys.argv) > 1:
            try:
                dig = int(sys.argv[1])
            except Exception:
                pass
        if len(sys.argv) > 2:
            try:
                deposit = float(sys.argv[2])
            except Exception:
                pass

        node.run_cycle(dig, deposit)
        while rclpy.ok() and not node.done:
            rclpy.spin_once(node, timeout_sec=1.0)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main(sys.argv)
