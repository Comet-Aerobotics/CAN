#!/usr/bin/env bash
set -euo pipefail
ROS_DISTRO=${ROS_DISTRO:-humble}

echo "[devcontainer] Appending ROS sourcing to ~/.bashrc"
if ! grep -q "/opt/ros/$ROS_DISTRO/setup.bash" "$HOME/.bashrc"; then
  echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> "$HOME/.bashrc"
fi
if ! grep -q "microros_ws/install/local_setup.bash" "$HOME/.bashrc"; then
  cat <<'EOT' >> "$HOME/.bashrc"
if [ -f "$HOME/microros_ws/install/local_setup.bash" ]; then
  source "$HOME/microros_ws/install/local_setup.bash"
fi
EOT
fi

# Create microros_ws and clone micro_ros_setup if not present
if [ ! -d "$HOME/microros_ws/src/micro_ros_setup" ]; then
  echo "[devcontainer] Creating microros_ws and cloning micro_ros_setup"
  mkdir -p "$HOME/microros_ws/src"
  git clone -b "$ROS_DISTRO" https://github.com/micro-ROS/micro_ros_setup.git "$HOME/microros_ws/src/micro_ros_setup"
fi

echo "[devcontainer] Updating rosdep (may require sudo)"
sudo rosdep update || true
echo "[devcontainer] Fixing rosdep permissions and updating cache for the non-root user"
sudo rosdep fix-permissions || true
# run rosdep update as the non-root user to populate user cache (~/.ros/rosdep)
rosdep update || true

echo "[devcontainer] Installing rosdep dependencies for microros_ws (best-effort)"
cd "$HOME/microros_ws" || true
rosdep install --from-paths src --ignore-src -y || true

echo "[devcontainer] Setup complete. To finish, open a new terminal (or run 'source ~/.bashrc')."
echo "Build your workspaces manually when ready, e.g.:"
echo "  colcon build --workspace /workspace/cometbot_ws"
echo "  ros2 run cometbot_control teleop_publisher"
