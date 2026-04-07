# Action-Based Orchestration: What's Included

## Summary of Changes

This deliverable replaces the simulated subsystem approach with a **ROS 2 Action-based orchestration system** for high-level mission control. Everything is Python and designed for simulation testing.

## New Files Created

### Action Definitions
- `action/Excavate.action` - Defines excavation action interface
- `action/Deposit.action` - Defines deposition action interface

### Python Nodes
- `cometbot_control/mission_orchestrator.py` - High-level FSM that coordinates the mission
- `cometbot_control/excavator_action_server.py` - Excavator action server implementation
- `cometbot_control/depositor_action_server.py` - Depositor action server implementation
- `cometbot_control/sensors/load_sensor.py` - Load cell simulation
- `cometbot_control/sensors/__init__.py` - Package marker
- `cometbot_control/action_client_example.py` - Example showing how to call actions

### Launch Files
- `launch/mission_sim.launch.py` - Single command to start all components

### Documentation
- `README_ACTIONS.md` - Overview of the new system
- `QUICKSTART.md` - 5-minute getting started guide
- `ACTION_ORCHESTRATION.md` - Detailed technical documentation
- `ARCHITECTURE.md` - System design and data flow diagrams
- `DEBUGGING.md` - Troubleshooting guide

### Configuration Updates
- `package.xml` - Updated with action dependencies and launch file registration
- `setup.py` - Updated with new node entry points

## Key Architecture

```
Mission Orchestrator (FSM)
  ├─ Sends: Excavate.Goal, Deposit.Goal
  ├─ Receives: Results + Feedback
  └─ Publishes: /fsm/state, /fsm/material_total

Excavator Action Server
  ├─ Executes: Excavate action
  ├─ Reads: /load_sensor/weight
  └─ Publishes: Feedback during excavation

Depositor Action Server
  ├─ Executes: Deposit action
  └─ Publishes: Feedback during deposition

Load Sensor
  └─ Publishes: /load_sensor/weight, /load_sensor/bucket_full
```

## How to Use

### Option 1: Start Everything (Recommended)
```bash
# One command to start all components
ros2 launch cometbot_control mission_sim.launch.py

# Watch it in another terminal:
ros2 topic echo /fsm/state
ros2 topic echo /fsm/material_total
```

### Option 2: Start Components Individually
```bash
# Terminal 1: Load sensor
ros2 run cometbot_control load_sensor

# Terminal 2: Excavator action server
ros2 run cometbot_control excavator_action_server

# Terminal 3: Depositor action server
ros2 run cometbot_control depositor_action_server

# Terminal 4: Mission orchestrator
ros2 run cometbot_control mission_orchestrator

# Terminal 5: Monitor
ros2 topic echo /fsm/state
```

## What's Different vs Old Approach

| Aspect | Old | New |
|--------|-----|-----|
| Subsystems | Docker containers with simulated state machines | ROS 2 action servers |
| Communication | String topics (`/cmd`) | Structured action goals/results/feedback |
| Mission Logic | Hardcoded in FSM with blocking waits | Clean state machine using action clients |
| Sensor Integration | Mocked in subsystem | Separate load sensor node |
| Testing | Required Docker | Pure ROS 2 testing |
| Hardware Integration | Would require rewriting subsystems | Replace action server, keep interface |

## Key Features

✅ **Action-based Communication**: Rich structured goals/results instead of string commands  
✅ **Non-blocking Control**: FSM uses async action clients, no blocking waits  
✅ **Real Feedback**: Progress updates from excavator/depositor during operations  
✅ **Load Sensor Integration**: Load cell simulation provides realistic bucket weight  
✅ **Parameterized Simulation**: Change dig rates, times for quick testing  
✅ **Easy Testing**: Test individual action servers without full mission  
✅ **Hardware-Ready**: Interface stays same when integrating real hardware  
✅ **Observable**: Rich topic publishing for monitoring and visualization  

## Example Mission Flow

```
[Time 0s]   Mission starts → NAV_TO_MINE (simulated)
[Time 2s]   → EXCAVATE (action-based)
            Send: Excavate.Goal(dig_duration_sec=30)
[Time 7s]   Load sensor reaches 5kg (bucket full)
            Action completes early → NAV_TO_DEPOSIT
[Time 9s]   → DEPOSIT (action-based)
            Send: Deposit.Goal(material_to_deposit_kg=5.0)
[Time 13s]  Deposit complete → back to NAV_TO_MINE
[Time 26s]  Total reached 10kg → NAV_HOME → IDLE
```

## Extension Points

1. **Navigation**: Add autonomous navigation action server
2. **Load Sensor**: Swap simulated for real ROS driver
3. **Excavator Motor**: Add CAN control via SPARK MAX
4. **Depositor Motor**: Add servo/door control
5. **Logging**: Subscribe and log all state changes

All without changing the mission orchestrator interface!

## Testing Parameters

Speed up testing:
```bash
ros2 launch cometbot_control mission_sim.launch.py \
  dig_rate:=10.0 \           # 10x faster digging
  deposit_rate:=10.0 \       # 10x faster deposit
  dig_duration:=1.0 \        # 1 second (vs 30s)
  target_material:=2.0       # 2kg target (vs 10kg)

# Full mission completes in ~5 seconds
```

## Integration with Isaac Sim

For your existing joystick/simulation setup:

```
Isaac Sim (Joystick)
   ↓ (/joy topic)
TeleopPublisher
   ↓ (/cmd_vel topic)
Mission Orchestrator (FSM)
   ├─ Excavator Action Server (simulated digging)
   ├─ Depositor Action Server (simulated dumping)
   └─ Load Sensor (simulated bucket weight)
   ↓ (/fsm/state, /load_sensor/weight topics)
Isaac Sim (visualized/animated)
```

## Build & Install

```bash
cd ~/cometbot_ws
colcon build --packages-select cometbot_control
source install/setup.bash
```

The build automatically generates Python action interfaces from the `.action` files.

## What's NOT Changed

- Teleop/joystick system (still works)
- C++ microROS ESP32 code (unchanged)
- Drive base (/cmd_vel) control (unchanged)
- Isaac Sim integration (enhanced)
- Overall package structure (compatible)

## Documentation Roadmap

1. **Start here**: [QUICKSTART.md](QUICKSTART.md)
2. **Deep dive**: [ACTION_ORCHESTRATION.md](ACTION_ORCHESTRATION.md)
3. **System design**: [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Troubleshoot**: [DEBUGGING.md](DEBUGGING.md)
5. **Overview**: [README_ACTIONS.md](README_ACTIONS.md)

## Next Steps

1. **Build and test**: Follow QUICKSTART.md
2. **Monitor mission**: Watch /fsm/state and /fsm/material_total
3. **Customize**: Adjust parameters for your testing needs
4. **Integrate hardware**: Replace action servers as needed
5. **Add features**: Navigation, safety checks, logging

## Files Modified

- `package.xml` - Added action dependencies, data files
- `setup.py` - Added new console_scripts entry points

## Code Quality

- All Python nodes use type hints
- Comprehensive docstrings on all functions
- Structured error handling with try/except
- Thread-safe action server implementations
- Configurable via ROS parameters

## Performance

- State machine loop: 2 Hz (500ms)
- Action feedback: 10 Hz (100ms)
- Typical mission: ~15-30s per cycle
- Full 10kg mission: ~1 minute simulated time

---

**Next**: See [QUICKSTART.md](QUICKSTART.md) to get it running!
