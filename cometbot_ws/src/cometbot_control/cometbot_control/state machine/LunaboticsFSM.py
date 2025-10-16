import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from enum import Enum, auto

class RoverState(Enum):
    STARTUP = auto()
    NAV_TO_MINE = auto()
    EXCAVATE = auto()
    NAV_TO_CONSTRUCT = auto()
    DEPOSIT = auto()
    RETURN = auto()
    IDLE = auto()
    EMERGENCY_STOP = auto()

class LunaboticsFSM(Node):
    def __init__(self):
        super().__init__('lunabotics_fsm')
        self.state = RoverState.STARTUP
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.loop)
        self.mine_arrived = False
        self.dump_arrived = False
        self.bucket_full = False
        self.deposited = False
        self.system_ready = True
        self.emergency = False

    def set_state(self, new_state: RoverState):
        if self.state != new_state:
            self.get_logger().info(f"Transition: {self.state.name} > {new_state.name}")
            self.state = new_state

    def loop(self):
        twist = Twist()

        if self.emergency:
            self.set_state(RoverState.EMERGENCY_STOP)

        if self.state == RoverState.STARTUP:
            self.get_logger().info_once("Initializing systems…")
            if self.system_ready:
                self.set_state(RoverState.NAV_TO_MINE)

        elif self.state == RoverState.NAV_TO_MINE:
            self.get_logger().info_throttle(2.0, "Navigating to mine site")
            twist.linear.x = 0.3
            if self.mine_arrived:
                self.set_state(RoverState.EXCAVATE)

        elif self.state == RoverState.EXCAVATE:
            self.get_logger().info_throttle(2.0, "Excavating regolith")
            if self.bucket_full:
                self.set_state(RoverState.NAV_TO_CONSTRUCT)

        elif self.state == RoverState.NAV_TO_CONSTRUCT:
            self.get_logger().info_throttle(2.0, "Navigating to dump site")
            twist.linear.x = 0.3
            if self.dump_arrived:
                self.set_state(RoverState.DEPOSIT)

        elif self.state == RoverState.DEPOSIT:
            self.get_logger().info_throttle(2.0, "Depositing material")
            if self.deposited:
                self.set_state(RoverState.RETURN)

        elif self.state == RoverState.RETURN:
            self.get_logger().info_throttle(2.0, "Returning to base")
            twist.linear.x = 0.3
            base_arrived = False
            if base_arrived:
                self.set_state(RoverState.IDLE)

        elif self.state == RoverState.IDLE:
            self.get_logger().info_once("Rover is idle - mission complete")
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        elif self.state == RoverState.EMERGENCY_STOP:
            self.get_logger().error("!!! EMERGENCY STOP TRIGGERED !!!")
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_pub.publish(twist)


def main(args=None):
    rclpy.init(args=args)
    node = LunaboticsFSM()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
