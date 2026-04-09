#!/usr/bin/env python3
"""
Safe robot hardware test node.
Gradually ramps up motor speeds for hardware validation.
Reduced to conservative speeds for safety.
"""

import time
import math
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32, Bool


class RobotTestNode(Node):
    """Test node for hardware validation."""

    def __init__(self):
        super().__init__('robot_test')
        
        # Create publishers
        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.enabled_pub = self.create_publisher(Bool, 'enabled', 10)
        self.actuator_pub = self.create_publisher(Float32, '/hardware/actuator_voltage', 10)
        self.depositor_pub = self.create_publisher(Float32, '/depositor/status', 10)
        
        # Test parameters
        self.declare_parameter('test_duration_sec', 30.0)
        self.declare_parameter('max_linear_speed', 0.3)  # Reduced from typical 1.0
        self.declare_parameter('max_angular_speed', 0.2)  # Reduced from typical 1.0
        self.declare_parameter('max_actuator_voltage', 6.0)  # Reduced from 12.0
        self.declare_parameter('max_depositor_power', 0.4)  # Reduced from 1.0
        
        self.test_duration = float(self.get_parameter('test_duration_sec').value)
        self.max_linear = float(self.get_parameter('max_linear_speed').value)
        self.max_angular = float(self.get_parameter('max_angular_speed').value)
        self.max_actuator = float(self.get_parameter('max_actuator_voltage').value)
        self.max_depositor = float(self.get_parameter('max_depositor_power').value)
        
        self.start_time = self.get_clock().now()
        self.test_running = True
        
        # Enable robot
        enabled_msg = Bool()
        enabled_msg.data = True
        self.enabled_pub.publish(enabled_msg)
        
        # Timer for test loop
        self.timer = self.create_timer(0.1, self.test_loop)
        
        self.get_logger().info("="*60)
        self.get_logger().info("🤖 Robot Test Node Started")
        self.get_logger().info("="*60)
        self.get_logger().info(f"Test Duration: {self.test_duration}s")
        self.get_logger().info(f"Max Linear Speed: {self.max_linear} m/s")
        self.get_logger().info(f"Max Angular Speed: {self.max_angular} rad/s")
        self.get_logger().info(f"Max Actuator Voltage: {self.max_actuator}V")
        self.get_logger().info(f"Max Depositor Power: {self.max_depositor}")
        self.get_logger().info("="*60)

    def test_loop(self):
        """Main test loop."""
        now = self.get_clock().now()
        elapsed = (now - self.start_time).nanoseconds / 1e9
        
        if elapsed > self.test_duration:
            self.get_logger().info("\n" + "="*60)
            self.get_logger().info("✅ Test Complete!")
            self.get_logger().info("="*60)
            self.stop_all()
            rclpy.shutdown()
            return
        
        # Progress (0.0 to 1.0)
        progress = elapsed / self.test_duration
        
        # Smooth ramp-up (ease-in curve)
        ramp = math.sin(progress * math.pi / 2)  # 0 to 1 smoothly
        
        # Print phase info
        if int(elapsed) % 5 == 0 and elapsed > int(elapsed) - 0.15:
            phase = self.get_phase(elapsed)
            self.get_logger().info(f"[{elapsed:5.1f}s] {phase:35s} Progress: {progress*100:5.1f}%")
        
        # Test phases
        if elapsed < self.test_duration / 4:
            # Phase 1: Forward/backward movement
            self.test_drivetrain(elapsed, ramp)
        elif elapsed < self.test_duration / 2:
            # Phase 2: Rotation
            self.test_rotation(elapsed - self.test_duration/4, ramp)
        elif elapsed < 3 * self.test_duration / 4:
            # Phase 3: Actuator voltage
            self.test_actuator(elapsed - self.test_duration/2, ramp)
        else:
            # Phase 4: Depositor
            self.test_depositor(elapsed - 3*self.test_duration/4, ramp)

    def get_phase(self, elapsed):
        """Get current test phase."""
        quarter = self.test_duration / 4
        if elapsed < quarter:
            return "Phase 1: Drivetrain Forward/Backward"
        elif elapsed < 2 * quarter:
            return "Phase 2: Drivetrain Rotation"
        elif elapsed < 3 * quarter:
            return "Phase 3: Actuator Voltage Ramp"
        else:
            return "Phase 4: Depositor Power Ramp"

    def test_drivetrain(self, elapsed, ramp):
        """Test drivetrain forward/backward."""
        msg = Twist()
        phase = (elapsed % 2.0) / 2.0  # Toggle every 2 seconds
        
        if phase < 0.5:
            # Forward
            msg.linear.x = self.max_linear * ramp
        else:
            # Backward
            msg.linear.x = -self.max_linear * ramp
        
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        msg.angular.z = 0.0
        
        self.cmd_vel_pub.publish(msg)

    def test_rotation(self, elapsed, ramp):
        """Test drivetrain rotation."""
        msg = Twist()
        phase = (elapsed % 2.0) / 2.0  # Toggle every 2 seconds
        
        msg.linear.x = 0.0
        msg.linear.y = 0.0
        msg.linear.z = 0.0
        
        if phase < 0.5:
            # Turn left
            msg.angular.z = self.max_angular * ramp
        else:
            # Turn right
            msg.angular.z = -self.max_angular * ramp
        
        msg.angular.x = 0.0
        msg.angular.y = 0.0
        
        self.cmd_vel_pub.publish(msg)

    def test_actuator(self, elapsed, ramp):
        """Test actuator voltage ramp."""
        # Ensure drivetrain is idle
        idle_msg = Twist()
        self.cmd_vel_pub.publish(idle_msg)
        
        # Ramp actuator voltage
        voltage = self.max_actuator * ramp
        msg = Float32()
        msg.data = voltage
        self.actuator_pub.publish(msg)

    def test_depositor(self, elapsed, ramp):
        """Test depositor power ramp."""
        # Ensure actuator is idle
        actuator_msg = Float32()
        actuator_msg.data = 0.0
        self.actuator_pub.publish(actuator_msg)
        
        # Ramp depositor power
        power = self.max_depositor * ramp
        msg = Float32()
        msg.data = power
        self.depositor_pub.publish(msg)

    def stop_all(self):
        """Stop all motors."""
        # Stop drivetrain
        idle = Twist()
        self.cmd_vel_pub.publish(idle)
        
        # Stop actuator
        zero = Float32()
        zero.data = 0.0
        self.actuator_pub.publish(zero)
        
        # Stop depositor
        self.depositor_pub.publish(zero)


def main(args=None):
    rclpy.init(args=args)
    node = RobotTestNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("\n⚠️  Test interrupted by user")
        node.stop_all()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
