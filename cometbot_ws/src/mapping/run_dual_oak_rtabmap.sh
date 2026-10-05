#!/usr/bin/env bash
# Start RTAB-Map SLAM with the front and back OAK-D Pro cameras, plus the
# Foxglove bridge (connect Foxglove to ws://localhost:8765).
#
# Usage:
#   FRONT_MXID=<id> BACK_MXID=<id> ./run_dual_oak_rtabmap.sh [launch_arg:=value ...]
#
# Examples:
#   ./run_dual_oak_rtabmap.sh front_x:=0.35 back_x:=-0.35
#   ./run_dual_oak_rtabmap.sh localization:=true     # reuse the saved map
#   ./run_dual_oak_rtabmap.sh use_imu:=false
#
# Finding the MXIDs: run once with one camera plugged in and look for
#   "Camera with MXID: <id> and Name: ... connected!"
# in the output. Without MXIDs, each driver grabs the first free camera, so
# front and back may be swapped.
set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROS_DISTRO="${ROS_DISTRO:-humble}"

source "/opt/ros/${ROS_DISTRO}/setup.bash"
WS_SETUP="${SCRIPT_DIR}/../../install/setup.bash"
if [ -f "$WS_SETUP" ]; then
  source "$WS_SETUP"
fi

missing=()
for pkg in depthai_ros_driver image_proc rtabmap_slam rtabmap_odom rtabmap_sync imu_filter_madgwick foxglove_bridge; do
  ros2 pkg prefix "$pkg" >/dev/null 2>&1 || missing+=("ros-${ROS_DISTRO}-${pkg//_/-}")
done
if [ ${#missing[@]} -gt 0 ]; then
  echo "Missing ROS packages. Install with:" >&2
  echo "  sudo apt-get install ${missing[*]}" >&2
  exit 1
fi

if ! lsusb 2>/dev/null | grep -qi "03e7:"; then
  echo "Warning: no OAK (Movidius 03e7) device visible on USB." >&2
fi

if [ -z "${FRONT_MXID:-}" ] || [ -z "${BACK_MXID:-}" ]; then
  echo "Warning: FRONT_MXID/BACK_MXID not set; front and back cameras may be swapped." >&2
fi

exec ros2 launch "${SCRIPT_DIR}/dual_oak_rtabmap.launch.py" \
  front_mxid:="${FRONT_MXID:-}" \
  back_mxid:="${BACK_MXID:-}" \
  "$@"
