#!/usr/bin/env python3
"""
Example showing how to use the action servers programmatically.
Useful for integration testing and debugging.

Run with:
  python3 action_client_example.py
  
Requires: excavator_action_server and depositor_action_server running
"""

import asyncio
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor

from cometbot_control.action import Excavate, Deposit


class ActionClientExample(Node):
    def __init__(self):
        super().__init__('action_client_example')
        
        self.excavate_client = ActionClient(self, Excavate, '/excavator/excavate')
        self.deposit_client = ActionClient(self, Deposit, '/depositor/deposit')

    async def send_excavate_goal(self):
        """Send a simple excavate goal."""
        print("\n=== Testing Excavate Action ===")
        
        # Wait for server
        if not self.excavate_client.wait_for_server(timeout_sec=3.0):
            print("Excavator action server not available!")
            return False
        
        # Create goal
        goal_msg = Excavate.Goal()
        goal_msg.dig_duration_sec = 10.0  # Short test dig
        
        print(f"Sending excavate goal: dig_duration={goal_msg.dig_duration_sec}s")
        
        # Send and wait for result
        send_goal_future = self.excavate_client.send_goal_async(
            goal_msg,
            feedback_callback=self.excavate_feedback_callback
        )
        
        goal_handle = await send_goal_future
        if not goal_handle.accepted:
            print("Goal rejected!")
            return False
        
        print("Goal accepted! Waiting for result...")
        result_future = goal_handle.get_result_async()
        result = await result_future
        
        if result.success:
            print(f"✓ Excavation succeeded: {result.material_collected_kg:.2f}kg collected")
        else:
            print("✗ Excavation failed")
        
        return result.success

    def excavate_feedback_callback(self, feedback_msg):
        """Called when excavator publishes feedback."""
        feedback = feedback_msg.feedback
        print(f"  Feedback: {feedback.bucket_fill_percentage:.1f}% full, "
              f"{feedback.estimated_time_remaining}s remaining")

    async def send_deposit_goal(self):
        """Send a simple deposit goal."""
        print("\n=== Testing Deposit Action ===")
        
        # Wait for server
        if not self.deposit_client.wait_for_server(timeout_sec=3.0):
            print("Depositor action server not available!")
            return False
        
        # Create goal
        goal_msg = Deposit.Goal()
        goal_msg.material_to_deposit_kg = 5.0
        
        print(f"Sending deposit goal: material_to_deposit={goal_msg.material_to_deposit_kg:.2f}kg")
        
        # Send and wait for result
        send_goal_future = self.deposit_client.send_goal_async(
            goal_msg,
            feedback_callback=self.deposit_feedback_callback
        )
        
        goal_handle = await send_goal_future
        if not goal_handle.accepted:
            print("Goal rejected!")
            return False
        
        print("Goal accepted! Waiting for result...")
        result_future = goal_handle.get_result_async()
        result = await result_future
        
        if result.success:
            print(f"✓ Deposit succeeded: {result.material_deposited_kg:.2f}kg deposited")
        else:
            print("✗ Deposit failed")
        
        return result.success

    def deposit_feedback_callback(self, feedback_msg):
        """Called when depositor publishes feedback."""
        feedback = feedback_msg.feedback
        print(f"  Feedback: {feedback.deposit_progress_percentage:.1f}% complete, "
              f"{feedback.estimated_time_remaining}s remaining")

    async def run_example_sequence(self):
        """Run a simple example sequence."""
        print("\n" + "=" * 50)
        print("ACTION CLIENT EXAMPLE")
        print("=" * 50)
        
        # Test single dig
        result = await self.send_excavate_goal()
        if not result:
            print("Failed to excavate, stopping")
            return
        
        # Test deposit
        result = await self.send_deposit_goal()
        if not result:
            print("Failed to deposit, stopping")
            return
        
        print("\n" + "=" * 50)
        print("✓ Example completed successfully!")
        print("=" * 50)


async def main(args=None):
    rclpy.init(args=args)
    
    # Create node
    node = ActionClientExample()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    
    # Run example in background
    example_task = asyncio.create_task(node.run_example_sequence())
    
    # Spin executor
    while not example_task.done():
        executor.spin_once(timeout_sec=0.1)
    
    # Cleanup
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
