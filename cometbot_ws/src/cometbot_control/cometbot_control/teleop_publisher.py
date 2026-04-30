"""
::::To Do::::
++++ DONE
---- TODO
**** TODO Important

---- Remove locking. The node's callback are multually exclusive by default 

"""

import rclpy
import math
from rclpy.node import Node
from sensor_msgs.msg import Joy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32
from rcl_interfaces.msg import ParameterDescriptor, FloatingPointRange, IntegerRange

class TeleopPublisher(Node):
    def __init__(self):
        super().__init__('teleop_publisher')  # Initialize the node with the name 'teleop_publisher'

        # Declare parameters with default values
        self.declare_parameter(
            'cmd_vel_pub_frequency', 
            20.0, 
            ParameterDescriptor(
                description='Frequency to publish cmd_vel messages in Hz. \nMAKE SURE JOY_NODE IS ALSO RUNNING AT SAME OR HIGHER FREQUENCY',
                floating_point_range=[
                    FloatingPointRange(from_value=0.0, to_value=100.0)
                ]
            )
        )

        self.declare_parameter(
            'deadzone',
            0.1,
            ParameterDescriptor(
                description='Deadzone for joystick input',
                floating_point_range=[
                    FloatingPointRange(from_value=0.0, to_value=1.0, step=0.01)
                ]
            )
        )

        self.declare_parameter(
            'joystick_power', 
            3, 
            ParameterDescriptor(
                description='Exponent for scaling joystick input', 
                integer_range=[
                    IntegerRange(from_value = 1, to_value = 9, step = 2)
                ]
            )
        )

        # Create a subscription to the 'joy' topic
        self.subscription = self.create_subscription(
            Joy,  # Message type: Joy
            'joy',  # Topic name: 'joy'
            self.listener_callback,  # Callback function to handle incoming messages
            10  # QoS profile depth
        )

        # Create a publisher for the 'cmd_vel' topic
        self.cmd_vel_publisher = self.create_publisher(Twist, 'cmd_vel', 10)
        self.depositor_publisher = self.create_publisher(Float32, 'depositor/position_setpoint', 10)
        self.excavator_actuator_publisher = self.create_publisher(Float32, 'excavator/actuator_output', 10)
        self.excavator_motor_publisher = self.create_publisher(Float32, 'excavator/velocity_setpoint', 10)

        # Set up a timer to publish Twist messages at the specified frequency
        timer_frequency = self.get_parameter('cmd_vel_pub_frequency').get_parameter_value().double_value
        self.timer = self.create_timer(1.0 / timer_frequency, self.timer_callback)

        # Only edit in subscriber
        self.input = Twist()
        self.output = Twist()
        self.depositor_position_setpoint = 0.0
        self.excavator_actuator_output = 0.0
        self.excavator_motor_velocity_setpoint = 0.0
        self.previous_axes = []
        self.previous_buttons = []

        self.deadzone = self.get_parameter('deadzone').get_parameter_value().double_value
        self.power = self.get_parameter('joystick_power').get_parameter_value().integer_value
        self.depositor_step = 0.25
        self.excavator_actuator_step = 0.1
        self.excavator_motor_step = 100.0
        self.depositor_min = -1000.0
        self.depositor_max = 1000.0
        self.excavator_actuator_min = -1.0
        self.excavator_actuator_max = 1.0
        self.excavator_motor_min = -5000.0
        self.excavator_motor_max = 5000.0
        
        # Prevent unused variable warning
        self.subscription
        self.get_logger().info('Initialized')

    def _axis(self, msg: Joy, index: int) -> float:
        if index < len(msg.axes):
            return msg.axes[index]
        return 0.0

    def _button(self, msg: Joy, index: int) -> int:
        if index < len(msg.buttons):
            return msg.buttons[index]
        return 0

    def _clamp(self, value: float, minimum: float, maximum: float) -> float:
        return max(min(value, maximum), minimum)

    def listener_callback(self, msg: Joy):
        # Map joystick axes to linear and angular velocities
        self.input.linear.x = self._axis(msg, 1)  # Forward/backward movement
        self.input.angular.z = self._axis(msg, 3)  # Left/right rotation

        dpad_horizontal = self._axis(msg, 6)
        a_button = self._button(msg, 0)
        b_button = self._button(msg, 1)
        lb_button = self._button(msg, 4)
        rb_button = self._button(msg, 5)

        if dpad_horizontal > 0.5 and (len(self.previous_axes) <= 6 or self.previous_axes[6] <= 0.5):
            self.depositor_position_setpoint = self._clamp(self.depositor_position_setpoint + self.depositor_step, self.depositor_min, self.depositor_max)
        elif dpad_horizontal < -0.5 and (len(self.previous_axes) <= 6 or self.previous_axes[6] >= -0.5):
            self.depositor_position_setpoint = self._clamp(self.depositor_position_setpoint - self.depositor_step, self.depositor_min, self.depositor_max)

        if a_button and (len(self.previous_buttons) <= 0 or not self.previous_buttons[0]):
            self.excavator_actuator_output = self._clamp(self.excavator_actuator_output + self.excavator_actuator_step, self.excavator_actuator_min, self.excavator_actuator_max)
        elif b_button and (len(self.previous_buttons) <= 1 or not self.previous_buttons[1]):
            self.excavator_actuator_output = self._clamp(self.excavator_actuator_output - self.excavator_actuator_step, self.excavator_actuator_min, self.excavator_actuator_max)

        if lb_button and (len(self.previous_buttons) <= 4 or not self.previous_buttons[4]):
            self.excavator_motor_velocity_setpoint = self._clamp(self.excavator_motor_velocity_setpoint + self.excavator_motor_step, self.excavator_motor_min, self.excavator_motor_max)
        elif rb_button and (len(self.previous_buttons) <= 5 or not self.previous_buttons[5]):
            self.excavator_motor_velocity_setpoint = self._clamp(self.excavator_motor_velocity_setpoint - self.excavator_motor_step, self.excavator_motor_min, self.excavator_motor_max)

        self.previous_axes = list(msg.axes)
        self.previous_buttons = list(msg.buttons)

        # Log the updated Twist message data
        self.get_logger().info(
            'Subscribing: Linear x: %s, Angular z: %s, Depositor: %s, Excavator output: %s, Excavator velocity: %s'
            % (
                self.input.linear.x,
                self.input.angular.z,
                self.depositor_position_setpoint,
                self.excavator_actuator_output,
                self.excavator_motor_velocity_setpoint,
            )
        )

    def timer_callback(self):
        self.output.linear.x = self.input.linear.x
        self.output.angular.z = self.input.angular.z
        

        # Apply deadzone filtering
        if math.hypot(self.output.linear.x, self.output.angular.z) < self.deadzone:
            self.output.linear.x = 0.0
            self.output.angular.z = 0.0
        else:
            # Apply scaling to joystick input
            
            self.output.linear.x = math.pow(self.output.linear.x, self.power)
            self.output.angular.z = math.pow(self.output.angular.z, self.power)
            
        self.cmd_vel_publisher.publish(self.output)  # Publish the Twist message

        depositor_msg = Float32()
        depositor_msg.data = self.depositor_position_setpoint
        self.depositor_publisher.publish(depositor_msg)

        excavator_actuator_msg = Float32()
        excavator_actuator_msg.data = self.excavator_actuator_output
        self.excavator_actuator_publisher.publish(excavator_actuator_msg)

        excavator_motor_msg = Float32()
        excavator_motor_msg.data = self.excavator_motor_velocity_setpoint
        self.excavator_motor_publisher.publish(excavator_motor_msg)

        # Log the publishing event
        self.get_logger().info(
            'Publishing: Linear x: %s, Angular z: %s, Depositor: %s, Excavator output: %s, Excavator velocity: %s'
            % (
                self.output.linear.x,
                self.output.angular.z,
                self.depositor_position_setpoint,
                self.excavator_actuator_output,
                self.excavator_motor_velocity_setpoint,
            )
        )

def main(args=None):
    try:
        # Initialize the ROS 2 Python client library
        rclpy.init(args=args)

        # Create an instance of the TeleopPublisher node
        teleop_publisher = TeleopPublisher()

        # Spin the node to process callbacks
        rclpy.spin(teleop_publisher)
    except KeyboardInterrupt:
        pass


# Entry point for the script
if __name__ == '__main__':
    main()
