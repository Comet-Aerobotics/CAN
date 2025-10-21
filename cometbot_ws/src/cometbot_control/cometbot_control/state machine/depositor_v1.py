#!/usr/bin/env python3
"""Preliminary depositor node for testing inside Docker.

This node simulates a depositor (dumping regolith) with a small state machine.

Topics:
  Subscribe: /depositor/cmd (std_msgs/String) - commands: start, stop, receive, dump, return
  Publish:   /depositor/status (std_msgs/String) - human-readable state
  Publish:   /depositor/has_space (std_msgs/Bool) - whether depositor has capacity to receive

Parameters:
  move_time_sec: how long to simulate moving to dump location
  receive_time_sec: how long to accept material
  dump_time_sec: how long dumping takes

This file mirrors the excavator node's lightweight design for easy Docker testing.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class DepositorState(Enum):
    IDLE = auto()
    MOVING_TO_DUMP = auto()
    RECEIVING = auto()
    DUMPING = auto()
    RETURNING = auto()
    STOPPED = auto()


class DepositorNode(Node):
    def __init__(self):
        super().__init__('depositor_v1')

        # Parameters with defaults
        self.declare_parameter('move_time_sec', 2.0)
        self.declare_parameter('receive_time_sec', 4.0)
        self.declare_parameter('dump_time_sec', 3.0)

        self.move_time = float(self.get_parameter('move_time_sec').value)
        self.receive_time = float(self.get_parameter('receive_time_sec').value)
        self.dump_time = float(self.get_parameter('dump_time_sec').value)

        # State
        self.state = DepositorState.IDLE
        self._state_start = time.monotonic()

        # Publishers / subscribers
        self.status_pub = self.create_publisher(String, '/depositor/status', 10)
        self.space_pub = self.create_publisher(Bool, '/depositor/has_space', 10)
        self.cmd_sub = self.create_subscription(String, '/depositor/cmd', self.cmd_cb, 10)

        # Timer 10Hz
        self.timer = self.create_timer(0.1, self.loop)

        # Capacity flag: True if depositor can receive material
        self._has_space = True

        self._logged_once = set()

        self.get_logger().info('Depositor node started (move=%.1fs receive=%.1fs dump=%.1fs)' % (self.move_time, self.receive_time, self.dump_time))

    def log_once(self, msg, level='info'):
        if msg in self._logged_once:
            return
        getattr(self.get_logger(), level)(msg)
        self._logged_once.add(msg)

    def cmd_cb(self, msg: String):
        cmd = (msg.data or '').strip().lower()
        if cmd == 'start':
            if self.state in (DepositorState.IDLE, DepositorState.RETURNING):
                # begin moving to dump site
                self.transition_to(DepositorState.MOVING_TO_DUMP)
        elif cmd == 'receive':
            # simulate receiving material from excavator
            if self.state in (DepositorState.MOVING_TO_DUMP, DepositorState.IDLE) and self._has_space:
                # if not at dump site yet, move there first
                if self.state != DepositorState.MOVING_TO_DUMP:
                    self.transition_to(DepositorState.MOVING_TO_DUMP)
                else:
                    self.transition_to(DepositorState.RECEIVING)
        elif cmd == 'dump':
            if self.state in (DepositorState.RECEIVING, DepositorState.MOVING_TO_DUMP, DepositorState.IDLE) and not self._has_space:
                self.transition_to(DepositorState.DUMPING)
        elif cmd == 'return':
            self.transition_to(DepositorState.RETURNING)
        elif cmd == 'stop':
            self.transition_to(DepositorState.STOPPED)
        else:
            self.get_logger().warn(f'Unknown depositor command: "{cmd}"')

    def transition_to(self, new_state: DepositorState):
        if self.state == new_state:
            return
        self.get_logger().info(f'Depositor: {self.state.name} -> {new_state.name}')
        self.state = new_state
        self._state_start = time.monotonic()

    def publish_state(self):
        s = String()
        s.data = self.state.name
        self.status_pub.publish(s)

        b = Bool()
        b.data = self._has_space
        self.space_pub.publish(b)

    def loop(self):
        now = time.monotonic()
        elapsed = now - self._state_start

        if self.state == DepositorState.IDLE:
            self.log_once('Depositor idle')

        elif self.state == DepositorState.MOVING_TO_DUMP:
            if elapsed >= self.move_time:
                # Arrived at dump area, ready to receive if has space
                if self._has_space:
                    self.transition_to(DepositorState.RECEIVING)
                else:
                    # nothing to receive, stay idle at site
                    self.transition_to(DepositorState.IDLE)

        elif self.state == DepositorState.RECEIVING:
            # simulate receiving material until no space
            if elapsed >= self.receive_time:
                self._has_space = False
                self.transition_to(DepositorState.IDLE)
            else:
                # debug progress
                if int(elapsed) % 2 == 0:
                    self.get_logger().debug(f'Receiving... {elapsed:.1f}s')

        elif self.state == DepositorState.DUMPING:
            if elapsed >= self.dump_time:
                self._has_space = True
                self.transition_to(DepositorState.IDLE)

        elif self.state == DepositorState.RETURNING:
            if elapsed >= self.move_time:
                self.transition_to(DepositorState.IDLE)

        elif self.state == DepositorState.STOPPED:
            self.log_once('Depositor stopped (manual)')

        # publish state flags every loop
        self.publish_state()


def main(args=None):
    rclpy.init(args=args)
    node = DepositorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt - shutting down depositor node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
