#!/usr/bin/env python3
"""
Excavator action server stub.

This is a simplified placeholder that simulates excavator control.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
from enum import Enum, auto
import asyncio
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.action.server import ServerGoalHandle
from cometbot_control.action import Excavate
from rclpy.action import ActionServer
from std_msgs.msg import Float32, Bool
from custom_messages.msg import RobotStatusMessage


class ExcavatorState(Enum):
    IDLE = auto()
    DIGGING = auto()
    SETTLING = auto()
    STOPPED = auto()


class ExcavatorActionServer(Node):
    """Stub excavator node that simulates excavation."""

    def __init__(self):
        super().__init__('excavator_action_server')
        self._action_server = ActionServer(
            self, 
            Excavate,
            "excavate",
            self.execute_callback

        )

        # Parameters
        self.declare_parameter('bucket_capacity_kg', 5.0)
        self.declare_parameter('simulation_mode', True)
        self.declare_parameter('max_current_limit', 5)

        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.bucket_capacity = float(self.get_parameter('bucket_capacity_kg').value)
        #variables
        self.laser_tripped = False
        self.motor_amps = 0.0
        self.max_limit = float(self.get_parameter('max_current_limit').value)

        # State
        self.state = ExcavatorState.IDLE
        self._current_weight = 0.0

        # Subscriber to laser sensor
        self.laser_sub = self.create_subscription(
            Bool,
            '/laser_sensor/status',
            self.laser_callback,
            10,
        )
        # Subscriber to current sensor
        self.current_sub = self.create_subscription(
            RobotStatusMessage,
            'robot_data',
            self.robot_status_callback,
            10
        )

        #publishers
        self.actuator_voltage = self.create_publisher(Float32, '/hardware/actuator_voltage', 10)
        self.vibrator = self.create_publisher(Bool, '/hardware/vibrator', 10)

        self.get_logger().info('Excavator initialized')
    def robot_status_callback(self, msg):
        # Extract current from the excavator Spark Max message
        self.motor_amps = msg.excavator.current
    def stop_all(self):
        """Emergency stop helper for all moving parts."""
        self.actuator_voltage.publish(Float32(data=0.0))
        self.vibrator.publish(Bool(data=False))
    def laser_callback(self, msg):
        self.laser_tripped = msg.data
    
    def current_callback(self, msg):
        self.motor_amps = msg.data

    

    async def execute_callback(self, goal_handle: ServerGoalHandle):
        result = Excavate.Result()
        feedback = Excavate.Feedback()
        start_time = self.get_clock().now()
        duration = goal_handle.request.dig_duration_sec

        while rclpy.ok():
            if goal_handle.is_cancel_requested:
                self.stop_all()
                goal_handle.canceled()
                result.success = False
                return result
            now = self.get_clock().now()
            elapsed_sec = (now - start_time).nanoseconds / 1e9

            if elapsed_sec >= duration: 
                break

            if self.motor_amps > self.max_limit:
                self.stop_all()
                goal_handle.abort()
                result.success = False
                result.is_full = False
                result.time_spent = elapsed_sec
                return result
            if self.laser_tripped == True:
                self.actuator_voltage.publish(Float32(data=0.0))
                self.vibrator.publish(Bool(data=True))
                await asyncio.sleep(3.0)
                self.vibrator.publish(Bool(data=False))
                await asyncio.sleep(0.5)
                if self.laser_tripped == True:
                    self.stop_all()
                    goal_handle.succeed()
                    result.success = True
                    result.is_full = True
                    result.time_spent = elapsed_sec
                    return result
            else:
                self.actuator_voltage.publish(Float32(data=12.0))
                feedback.laser_tripped = self.laser_tripped
                feedback.estimated_time_remaining = int(max(0, duration - elapsed_sec))
                goal_handle.publish_feedback(feedback)
            await asyncio.sleep(0.1)

            
        self.stop_all()
        goal_handle.succeed()
        result.success = True
        result.is_full = False
        result.time_spent = elapsed_sec
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
        node.stop_all()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
