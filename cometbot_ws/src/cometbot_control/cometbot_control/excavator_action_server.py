#!/usr/bin/env python3
"""
Excavator action server stub.

This is a simplified placeholder that simulates excavator control.
For actual hardware integration, replace with proper ROS 2 ActionServer.
"""
import time
import threading
from enum import Enum, auto
import rclpy
from rclpy.node import Node
from rclpy.executors import MultiThreadedExecutor
from rclpy.action.server import ServerGoalHandle
from cometbot_msgs.action import Excavate
from rclpy.action import ActionServer
from std_msgs.msg import Float32, Bool
from cometbot_msgs.msg import RobotStatusMessage


def _extract_currents(msg):
    """Return (excavator_current, depositor_current) if available from different message shapes.

    Supports common variants:
    - cometbot_msgs/RobotStatusMessage: flat `excavator_current`, `depositor_current`
    - custom_messages/RobotStatusMessage: nested `excavator`/`depositor` or
      `left_drivebase`/`right_drivebase` with `.current` field
    """
    exc = None
    dep = None
    # flat fields
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

    # nested fields fallback
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
        self.declare_parameter('dig_rate_kg_per_sec', 1.0)

        self.dig_rate = float(self.get_parameter('dig_rate_kg_per_sec').value)
        self.bucket_capacity = float(self.get_parameter('bucket_capacity_kg').value)
        #variables
        self.laser_tripped = False
        self.motor_amps = 0.0
        self.max_limit = float(self.get_parameter('max_current_limit').value)

        # State
        self.state = ExcavatorState.IDLE
        self._current_weight = 0.0
        self._latest_excavator_current = None
        self._latest_depositor_current = None

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
        

        self.get_logger().info('Excavator initialized')
    def robot_status_callback(self, msg):
        # Extract excavator current from incoming robot_data (supports multiple message shapes)
        exc, dep = _extract_currents(msg)
        if exc is not None:
            self.motor_amps = exc
            self._latest_excavator_current = exc
    def stop_all(self):
        """Emergency stop helper for all moving parts."""
        self.actuator_voltage.publish(Float32(data=0.0))
    def laser_callback(self, msg):
        self.laser_tripped = msg.data
    
    def current_callback(self, msg):
        self.motor_amps = msg.data

    

    def execute_callback(self, goal_handle: ServerGoalHandle):
        result = Excavate.Result()
        feedback = Excavate.Feedback()
        start_time = self.get_clock().now()
        duration = float(goal_handle.request.dig_duration_sec)

        done = threading.Event()

        # state for vibration sequence
        state = {
            'phase': 'digging',
            'vibration_end': None,
            'pause_end': None,
        }

        def timer_cb():
            if not rclpy.ok():
                done.set()
                return

            if goal_handle.is_cancel_requested:
                self.stop_all()
                goal_handle.canceled()
                result.success = False
                done.set()
                return

            now = self.get_clock().now()
            elapsed_sec = (now - start_time).nanoseconds / 1e9

            # timeout complete
            if elapsed_sec >= duration:
                self.stop_all()
                goal_handle.succeed()
                result.success = True
                result.is_full = False
                result.time_spent = elapsed_sec
                done.set()
                return

            # overcurrent -> abort
            if self.motor_amps > self.max_limit:
                self.stop_all()
                goal_handle.abort()
                result.success = False
                result.is_full = False
                result.time_spent = elapsed_sec
                done.set()
                return

            # laser tripped handling (non-blocking state machine)
            if self.laser_tripped:
                if state['phase'] == 'digging':
                    self.actuator_voltage.publish(Float32(data=0.0))
                    state['vibration_end'] = (now.nanoseconds / 1e9) + 3.0
                    state['phase'] = 'vibrating'
                    return
                elif state['phase'] == 'vibrating':
                    if (now.nanoseconds / 1e9) >= state['vibration_end']:
                        state['pause_end'] = (now.nanoseconds / 1e9) + 0.5
                        state['phase'] = 'pause'
                        return
                elif state['phase'] == 'pause':
                    if (now.nanoseconds / 1e9) >= state['pause_end']:
                        if self.laser_tripped:
                            self.stop_all()
                            goal_handle.succeed()
                            result.success = True
                            result.is_full = True
                            result.time_spent = elapsed_sec
                            done.set()
                            return
                        else:
                            state['phase'] = 'digging'
                            return
            else:
                state['phase'] = 'digging'
                self.actuator_voltage.publish(Float32(data=12.0))
                feedback.laser_tripped = self.laser_tripped
                feedback.estimated_time_remaining = int(max(0, duration - elapsed_sec))
                goal_handle.publish_feedback(feedback)

        timer = self.create_timer(0.1, timer_cb)
        done.wait()
        try:
            self.destroy_timer(timer)
        except Exception:
            pass

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
