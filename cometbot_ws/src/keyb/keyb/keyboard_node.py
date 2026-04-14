import select
import sys
import termios
import time
import tty
import math

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Joy


class KeyToJoy(Node):
    def __init__(self):
        super().__init__("keyb")
        self.publisher_ = self.create_publisher(Joy, "joy", 10)
        self.speed = 0.5  # Percentage

        # Terminal settings to read raw keypresses
        self.settings = termios.tcgetattr(sys.stdin)

        # State tracking
        self.current_axes = [0.0, 0.0, 0.0, 0.0]
        self.last_key_time = 0.0

        # This timeout bridges the gap between repeated 'W' characters sent by the OS.
        # If the robot feels too "sticky" when you let go, decrease this to 0.1.
        self.key_timeout = 0.15

        # Timer for polling and publishing (50Hz)
        self.create_timer(0.02, self.timer_callback)
        self.get_logger().info(
            "Keyboard to Joy node started. Use WASD for directions, QE for speed control! Press Ctrl+C to quit."
        )

    def get_key(self):
        """Reads a single character from stdin without blocking."""
        tty.setraw(sys.stdin.fileno())
        # Non-blocking read with a tiny timeout
        rlist, _, _ = select.select([sys.stdin], [], [], 0.01)
        if rlist:
            key = sys.stdin.read(1).lower()  # Handle shift-lock or caps
        else:
            key = None
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.settings)
        return key

    def timer_callback(self):
        key = self.get_key()
        now = time.time()

        if key is not None:
            # We detected a keypress! Update the timestamp.
            self.last_key_time = now

            # Reset axes and apply the current direction immediately
            self.current_axes = [0.0, 0.0, 0.0, 0.0]

            speed = math.pow(self.speed, 1/3)

            if key == "w":
                self.current_axes[1] = speed  # Forward
            elif key == "s":
                self.current_axes[1] = -speed  # Backward
            elif key == "a":
                self.current_axes[0] = speed  # Left
            elif key == "d":
                self.current_axes[0] = -speed  # Right

            # Speed control
            if key == "q":
                self.speed = round(min(1.0, self.speed + 0.05), 2)
                self.get_logger().info(f"Current speed: {self.speed:.2f}%")
            elif key == "e":
                self.speed = round(max(0.0, self.speed - 0.05), 2)
                self.get_logger().info(f"Current speed: {self.speed:.2f}%")
        else:
            # No key seen in this specific loop iteration.
            # Only reset to 0 if we haven't seen a key for longer than the timeout.
            if now - self.last_key_time > self.key_timeout:
                self.current_axes = [0.0, 0.0, 0.0, 0.0]

        # Construct and publish the Joy message
        msg = Joy()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.axes = self.current_axes
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = KeyToJoy()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Crucial: Reset terminal settings so your terminal doesn't break
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, node.settings)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
    
