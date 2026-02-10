# Quick Start: Action-Based Mission Orchestration

## Build & Setup

```bash
cd ~/cometbot_ws
colcon build --packages-select cometbot_control
source install/setup.bash
```

## Option 1: Run All Components (Recommended)

Single command to start the full mission in simulation:

```bash
ros2 launch cometbot_control mission_sim.launch.py
```

With custom parameters for faster sim:

```bash
ros2 launch cometbot_control mission_sim.launch.py \
  dig_rate:=5.0 \
  deposit_rate:=5.0 \
  dig_duration:=10.0 \
  target_material:=2.0
```

## Option 2: Run Components Individually

Great for debugging individual components.

### Terminal 1: Load Sensor (required by excavator)
```bash
ros2 run cometbot_control load_sensor
```

### Terminal 2: Excavator Action Server
```bash
ros2 run cometbot_control excavator_action_server
```

### Terminal 3: Depositor Action Server
```bash
ros2 run cometbot_control depositor_action_server
```

### Terminal 4: Mission Orchestrator (the FSM)
```bash
ros2 run cometbot_control mission_orchestrator
```

### Terminal 5: Monitor Mission Progress
```bash
# Watch state transitions
ros2 topic echo /fsm/state

# Watch total material
ros2 topic echo /fsm/material_total --rate=1

# Watch load sensor
ros2 topic echo /load_sensor/weight --rate=1
```

## Testing Individual Actions

With all servers running, you can manually test actions:

### Test Excavation (30s dig)
```bash
ros2 action send_goal /excavator/excavate \
  cometbot_control/action/Excavate \
  "{dig_duration_sec: 30}"
```

### Test Deposit (5kg material)
```bash
ros2 action send_goal /depositor/deposit \
  cometbot_control/action/Deposit \
  "{material_to_deposit_kg: 5.0}"
```

### Monitor Action Progress
```bash
# In separate terminal, watch load increase during dig
ros2 topic echo /load_sensor/weight --rate=5

# Or echo bucket_full status
ros2 topic echo /load_sensor/bucket_full
```

## Expected Mission Flow (with defaults)

```
[0s]  Mission starts → NAV_TO_MINE
[2s]  → EXCAVATE (sends 30s dig action)
[7s]  Bucket fills to 5kg (load sensor hits capacity)
[7s]  Excavation completes → NAV_TO_DEPOSIT
[9s]  → DEPOSIT (sends 5kg deposit action)
[13s] Deposit completes → repeat cycle
[26s] Total material >= 10kg → NAV_HOME → IDLE
```

## Debugging

### Check if all nodes are running
```bash
ros2 node list
```
Should show:
- /load_sensor
- /excavator_action_server
- /depositor_action_server
- /mission_orchestrator

### Check topics
```bash
ros2 topic list
```
Should show:
- /fsm/material_total
- /fsm/state
- /load_sensor/bucket_full
- /load_sensor/weight

### View ros logs
```bash
# Follow logs from mission orchestrator
ros2 launch cometbot_control mission_sim.launch.py 2>&1 | grep mission_orchestrator
```

### Test with verbose logging
Each node has built-in logging. Look for:
- `[mission_orchestrator]` - state transitions, action sends
- `[excavator_action_server]` - dig progress
- `[depositor_action_server]` - deposit progress
- `[load_sensor]` - weight updates

## Common Issues

### "Action server not available"
- Make sure excavator_action_server and depositor_action_server are running
- Check: `ros2 action list`

### Weight not updating
- Ensure load_sensor is running
- Check: `ros2 topic echo /load_sensor/weight`

### No state changes
- Make sure mission_orchestrator is running
- Check: `ros2 node list | grep mission`
- View logs to see what state it's stuck in

### Actions not completing
- Check timeout values in node parameters
- Verify action servers are responsive: `ros2 action list -t`

## Next Steps

1. **Integrate Isaac Sim**: Have simulator subscribe to `/fsm/state` for animations
2. **Add Navigation**: Create autonomous navigation action server
3. **Monitor Dashboard**: Create RViz/web dashboard for mission visualization
4. **Hardware Integration**: Replace load sensor with real hardware ROS driver

## Files Reference

- **Action definitions**: `action/Excavate.action`, `action/Deposit.action`
- **Mission FSM**: `cometbot_control/mission_orchestrator.py`
- **Server implementations**: 
  - `cometbot_control/excavator_action_server.py`
  - `cometbot_control/depositor_action_server.py`
- **Sensor simulation**: `cometbot_control/sensors/load_sensor.py`
- **Launch file**: `launch/mission_sim.launch.py`
- **Full documentation**: `ACTION_ORCHESTRATION.md`
