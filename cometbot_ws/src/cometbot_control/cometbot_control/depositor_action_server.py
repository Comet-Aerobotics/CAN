#!/usr/bin/env python3
"""
Depositor action server stub.

This is a simplified placeholder that simulates material deposition.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from cometbot_control.action import Deposit 
from rclpy.action import ActionClient
from rclpy.action.server import ServerGoalHandle;
from std_msgs.msg import String


class DepositorState(Enum):
    IDLE = auto()
    DEPOSITING = auto()
    STOPPED = auto()


class DepositorActionServer(Node):
    """Stub depositor node that simulates material deposit."""

    def __init__(self):
        super().__init__('depositor_action_server')
        # Parameters
        self.declare_parameter('deposit_rate_kg_per_sec', 1.5)
        self.declare_parameter('max_deposit_time_sec', 10.0)
        self.declare_parameter('simulation_mode', True)
  
         # Status publisher (for visualization/debugging)
        self.status_pub = self.create_publisher(String, '/depositor/status', 10)
        self.depositor_action_server_ = ActionServer(
            self, 
            Deposit, 
            "deposit",
             execute_callback=self.execute_callback
             )
         # State
        self.state = DepositorState.IDLE
        self.get_logger().info('Depositor stub initialized (simulation mode)')

      def execute_callback(self, goal_handle: ServerGoalHandle):
        # get request from goal
        material = goal_handle.request.material_to_deposit_kg
        self.get_logger().info("Deposit {material} kg")
        
        #Execute the action
        self.get_logger().info("Executing the goal")

        
        self.deposit_rate = float(self.get_parameter('deposit_rate_kg_per_sec').value)
        self.max_deposit_time = float(self.get_parameter('max_deposit_time_sec').value)

        # Calculate how long it will take to deposit and compare against max time
        current_required_deposit_time = material / self.deposit_rate 

        result = Depositor.Result()

        if current_required_deposit_time > self.max_deposit_time :
            self.get_logger().info("Error: It will take too long to deposit");
            # Change status 
            self.state = DepositorState.STOPPED

            # Final goal state
            goal_handle.abort()

            # send result
            result.success = false
            result.material_deposited_kg = 0.0
        
        else :
            # Changing state to depositing
            self.state = DepositorState.DEPOSITING
            self.get_logger().info("Motor Starting")

        # record current time
        start_time = time.time()
        # Set a target timestamp
        target_time = start_time + current_required_deposit_time

        # Loop until the current time reaches the target time
        while time.time() < target_time:
           
           # Check if goal is canceled
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info("Goal canceled.")
                self.state = DepositorState.STOPPED
                result.success = False
                return result

            
            time.sleep(0.05)

            material_deposited = elapsed_time * deposit_rate

            # Final goal state
            goal_handle.succeed()

             # send result
            
            result.material_deposited_kg = material_deposited
            result.success = true
        
       

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
