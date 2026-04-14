#!/usr/bin/env bash
set -euo pipefail

# Source ROS 2 setup if available
if [ -f "/opt/ros/humble/setup.bash" ]; then
  source /opt/ros/humble/setup.bash
fi

# Allow overriding node script via first arg
if [ "$#" -eq 0 ]; then
  exec python3 "/opt/cometbot_control/state machine/excavator_v1.py"
else
  exec "$@"
fi
