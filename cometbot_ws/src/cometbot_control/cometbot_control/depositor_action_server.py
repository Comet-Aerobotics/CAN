#!/usr/bin/env python3
"""
Depositor action server stub.

This is a simplified placeholder that simulates material deposition.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
from enum import Enum, auto
import asyncio
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from cometbot_control.action import Deposit 
from rclpy.action import ActionClient
from rclpy.action import ActionServer
from rclpy.action.server import ServerGoalHandle;
from std_msgs.msg import String
from custom_messages.msg import RobotStatusMessage


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

        self.latest_motor_data = None
  
         # Status publisher (for visualization/debugging)
        self.status_pub = self.create_publisher(String, '/depositor/status', 10)
        self.create_subscription(RobotStatusMessage, 'robot_data', self.motor_data_callback, 10)
        self.depositor_action_server_ = ActionServer(
            self, 
            Deposit, 
            "deposit",
             execute_callback=self.execute_callback
             )
         # State
        self.state = DepositorState.IDLE
        self.get_logger().info('Depositor stub initialized (simulation mode)')
        
    def motor_data_callback(self, msg):
        self.latest_motor_data = msg

    def stop_motor(self):
        msg = String()
        msg.data = "POWER:0.00"
        self.status_pub.publish(msg)

    async def execute_callback(self, goal_handle: ServerGoalHandle):
        
        if self.latest_motor_data is None:
            self.get_logger().error("No motor data from ESP32. Aborting.")
            goal_handle.abort()
            return Deposit.Result(success=False)

        material_goal = goal_handle.request.material_to_deposit_kg
        self.get_logger().info(f"Goal: Deposit {material_goal} kg")
        
        result = Deposit.Result()
        feedback_msg = Deposit.Feedback()
        
        current_power = 0.05
        total_mass_deposited = 0.0
        motion_detected = False
        
        # Constants
        RAMP_INCREMENT = 0.02
        VELOCITY_THRESHOLD = 0.1
        MASS_MAGIC_NUMBER = 0.125 

        # Execution Loop
        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.stop_motor()
                goal_handle.canceled()
                return result

            # Pull sensor data
            motor_vel = self.latest_motor_data.depositor_motor.velocity
            motor_current = self.latest_motor_data.depositor_motor.current

            # Ramping
            if not motion_detected:
                if abs(motor_vel) > VELOCITY_THRESHOLD:
                    motion_detected = True
                    self.get_logger().info(f"Motion detected at {current_power:.2f} power")
                else:
                    current_power += RAMP_INCREMENT
                    if current_power > 1.0: current_power = 1.0
            
            # Mass Calculation
            if motion_detected:
                # 10Hz loop means dt = 0.1
                total_mass_deposited += (current_power * motor_current * MASS_MAGIC_NUMBER * 0.1)

            # Publish message with power
            cmd_msg = String()
            cmd_msg.data = f"POWER:{current_power:.2f}"
            self.status_pub.publish(cmd_msg)

            # Feedback
            feedback_msg.current_progress_kg = total_mass_deposited
            goal_handle.publish_feedback(feedback_msg)

            if total_mass_deposited >= material_goal:
                break
                
            await asyncio.sleep(0.1)

        self.stop_motor()
        goal_handle.succeed()
        result.success = True
        result.material_deposited_kg = total_mass_deposited
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
