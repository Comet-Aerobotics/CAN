#!/usr/bin/env python3
import rclpy
import math
from rclpy.node import Node
from geometry_msgs.msg import Twist, Vector3Stamped

class MoveController(Node):
    def __init__(self):
        super().__init__('move_controller_open_loop')

        # === MOTION SPECS (tune for your robot!) ===
        self.wheel_radius    = 0.0762   # [m]
        self.track_width     = 0.635    # [m]
        self.motor_max_rpm   = 10     # max wheel rpm

        # compute robot max speeds
        omega_wheel_max = self.motor_max_rpm * 2*math.pi / 60.0  
        self.max_lin_speed = omega_wheel_max * self.wheel_radius  
        self.max_ang_speed = 2.0 * omega_wheel_max * self.wheel_radius / self.track_width

        # state machine: IDLE → ROTATING → MOVING → IDLE
        self.state = 'IDLE'
        self.phase_start = None

        # placeholders for current command
        self.rot_direction = 0.0    # ±1
        self.rot_duration  = 0.0
        self.move_direction = 0.0   # ±1
        self.move_duration = 0.0

        # subscribe to polar readings
        self.create_subscription(
            Vector3Stamped,
            '/apriltag_polar',
            self.apriltag_callback,
            10
        )

        self.cmd_vel_pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.create_timer(1.0/50.0, self.control_loop)

        self.get_logger().info('Open-loop MoveController ready (capped output).')

    def apriltag_callback(self, msg: Vector3Stamped):
        if self.state != 'IDLE':
            self.get_logger().info('Busy – ignoring new /apriltag_polar input')
            return
        realmsg = msg.vector
        delta_yaw  = realmsg.y
        delta_dist = realmsg.x

        # figure out rotation phase
        self.rot_direction = math.copysign(1.0, delta_yaw) if abs(delta_yaw) > 1e-6 else 0.0
        self.rot_duration  = abs(delta_yaw) / (self.max_ang_speed + 1e-6)

        # figure out translation phase
        self.move_direction =  if abs(delta_dist) > 1e-6 else 0.0
        self.move_duration  = math.copysign(1.0, delta_dist)abs(delta_dist) / (self.max_lin_speed + 1e-6)

        # start the rotation phase
        self.phase_start = self.get_clock().now()
        self.state       = 'ROTATING'
        self.get_logger().info(
            f'New goal: Δyaw={delta_yaw:.3f} rad ⇒ {self.rot_duration:.2f}s @±1.0, '
            f'Δdist={delta_dist:.3f} m ⇒ {self.move_duration:.2f}s @±1.0'
        )

    def control_loop(self):
        now = self.get_clock().now()
        cmd = Twist()

        if self.state == 'ROTATING':
            elapsed = (now - self.phase_start).nanoseconds * 1e-9
            if elapsed < self.rot_duration:
                # publish unit-rate rotation
                cmd.angular.z = self.rot_direction
            else:
                # switch to move phase
                self.state       = 'MOVING'
                self.phase_start = now
                cmd.angular.z    = 0.0
                self.get_logger().info('Rotation done; starting forward motion.')
        elif self.state == 'MOVING':
            elapsed = (now - self.phase_start).nanoseconds * 1e-9
            if elapsed < self.move_duration:
                # publish unit-rate forward
                cmd.linear.x = self.move_direction
            else:
                # finished both phases → idle
                self.state   = 'IDLE'
                cmd.linear.x = 0.0
                self.get_logger().info('Movement done; entering IDLE.')
        else:
            # IDLE: zero outputs
            cmd.linear.x  = 0.0
            cmd.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd)

def main(args=None):
    rclpy.init(args=args)
    node = MoveController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
