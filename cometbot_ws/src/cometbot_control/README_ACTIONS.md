# Cometbot ROS 2 Control - Action-Based Orchestration

High-level mission orchestration for the Lunabotics competition using ROS 2 Actions.

## What's New

This system replaces simulated subsystems with **action-based orchestration**, enabling:

- 🎯 **Structured Communication**: ROS 2 Actions for excavator/depositor instead of string commands
- 📊 **Rich Feedback**: Real-time progress updates during long operations
- 🔄 **Non-blocking Control**: Python asyncio-compatible action clients for smooth FSM operation
- 🧪 **Easy Simulation**: Parameterized excavation/deposition rates for fast testing
- 🔌 **Hardware-Ready**: Same Python interfaces work with hardware servers

## Quick Start

### Installation
```bash
cd cometbot_ws
colcon build --packages-select cometbot_control
source install/setup.bash
```

### Run the Full Mission (Simulation)
```bash
ros2 launch cometbot_control mission_sim.launch.py
```

See [QUICKSTART.md](QUICKSTART.md) for detailed instructions.

## System Components

| Component | Role | Status |
|-----------|------|--------|
| **Mission Orchestrator** | High-level FSM that coordinates excavation/deposition cycles | ✅ Python |
| **Excavator Action Server** | Handles `/excavator/excavate` action with simulated digging | ✅ Python |
| **Depositor Action Server** | Handles `/depositor/deposit` action with simulated dumping | ✅ Python |
| **Load Sensor** | Publishes bucket weight via `/load_sensor/weight` topic | ✅ Python |
| **Drive Base Control** | Receives `/cmd_vel` from mission FSM (through teleop in sim) | ✅ C++ (microROS) |

## Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get it running in 5 minutes
- **[ACTION_ORCHESTRATION.md](ACTION_ORCHESTRATION.md)** - Detailed component documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System design and data flow

## Core Concepts

### ROS 2 Actions
Instead of commands being simple strings or booleans, they're now:
- **Goals**: What the server should do
- **Results**: What was accomplished
- **Feedback**: Progress updates during execution

```python
# Instead of: pub.publish(String("start_dig"))
# Now:
goal = Excavate.Goal()
goal.dig_duration_sec = 30.0
handle = await excavate_client.send_goal_async(goal)
result = await handle.get_result_async()
print(f"Collected {result.material_collected_kg}kg")
```

### Mission Phases

```
STARTUP
   ↓
NAV_TO_MINE (2s simulated)
   ↓
EXCAVATE (action-based)
   ├─ Sends: Excavate.Goal(dig_duration=30s)
   ├─ Monitors: Load sensor feedback
   ├─ Stops early if bucket full
   ↓ (when complete)
NAV_TO_DEPOSIT (2s simulated)
   ↓
DEPOSIT (action-based)
   ├─ Sends: Deposit.Goal(material=5kg)
   ├─ Waits for completion
   ↓ (when complete)
Check: total_material >= target?
   ├─ No → back to NAV_TO_MINE
   ├─ Yes → NAV_HOME → IDLE
   ↓ (mission complete)
```

## File Structure

```
cometbot_control/
├── action/                           # ROS action definitions
│   ├── Excavate.action              # Excavation action
│   └── Deposit.action               # Deposition action
│
├── cometbot_control/
│   ├── mission_orchestrator.py      # Main FSM (uses actions)
│   ├── excavator_action_server.py   # Excavator implementation
│   ├── depositor_action_server.py   # Depositor implementation
│   ├── action_client_example.py     # Example action usage
│   │
│   └── sensors/
│       └── load_sensor.py           # Load cell simulation
│
├── launch/
│   └── mission_sim.launch.py        # Single command to start all
│
├── QUICKSTART.md                     # Get running in 5 mins
├── ACTION_ORCHESTRATION.md          # Full technical docs
└── ARCHITECTURE.md                  # System design details
```

## Running Individual Components

```bash
# Terminal 1: Load sensor (publishes bucket weight)
ros2 run cometbot_control load_sensor

# Terminal 2: Action server for excavator
ros2 run cometbot_control excavator_action_server

# Terminal 3: Action server for depositor  
ros2 run cometbot_control depositor_action_server

# Terminal 4: Mission orchestrator (FSM)
ros2 run cometbot_control mission_orchestrator

# Terminal 5: Monitor progress
ros2 topic echo /fsm/state
ros2 topic echo /fsm/material_total
```

Or use the launch file to start everything at once:

```bash
ros2 launch cometbot_control mission_sim.launch.py
```

## Testing Actions Manually

```bash
# Send a 30-second dig command
ros2 action send_goal /excavator/excavate \
  cometbot_control/action/Excavate \
  "{dig_duration_sec: 30}"

# Send a 5kg deposit command
ros2 action send_goal /depositor/deposit \
  cometbot_control/action/Deposit \
  "{material_to_deposit_kg: 5.0}"
```

## Custom Parameters

Speed up testing with custom rates:

```bash
ros2 launch cometbot_control mission_sim.launch.py \
  dig_rate:=5.0 \              # 5x faster excavation
  deposit_rate:=5.0 \          # 5x faster deposit
  dig_duration:=5.0 \          # Shorter dig time
  target_material:=2.0         # Smaller target for quick test
```

Mission completes in ~10 seconds instead of 2+ minutes.

## Integration with Isaac Sim

For joystick input from Isaac Sim in simulation:

1. **Joystick Input**
   - Isaac Sim publishes `/joy` messages
   - `teleop_publisher` converts to `/cmd_vel`

2. **Visual Feedback**
   - Subscribe to `/fsm/state` for animation triggers
   - Subscribe to `/fsm/material_total` for progress display
   - Subscribe to `/load_sensor/weight` for bucket visualization

3. **Complete Loop**
   ```
   Isaac Sim (Joystick) → teleop → /cmd_vel
   
   Mission Orchestrator ← /cmd_vel (for future nav integration)
                        ← /load_sensor/* (simulated feedback)
   
   Action Servers (Excavator, Depositor)
   
   Isaac Sim (animates based on /fsm/state)
   ```

## Next: Hardware Integration

To use with real hardware:

1. **Load Sensor**: Replace `load_sensor.py` with real ROS driver
2. **Excavator Motor**: Replace action server with CAN/motor control
3. **Depositor Motor**: Same as excavator
4. **Navigation**: Add autonomous navigation action server

**Key Point**: The mission orchestrator interface doesn't change - it continues to send the same action goals!

## Building the Package

The package generates ROS 2 action interfaces from `.action` files. When you build:

```bash
colcon build --packages-select cometbot_control
```

It automatically generates Python message classes:
- `cometbot_control.action.Excavate`
- `cometbot_control.action.Deposit`

These are used by all the action servers and clients.

## Troubleshooting

### "Action server not available"
- Check that action servers are running: `ros2 action list`
- Make sure you sourced setup: `source install/setup.bash`

### "Wait, where's the Docker stuff?"
- Old subsystems are archived (see git history)
- New approach doesn't need Docker for testing
- Still using same Docker setup for deployed system

### "How do I know it's working?"
- Check nodes: `ros2 node list` (should show 4 nodes)
- Check topics: `ros2 topic list` (should show ~6 topics)
- Watch FSM state: `ros2 topic echo /fsm/state` (transitions every few seconds)
- Watch material total: `ros2 topic echo /fsm/material_total` (increases by 5kg every ~15s)

## Performance

- **State machine loop rate**: 2 Hz (500ms)
- **Load sensor update rate**: 10 Hz (100ms)
- **Action feedback rate**: 10 Hz (100ms)
- **Typical mission cycle**: ~15 seconds per excavate+deposit loop
- **Full mission (10kg target)**: ~30-60 seconds depending on parameters

## References

- **ROS 2 Actions**: https://docs.ros.org/en/humble/Concepts/Basic/About_Actions.html
- **ROS 2 Humble**: https://docs.ros.org/en/humble/
- **Lunabotics Competition**: https://www.seds.org/lunabotics/

## Contributing

See original project structure - this maintains compatibility with:
- Existing teleop/joystick system
- Future C++ microROS bridge
- Isaac Sim integration

## License

Apache 2.0 (same as original package)

---

**Need help?** Start with [QUICKSTART.md](QUICKSTART.md) for immediate hands-on guidance.
