#!/usr/bin/env bash
# Check that one OAK-D Pro is reachable from the dev container and streaming depth.
#
# Usage: ./oak_check.sh [seconds to measure, default 10]
#
# Starts depthai_ros_driver as /oak, then reports the rate of the depth and RGB
# topics. Exits non-zero if the camera isn't on USB or no depth arrives.
set -eo pipefail

MEASURE_SECS="${1:-10}"
ROS_DISTRO="${ROS_DISTRO:-humble}"
source "/opt/ros/${ROS_DISTRO}/setup.bash"

# Under a VM the booted OAK may only reappear after the user re-accepts it
# (e.g. UTM's USB prompt), so wait longer than depthai's defaults.
export DEPTHAI_BOOTUP_TIMEOUT="${DEPTHAI_BOOTUP_TIMEOUT:-60000}"
export DEPTHAI_CONNECT_TIMEOUT="${DEPTHAI_CONNECT_TIMEOUT:-60000}"

if ! lsusb | grep -qi "03e7:"; then
  echo "[oak_check] No OAK (Movidius 03e7) on USB." >&2
  echo "  On Docker Desktop for Mac this is expected; see .devcontainer/mac_vm_setup.sh." >&2
  exit 1
fi
lsusb | grep -i "03e7:"

LOG="$(mktemp -t oak_check.XXXX.log)"
echo "[oak_check] Starting depthai_ros_driver (log: $LOG)"
ros2 launch depthai_ros_driver camera.launch.py name:=oak camera_model:=OAK-D-PRO >"$LOG" 2>&1 &
DRIVER_PID=$!
trap 'kill -INT "$DRIVER_PID" 2>/dev/null; wait "$DRIVER_PID" 2>/dev/null || true' EXIT

# Booting the firmware and building the pipeline takes ~10-20 s.
for _ in $(seq 1 90); do
  if ros2 topic list 2>/dev/null | grep -qx "/oak/stereo/image_raw"; then
    break
  fi
  if ! kill -0 "$DRIVER_PID" 2>/dev/null; then
    echo "[oak_check] Driver exited. Last log lines:" >&2
    tail -n 20 "$LOG" >&2
    exit 1
  fi
  sleep 1
done

status=0
for topic in /oak/stereo/image_raw /oak/rgb/image_raw; do
  echo "[oak_check] Measuring $topic for ${MEASURE_SECS}s"
  rate="$(timeout "$MEASURE_SECS" ros2 topic hz "$topic" 2>/dev/null \
    | awk '/average rate/ {r=$3} END {print r}')"
  if [ -n "$rate" ]; then
    echo "  $topic: ${rate} Hz"
  else
    echo "  $topic: no messages" >&2
    status=1
  fi
done

if [ "$status" -ne 0 ]; then
  echo "[oak_check] Last log lines:" >&2
  tail -n 20 "$LOG" >&2
fi
exit "$status"
