Testing the Excavator Action Server (no hardware)

Quick steps

1. Build and source your workspace (if you haven't already):

   ```bash
   # source ROS 2 distro
   source /opt/ros/<distro>/setup.bash
   # from workspace root (optional if already built)
   colcon build --packages-select cometbot_msgs cometbot_control
   source install/setup.bash
   ```

2. Run the action server (in terminal A):

   ```bash
   python3 src/cometbot_control/cometbot_control/excavator_action_server.py
   ```

3. Run the mock hardware (in terminal B):

   ```bash
   python3 src/cometbot_control/scripts/mock_hardware.py
   ```

4. Send a goal with the test client (in terminal C):

   ```bash
   python3 src/cometbot_control/scripts/excavator_test_client.py 12
   # or use ros2 action send_goal
   ros2 action send_goal /excavate cometbot_msgs/action/Excavate "{dig_duration_sec: 12}"
   ```

Notes
- The mock node publishes `/laser_sensor/status` (Bool) and `robot_data` (RobotStatusMessage).
- The mock listens for `/hardware/actuator_voltage` so you can verify commands.
- Adjust the client's duration to exercise normal completion, laser-tripped behavior, and current-limit aborts.
