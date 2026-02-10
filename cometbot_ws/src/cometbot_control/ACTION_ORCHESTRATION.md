# Action-Based Mission Orchestration Architecture

## Overview

This system replaces simulated subsystems with **action-based orchestration** that enables:
- High-level mission control via ROS Actions
- Realistic sensor feedback (load cell simulation)
- Non-blocking concurrent operations
- Easy transition to hardware control

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Isaac Sim / Teleop                     │
│                    (provides /cmd_vel, /joy)                │
└─────────────────────────┬───────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────┐
│            Mission Orchestrator (FSM)                        │
│  - Coordinates mission phases (navigate, dig, deposit)      │
│  - Monitors load sensor feedback                            │
│  - Sends action goals                                        │
│  - Publishes: /fsm/state, /fsm/material_total              │
└──────────┬─────────────────────────────┬────────────────────┘
           │                             │
           ▼                             ▼
┌──────────────────────┐        ┌───────────────────────┐
│ Excavator            │        │ Depositor             │
│ Action Server        │        │ Action Server         │
│ ─────────────────    │        │ ─────────────────     │
│ Goal: dig_duration   │        │ Goal: material_amount │
│ Result: collected_kg │        │ Result: deposited_kg  │
│ Feedback: %_full     │        │ Feedback: %_complete  │
└──────────┬───────────┘        └───────────┬───────────┘
           │                               │
           └───────────┬───────────────────┘
                       │
                       ▼
              ┌─────────────────────┐
              │  Load Sensor        │
              │  ─────────────────  │
              │ Pub: /weight (kg)   │
              │ Pub: /bucket_full   │
              │                     │
              │ (Simulates load     │
              │  cell + noise)      │
              └─────────────────────┘
```

## Components

### 1. **Mission Orchestrator** (`mission_orchestrator.py`)
High-level state machine that:
- Manages mission phases: STARTUP → NAV_TO_MINE → EXCAVATE → NAV_TO_DEPOSIT → DEPOSIT → NAV_HOME → IDLE
- Sends excavate/deposit action goals
- Monitors load sensor for bucket status
- Publishes `/fsm/state` and `/fsm/material_total` for visualization

**Topics:**
- Subscribe: `/cmd_vel`, `/load_sensor/weight`, `/load_sensor/bucket_full`
- Publish: `/fsm/state`, `/fsm/material_total`
- Actions: Calls `/excavator/excavate` and `/depositor/deposit`

**Parameters:**
- `dig_duration_sec`: How long to excavate (default: 30s)
- `target_total_material_kg`: Mission success target (default: 10kg)

### 2. **Excavator Action Server** (`excavator_action_server.py`)
Handles material excavation:
- Accepts `/excavator/excavate` action calls
- Simulates digging with configurable collection rate
- Publishes feedback: bucket fill percentage, time remaining
- Stops early when bucket is full

**Action: `/excavator/excavate`**
- Goal: `dig_duration_sec` (seconds to dig)
- Result: `material_collected_kg`, `success`
- Feedback: `bucket_fill_percentage`, `estimated_time_remaining`

**Parameters:**
- `dig_rate_kg_per_sec`: Collection rate (default: 1.0 kg/s)
- `bucket_capacity_kg`: Max bucket size (default: 5.0 kg)

### 3. **Depositor Action Server** (`depositor_action_server.py`)
Handles material deposition:
- Accepts `/depositor/deposit` action calls
- Simulates dumping with configurable deposit rate
- Publishes feedback: deposit progress, time remaining
- Has safety timeout

**Action: `/depositor/deposit`**
- Goal: `material_to_deposit_kg` (amount to dump)
- Result: `material_deposited_kg`, `success`
- Feedback: `deposit_progress_percentage`, `estimated_time_remaining`

**Parameters:**
- `deposit_rate_kg_per_sec`: Dump rate (default: 1.5 kg/s)
- `max_deposit_time_sec`: Safety timeout (default: 10s)

### 4. **Load Sensor** (`sensors/load_sensor.py`)
Simulates load cell that measures bucket weight:
- Publishes `/load_sensor/weight` continuously (Float32, kg)
- Publishes `/load_sensor/bucket_full` status bool
- Adds configurable Gaussian noise for realism
- Can be commanded to empty bucket (for future integration with depositor)

**Topics:**
- Publish: `/load_sensor/weight`, `/load_sensor/bucket_full`

**Parameters:**
- `bucket_capacity_kg`: Max weight (default: 5.0 kg)
- `sensor_noise_sigma`: Noise standard deviation (default: 0.1 kg)
- `publish_rate_hz`: Update frequency (default: 10 Hz)

## Running the System (Simulation)

### Build the package
```bash
cd cometbot_ws
colcon build --packages-select cometbot_control
source install/setup.bash
```

### Terminal 1: Load Sensor
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

### Terminal 4: Mission Orchestrator
```bash
ros2 run cometbot_control mission_orchestrator
```

### Terminal 5: Monitor the mission
```bash
# Watch FSM state transitions
ros2 topic echo /fsm/state

# Watch total material collected
ros2 topic echo /fsm/material_total

# Watch load sensor
ros2 topic echo /load_sensor/weight
ros2 topic echo /load_sensor/bucket_full

# View action calls (in separate terminals)
# Excavator actions:
ros2 action send_goal /excavator/excavate cometbot_control/action/Excavate "{dig_duration_sec: 30}"

# Depositor actions:
ros2 action send_goal /depositor/deposit cometbot_control/action/Deposit "{material_to_deposit_kg: 5.0}"
```

## Data Flow Example

```
Mission Orchestrator:
1. [STARTUP] → Set state to NAV_TO_MINE
2. [NAV_TO_MINE] → Wait 2s (simulated navigation)
3. [EXCAVATE] → Send excavate action goal (dig_duration=30s)
   
Excavator Server:
   → Receives goal, starts digging
   → Load sensor publishes: 0kg → 5kg (over 5 seconds)
   → Publishes feedback: 0% → 100% bucket_fill
   
Mission Orchestrator:
4. [EXCAVATE] → Receives feedback, waits for action completion
5. Excavate action complete: Result (material_collected_kg=5.0, success=true)
6. Total material += 5.0kg
7. [NAV_TO_DEPOSIT] → Wait 2s (simulated navigation)
8. [DEPOSIT] → Send deposit action goal (material_to_deposit_kg=5.0)

Depositor Server:
   → Receives goal, starts depositing
   → Publishes feedback: 0% → 100% deposit_progress
   
Mission Orchestrator:
9. [DEPOSIT] → Receives feedback, waits for action completion
10. Deposit action complete: Result (material_deposited_kg=5.0, success=true)
11. Check if total >= target (5.0 >= 10.0? No)
12. [NAV_TO_MINE] → Cycle repeats
```

## Key Design Decisions

### 1. **Actions vs Topics/Services**
- **Why Actions?** They provide:
  - Built-in cancellation support
  - Feedback during long operations
  - Non-blocking async pattern
  - Clean state machine integration
  - Preemption handling

### 2. **Separate Load Sensor**
- Independent publisher allows real sensor integration later
- Mission logic decoupled from sensor details
- Easy to swap with actual hardware ROS driver

### 3. **Non-blocking Simulation**
- Excavator/Depositor: Simulate time-based material collection
- FSM: Drives state machine via timers, not blocking waits
- Easy to test mission logic without hardware

### 4. **Parameter-Driven**
- All timing and rates configurable via ROS parameters
- Speeds up testing (dig faster in sim, normal on hardware)
- Example: `ros2 run ... --ros-args -p dig_rate_kg_per_sec:=10.0`

## Extending to Hardware

To integrate with actual hardware:

1. **Load Sensor**: Replace with real ROS driver that publishes same topics
   - Example: connect to Arduino/microcontroller publishing `/load_sensor/weight`

2. **Excavator**: Replace action server with hardware bridge
   - Connect to servo/motor controller
   - Read actual bucket weight instead of simulating
   - Keep same action interface!

3. **Depositor**: Same as excavator
   - Command real dump mechanism (servo, door, etc.)

4. **Navigation**: Replace simulated 2s wait with actual autonomous nav
   ```python
   # Instead of:
   if time.monotonic() - self._nav_start_time > 2.0:
   
   # Use:
   nav_goal = self.send_nav_action(target_pose)
   ```

## Testing Mission Logic

Since physics is simulated, you can:
- Speed up/slow down excavation rates
- Test edge cases (bucket overflow, stuck operations)
- Modify mission phases without changing hardware dependencies
- Unit test action servers independently

Example fast test:
```bash
ros2 run cometbot_control mission_orchestrator --ros-args \
  -p dig_duration_sec:=5.0 \
  -p target_total_material_kg:=2.0 \
  excavator_action_server --ros-args \
  -p dig_rate_kg_per_sec:=10.0 \
  depositor_action_server --ros-args \
  -p deposit_rate_kg_per_sec:=10.0
```

## Visualization

For Isaac Sim integration, you can:
1. Subscribe to `/fsm/state` to trigger sim animations (bucket fill, dump, drive)
2. Monitor `/fsm/material_total` for mission progress
3. Publish `Joy` messages to trigger teleop
4. Map `/cmd_vel` to robot movement in sim

## Next Steps

1. **Integrate Load Sensor with Excavator**: Have excavator server receive load sensor updates
2. **Add Navigation Action**: Create autonomous navigation action server
3. **Hardware Bridge**: Create CAN/serial bridge from action goals to microROS ESP32
4. **Visual Monitoring**: RViz plugin or web dashboard to show mission progress
