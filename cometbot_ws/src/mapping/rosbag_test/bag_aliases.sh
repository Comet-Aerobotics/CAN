# Shortcuts for testing RTAB-Map on the TUM fr1_xyz bag. Source from ~/.bashrc:
#   source /workspace/cometbot_ws/src/mapping/rosbag_test/bag_aliases.sh
#
# Run each in its own terminal:
#   rtab       RTAB-Map on the bag topics (extra launch args are passed through)
#   fox        Foxglove bridge on $FOX_PORT (default 8080); respawns when killed
#   bagplay    bagreset, then play the bag (extra args go to ros2 bag play, e.g. --rate 0.5)
#   bagreset   clear the RTAB-Map map + odometry and restart the bridge so Foxglove
#              reconnects with an empty 3D panel

BAG_TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FOX_PORT="${FOX_PORT:-8080}"

rtab() {
  ros2 launch rtabmap_launch rtabmap.launch.py \
    rgb_topic:=/camera/rgb/image_color \
    depth_topic:=/camera/depth/image \
    camera_info_topic:=/camera/rgb/camera_info \
    frame_id:=openni_rgb_optical_frame \
    approx_sync:=true \
    use_sim_time:=true \
    rtabmap_args:="--delete_db_on_start" \
    rviz:=false \
    rtabmapviz:=false \
    "$@"
}

fox() {
  # A second loop can't bind the port and would crash-restart forever.
  if pgrep -x foxglove_bridge >/dev/null; then
    echo "[fox] foxglove_bridge already running (another fox terminal?); not starting a second one" >&2
    return 1
  fi
  # Subshell so Ctrl-C ends the loop, while bagreset's kill only restarts the bridge.
  (
    trap 'exit 0' INT
    while :; do
      ros2 run foxglove_bridge foxglove_bridge --ros-args -p port:="$FOX_PORT"
      echo "[fox] bridge exited, restarting (Ctrl-C to stop)"
      sleep 1
    done
  )
}

bagreset() {
  timeout 5 ros2 service call /rtabmap/rtabmap/reset std_srvs/srv/Empty >/dev/null \
    || echo "[bagreset] /rtabmap/rtabmap/reset not available (is rtab running?)"
  timeout 5 ros2 service call /rtabmap/rgbd_odometry/reset_odom std_srvs/srv/Empty >/dev/null \
    || echo "[bagreset] /rtabmap/rgbd_odometry/reset_odom not available"
  if pkill -x foxglove_bridge; then
    sleep 2  # let fox respawn the bridge and Foxglove reconnect
  else
    echo "[bagreset] foxglove_bridge not running (is fox running?)"
  fi
}

bagplay() {
  bagreset
  ros2 bag play "$BAG_TEST_DIR/fr1_xyz_fixed" --clock --remap /tf:=/tf_gt "$@"
}
