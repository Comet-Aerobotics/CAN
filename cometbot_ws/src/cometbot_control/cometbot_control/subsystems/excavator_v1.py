#!/usr/bin/env python3
"""Preliminary excavator node for testing inside Docker.

This node simulates an excavator subsystem with a simple state machine
that can be driven via a String command topic (/excavator/cmd).

Topics:
  Subscribe: /excavator/cmd (std_msgs/String) - commands: start, stop, dump
  Publish:   /excavator/status (std_msgs/String) - human-readable state
  Publish:   /excavator/bucket_full (std_msgs/Bool)

Parameters (ROS params):
  dig_time_sec: how long to simulate digging before bucket becomes full
  dump_time_sec: how long it takes to dump

This file is intentionally self-contained and lightweight so it can be built
into a Docker image for development testing.
"""
import time
from enum import Enum, auto

import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool


class ExcavatorState(Enum):
    IDLE = auto()
    DIGGING = auto()
    BUCKET_FULL = auto()
    DUMPING = auto()
    STOPPED = auto()


class ExcavatorNode(Node):
    def __init__(self):
        super().__init__('excavator_v1')

        # Parameters with defaults
        self.declare_parameter('dig_time_sec', 5.0)
        self.declare_parameter('dump_time_sec', 3.0)

        self.dig_time = float(self.get_parameter('dig_time_sec').value)
        self.dump_time = float(self.get_parameter('dump_time_sec').value)

        # State
        self.state = ExcavatorState.IDLE
        self._state_start = time.monotonic()

        # Publishers / subscribers
        self.status_pub = self.create_publisher(String, '/excavator/status', 10)
        self.bucket_pub = self.create_publisher(Bool, '/excavator/bucket_full', 10)
        self.cmd_sub = self.create_subscription(String, '/excavator/cmd', self.cmd_cb, 10)

        # Timer 10Hz
        self.timer = self.create_timer(0.1, self.loop)

        # Simulated bucket flag
        self._bucket_full = False

        # Simple logging helpers similar to LunaboticsFSM
        self._logged_once = set()
        # keep track of last announced state for quieter logging
        self._last_announced_state = None

        self.get_logger().info('Excavator node started (dig_time=%.1fs dump_time=%.1fs)' % (self.dig_time, self.dump_time))

    # ---- logging small helpers ----
    def log_once(self, msg, level='info'):
        if msg in self._logged_once:
            return
        getattr(self.get_logger(), level)(msg)
        self._logged_once.add(msg)

    # ---- control functions (encapsulate behaviors) ----
    def start_dig(self):
        self.get_logger().info('Command: start_dig')
        self.transition_to(ExcavatorState.DIGGING)

    def stop_all(self):
        self.get_logger().info('Command: stop_all')
        self.transition_to(ExcavatorState.STOPPED)

    def start_dump(self):
        self.get_logger().info('Command: start_dump')
        # allow dump from DIGGING or BUCKET_FULL
        if self.state in (ExcavatorState.DIGGING, ExcavatorState.BUCKET_FULL):
            self.transition_to(ExcavatorState.DUMPING)

    def _on_bucket_full(self):
        # Called when bucket becomes full
        self.get_logger().info('Bucket is now FULL')

    def _on_bucket_emptied(self):
        self.get_logger().info('Bucket emptied')

    # ---- command handling ----
    def cmd_cb(self, msg: String):
        cmd = (msg.data or '').strip().lower()
        if cmd == 'start':
            self.start_dig()
        elif cmd == 'stop':
            self.stop_all()
        elif cmd == 'dump':
            self.start_dump()
        else:
            self.get_logger().warn(f'Unknown excavator command: "{cmd}"')

    def transition_to(self, new_state: ExcavatorState):
        if self.state == new_state:
            return
        self.get_logger().info(f'Excavator: {self.state.name} -> {new_state.name}')
        self.state = new_state
        self._state_start = time.monotonic()

    def publish_state(self):
        s = String()
        s.data = self.state.name
        self.status_pub.publish(s)

        b = Bool()
        b.data = self._bucket_full
        self.bucket_pub.publish(b)

    def loop(self):
        # Main simulation loop (called by timer)
        now = time.monotonic()
        elapsed = now - self._state_start

        if self.state == ExcavatorState.IDLE:
            # idle: do nothing
            self.log_once('Excavator idle')

        elif self.state == ExcavatorState.DIGGING:
            # Simulate digging until bucket is full
            if elapsed >= self.dig_time:
                self._bucket_full = True
                # announce and transition
                self._on_bucket_full()
                self.transition_to(ExcavatorState.BUCKET_FULL)
            else:
                # occasional info to show progress
                if int(elapsed) % 2 == 0:
                    self.get_logger().debug(f'Digging... {elapsed:.1f}s')

        elif self.state == ExcavatorState.BUCKET_FULL:
            # Wait for explicit dump command or auto-dump after a short hold
            # For safety, do nothing but advertise bucket full
            pass

        elif self.state == ExcavatorState.DUMPING:
            # Simulate dump
            if elapsed >= self.dump_time:
                self._bucket_full = False
                # finished dumping
                self._on_bucket_emptied()
                self.transition_to(ExcavatorState.IDLE)

        elif self.state == ExcavatorState.STOPPED:
            # stopped: clear timers but keep bucket flag
            self.log_once('Excavator stopped (manual)')

        # publish state and bucket flag every loop
        # quieter publish: only log state change once
        if self._last_announced_state != self.state.name:
            self.get_logger().info(f'Excavator state: {self.state.name}')
            self._last_announced_state = self.state.name
        self.publish_state()


def main(args=None):
    rclpy.init(args=args)
    node = ExcavatorNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt - shutting down excavator node')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
