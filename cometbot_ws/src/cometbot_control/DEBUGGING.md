# Debugging Guide - Action-Based Orchestration

## Before Running: Setup Checklist

- [ ] Built the package: `colcon build --packages-select cometbot_control`
- [ ] Sourced setup: `source install/setup.bash`
- [ ] ROS domain ID is set (optional): `export ROS_DOMAIN_ID=42`
- [ ] All terminals source the same setup script

## Startup Issues

### Problem: "Package not found"
```bash
# Solution:
colcon build --packages-select cometbot_control
source install/setup.bash
```

### Problem: "Module 'cometbot_control' has no attribute 'action'"
```bash
# The action interfaces weren't generated
# Solution:
colcon build --packages-select cometbot_control
colcon clean packages --select cometbot_control
colcon build --packages-select cometbot_control
```

### Problem: "No module named 'numpy'" (in load_sensor.py)
```bash
pip install numpy
```

## Running Components

### Verify Nodes Started Successfully

```bash
# In a new terminal:
ros2 node list
```

Expected output:
```
/depositor_action_server
/excavator_action_server
/load_sensor
/mission_orchestrator
```

If missing nodes, check the terminal where you started them for error messages.

### Verify Topics Publishing

```bash
ros2 topic list
```

Expected output includes:
```
/fsm/material_total
/fsm/state
/load_sensor/bucket_full
/load_sensor/weight
```

## Runtime Debugging

### Mission Stuck in State

```bash
# Check what state it's in:
ros2 topic echo /fsm/state

# Expected: State changes every 2-5 seconds
# If not changing: Check mission_orchestrator logs for errors
```

### Load Sensor Not Publishing

```bash
# Check weight updates:
ros2 topic echo /load_sensor/weight --rate=2

# Expected: Values 0.0-5.0 kg, changing value
# If constant: Load sensor might be stuck
```

```bash
# Check if server is responsive:
ros2 node info /load_sensor

Expected: Node has publishers for /load_sensor/weight and /load_sensor/bucket_full
```

### Actions Not Completing

```bash
# Manually test excavator action:
ros2 action send_goal /excavator/excavate \
  cometbot_control/action/Excavate \
  "{dig_duration_sec: 5}"

# Expected: Goal accepted, feedback every 100ms, then result
# If not accepted: Check excavator_action_server logs
```

### All Nodes Running but Nothing Happening

```bash
# Check if there are RCL errors
# Look at terminal outputs for messages like:
#   "[mission_orchestrator] ERROR: ..."
#   "[excavator_action_server] ERROR: ..."

# Common causes:
# 1. ROS_DOMAIN_ID mismatch (if set manually)
# 2. Local loopback not configured (use same machine initially)
# 3. Firewall blocking ports (should work on localhost)
```

## Monitoring Tools

### Watch All Activity
```bash
# Terminal 1: Monitor state
ros2 topic echo /fsm/state

# Terminal 2: Monitor material
ros2 topic echo /fsm/material_total --rate=1

# Terminal 3: Monitor load sensor
ros2 topic echo /load_sensor/weight --rate=2
```

### Check Action Status
```bash
# List all actions:
ros2 action list

# Expected: 
#   /excavator/excavate
#   /depositor/deposit

# Get action info:
ros2 action info /excavator/excavate

# Expected:
#   Action: /excavator/excavate
#   Action type: cometbot_control/action/Excavate
#   Number of action servers: 1
#   Number of action clients: 1
```

### View Raw Messages

```bash
# View complete message structure:
ros2 interface show cometbot_control/action/Excavate

# Expected: Shows Goal, Result, Feedback structures
```

## Per-Component Debugging

### Load Sensor Debugging

```bash
# Check if sensor is actually updating:
ros2 topic echo /load_sensor/weight -n 10 | grep -v "data: " | sort | uniq -c

# If all values the same: Sensor is stuck
# If values changing: Sensor is working

# Check bucket_full threshold:
ros2 topic echo /load_sensor/bucket_full

# Should be False when weight < 4.75kg (95% of 5kg capacity)
# Should be True when weight >= 4.75kg
```

### Excavator Server Debugging

```bash
# Start just the excavator and load sensor
ros2 run cometbot_control load_sensor &
LOAD_SENSOR_PID=$!
ros2 run cometbot_control excavator_action_server &
EXCAVATOR_PID=$!

# Send a 5 second dig:
ros2 action send_goal /excavator/excavate \
  cometbot_control/action/Excavate \
  "{dig_duration_sec: 5}" \
  --feedback

# Watch load sensor in another terminal:
ros2 topic echo /load_sensor/weight

# Expected: Weight goes 0→5kg in ~5 seconds
# Expected: Action completes with result

# Cleanup:
kill $EXCAVATOR_PID $LOAD_SENSOR_PID
```

### Depositor Server Debugging

```bash
# Start depositor server alone (no load sensor needed):
ros2 run cometbot_control depositor_action_server &
DEPOSITOR_PID=$!

# Send a deposit goal:
ros2 action send_goal /depositor/deposit \
  cometbot_control/action/Deposit \
  "{material_to_deposit_kg: 5.0}" \
  --feedback

# Check logs - should see deposit progress

kill $DEPOSITOR_PID
```

### Mission Orchestrator Debugging

Enable verbose logging:

```python
# Add to mission_orchestrator.py temporarily:
self.get_logger().set_level(rclpy_logging.LoggingSeverity.DEBUG)
```

Or use launch parameter:
```bash
ros2 run cometbot_control mission_orchestrator \
  --ros-args --log-level mission_orchestrator:=DEBUG
```

## Common Issues and Fixes

### Issue: "Failed to send action goal"
```
Cause: Action server not running or not accessible
Fix: 
1. Check ros2 action list shows /excavator/excavate
2. Check node info: ros2 node info /excavator_action_server
3. Restart action server node
```

### Issue: "Action goal rejected"
```
Cause: Server rejected the goal or received invalid goal
Fix:
1. Check goal parameters match action definition
2. Look at server logs for rejection reason
3. Verify goal values are reasonable (e.g., positive numbers)
```

### Issue: "Action times out waiting for result"
```
Cause: Server crashed or got stuck
Fix:
1. Check server logs for error messages
2. Kill and restart the server: pkill -f action_server
3. Verify load sensor is working (if server depends on it)
```

### Issue: "Load sensor publishes but mission doesn't use it"
```
Cause: Mission not subscribed or subscription failing
Fix:
1. Check mission orchestrator logs
2. Verify topic name: ros2 topic echo /load_sensor/weight
3. Check subscription callback in code
```

## Performance Issues

### Slow State Transitions

```bash
# Mission should change states every 2-15 seconds
# Check FSM loop rate:
ros2 stat /fsm/state

# Should show ~2 Hz (500ms period)
# If slower: Might be waiting on action to complete
```

### Actions Taking Too Long

Use debug timing:
```python
# Option 1: Print timestamps
self.get_logger().info(f"Dig complete at {time.monotonic()}")

# Option 2: Reduce simulation times
ros2 launch cometbot_control mission_sim.launch.py \
  dig_rate:=10.0 \
  dig_duration:=1.0
```

### High CPU Usage

```bash
# Check if spinning too fast:
ps aux | grep cometbot

# If process is using >50% CPU:
# 1. One of the callbacks is running too often
# 2. Or doing expensive computation
# 3. Check timer frequencies in code (should be 0.1-2 Hz)
```

## Network/Communication Issues

### Nodes Not Seeing Each Other

```bash
# Check ROS_DOMAIN_ID:
echo $ROS_DOMAIN_ID  # Should be same for all terminals

# Check localhost resolution:
ping localhost
ping 127.0.0.1

# Force localhost only:
export ROS_LOCALHOST_ONLY=1
```

### Action Calls From Different Machines

This setup assumes single machine initially. For multi-machine:

```bash
# Set ROS_DOMAIN_ID and IP on both machines
export ROS_DOMAIN_ID=42
export ROS_RMW_IMPLEMENTATION=rmw_cyclonedds_cpp  # or similar

# Test connectivity:
ros2 daemon stop
ros2 daemon start
ros2 node list  # should eventually show remote nodes
```

## Logs and Error Messages

### Find Detailed Errors
```bash
# Grep for ERROR in a terminal running nodes:
grep -i error

# Or check ROS logs:
~/.ros/log/  # Contains timestamped logs

# View latest:
tail -f ~/.ros/log/latest/*/stdout
```

### Redirect All Output
```bash
# Capture all output to file:
ros2 launch cometbot_control mission_sim.launch.py 2>&1 | tee mission_run.log

# Later: grep mission_run.log for issues
```

## Testing Framework

### Unit Test Template
```bash
# Start just one component:
ros2 run cometbot_control [component_name] &
COMPONENT_PID=$!

# Run tests...

# Cleanup:
kill $COMPONENT_PID
```

### Integration Test
```bash
# Start all components:
ros2 launch cometbot_control mission_sim.launch.py &
LAUNCH_PID=$!

# Run full mission:
# - Wait 60 seconds
# - Check /fsm/state reaches IDLE
# - Check /fsm/material_total >= target

# Cleanup:
kill $LAUNCH_PID
```

## Getting Help

If still stuck:

1. **Check the log file**: `grep ERROR *.log`
2. **Verify basic setup**: `ros2 node list`, `ros2 topic list`
3. **Test one component**: Start load_sensor alone, then add excavator, etc.
4. **Reduce complexity**: Use fast parameters for quicker feedback
5. **Read the code**: The node implementations have comments explaining behavior

## Network Debugging (Advanced)

```bash
# Monitor ROS 2 network traffic:
ros2 daemon stop
RMW_IMPLEMENTATION=rmw_cyclonedds_cpp ddsperf sanity \
  --transport tcp

# This shows if DDS is working properly
```

See [QUICKSTART.md](QUICKSTART.md) and [ACTION_ORCHESTRATION.md](ACTION_ORCHESTRATION.md) for more details.
