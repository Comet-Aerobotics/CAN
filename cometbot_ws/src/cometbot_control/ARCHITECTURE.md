# Action-Based Orchestration: Architecture Summary

## System Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          MISSION ORCHESTRATOR (FSM)                      │
│                                                                            │
│  States: STARTUP → NAV_TO_MINE → EXCAVATE → NAV_TO_DEPOSIT →            │
│          DEPOSIT → NAV_HOME → IDLE                                        │
│                                                                            │
│  Responsibilities:                                                         │
│  • Coordinate mission phases                                              │
│  • Send action goals to subsystems                                        │
│  • Monitor load sensor feedback                                           │
│  • Track total material collected                                         │
└──────────────────┬─────────────────────────────────────────┬──────────────┘
                   │                                         │
        ┌──────────▼────────────┐              ┌────────────▼──────────┐
        │ EXCAVATOR ACTION SERVER│              │ DEPOSITOR ACTION SERVER│
        │                        │              │                       │
        │ Action: /excavator/...│              │ Action: /depositor/...│
        │                        │              │                       │
        │ Goal: dig_duration_sec │              │ Goal: material_to_dep │
        │ Result: kg_collected   │              │ Result: kg_deposited  │
        │ Feedback: %_fill       │              │ Feedback: %_complete  │
        │                        │              │                       │
        │ • Simulates digging    │              │ • Simulates dumping    │
        │ • Reads load sensor    │              │ • Publishes progress   │
        │ • Early stop if full   │              │ • Safety timeout       │
        └──────────┬─────────────┘              └────────────┬──────────┘
                   │                                        │
                   └────────────────┬─────────────────────┘
                                    │
                                    │ Subscribe to
                                    │ /load_sensor/weight
                                    │ (both servers read)
                                    │
                                    ▼
                            ┌───────────────────────┐
                            │   LOAD SENSOR         │
                            │                       │
                            │ Publishes:            │
                            │ • /load_sensor/weight │
                            │ • /load_sensor/bucket_├─ (Simulates load cell)
                            │                       │
                            │ Features:             │
                            │ • Gaussian noise      │
                            │ • 10 Hz publish rate  │
                            │ • Bucket capacity     │
                            │   thresholding        │
                            └───────────────────────┘
```

## Key Features vs Old Approach

| Feature | Old Approach | New Approach |
|---------|-------------|--------------|
| **Subsystem Control** | Docker containers with simulated state machines | ROS 2 Action Servers with async operations |
| **Communication** | String topics (/cmd) | Structured Action goals/results/feedback |
| **Feedback** | Boolean status | Rich feedback during operations |
| **Real-time Monitoring** | Simulated state only | Load cell feedback integration |
| **Blocking** | Potentially blocking FSM | Non-blocking action clients |
| **Testing** | Hard to test without full Docker setup | Easy to test individual actions |
| **Hardware Integration** | Requires subsystem rewrite | Swap server implementation, keep interface |

## Data Flow: Complete Mission Cycle

### Phase 1: Navigation to Mine (2s simulated)
```
[FSM] State: NAV_TO_MINE
├─ Wait 2 seconds (simulates drive)
└─ Transition to EXCAVATE
```

### Phase 2: Excavation (5s actual, ~5kg collected)
```
[FSM] State: EXCAVATE
├─ Send goal: Excavate.Goal(dig_duration_sec=30)
│
[Excavator Server]
├─ Start digging simulation
├─ Publish: 0→100% bucket_fill
│
[Load Sensor]
├─ Weight increases: 0→5kg
│
[Excavator Server (watching load sensor)]
├─ Detects bucket full (5kg >= capacity 5kg)
├─ Stop early (goal=30s but stop at ~5s)
├─ Return: Result(material_collected_kg=5.0, success=true)
│
[FSM] Receives result
├─ Update total_material_collected += 5.0kg
└─ Transition to NAV_TO_DEPOSIT
```

### Phase 3: Navigation to Dump (2s simulated)
```
[FSM] State: NAV_TO_DEPOSIT
├─ Wait 2 seconds
└─ Transition to DEPOSIT
```

### Phase 4: Deposition (3-4s actual, 5kg dumped)
```
[FSM] State: DEPOSIT
├─ Send goal: Deposit.Goal(material_to_deposit_kg=5.0)
│
[Depositor Server]
├─ Start dump simulation
├─ Publish: 0→100% deposit_progress
├─ Return: Result(material_deposited_kg=5.0, success=true)
│
[FSM] Receives result
├─ Check if total >= target (5.0 >= 10.0? No)
├─ Reset bucket (via load sensor)
└─ Transition back to NAV_TO_MINE (for next cycle)
```

### Cycle Repeats
```
Total collected after 2 cycles: 5kg + 5kg = 10kg ≥ target_10kg
└─ Transition to NAV_HOME → IDLE (mission complete)
```

## Component Interfaces

### Load Sensor Output
```
Topic: /load_sensor/weight (Float32)
┌──────────────────┐
│ 0.0 kg         0│
├──────────────────┤
│ 1.5 kg      XXXX│  (with noise)
├──────────────────┤
│ 3.2 kg   XXXXXXX│
├──────────────────┤
│ 5.0 kg XXXXXXXXX│  (full)
└──────────────────┘

Topic: /load_sensor/bucket_full (Bool)
┌──────────┐
│ False  ##│
├──────────┤
│ True   ##│  (when >= 95% capacity)
└──────────┘
```

### Excavator Action
```
Goal:
├─ dig_duration_sec: 30.0 (how long to dig)

Feedback (published during dig):
├─ bucket_fill_percentage: 47.3
└─ estimated_time_remaining: 15

Result (when done):
├─ material_collected_kg: 5.0
└─ success: true
```

### Depositor Action
```
Goal:
├─ material_to_deposit_kg: 5.0 (how much to dump)

Feedback (published during deposit):
├─ deposit_progress_percentage: 73.5
└─ estimated_time_remaining: 2

Result (when done):
├─ material_deposited_kg: 5.0
└─ success: true
```

### FSM Publications
```
Topic: /fsm/state (String)
├─ "STARTUP"
├─ "NAV_TO_MINE"
├─ "EXCAVATE"
├─ "NAV_TO_DEPOSIT"
├─ "DEPOSIT"
├─ "NAV_HOME"
└─ "IDLE"

Topic: /fsm/material_total (Float32)
├─ 0.0 kg
├─ 5.0 kg (after first excavation)
├─ 10.0 kg (after second excavation, mission complete)
```

## Testing Levels

### Unit Test: Single Action Server
```bash
# Start just excavator server
ros2 run cometbot_control excavator_action_server &
EXCAVATOR_PID=$!

# Send test goal (manual or via action_client_example.py)
ros2 action send_goal /excavator/excavate \
  cometbot_control/action/Excavate \
  "{dig_duration_sec: 10}"

# Verify
# - Action completes successfully
# - Result has correct material_collected_kg
# - Feedback was published

kill $EXCAVATOR_PID
```

### Integration Test: Full Mission
```bash
# Start all components
ros2 launch cometbot_control mission_sim.launch.py

# Monitor for ~30 seconds
# - FSM transitions through states
# - Load sensor weight increases during excavation
# - Material total increases
# - Mission reaches IDLE state

# Stop (Ctrl+C)
```

### Stress Test: Fast Iteration
```bash
# Override simulation rates for quick testing
ros2 launch cometbot_control mission_sim.launch.py \
  dig_rate:=20.0 \           # 20kg/s (vs 1kg/s)
  deposit_rate:=20.0 \       # 20kg/s (vs 1.5kg/s)
  dig_duration:=1.0 \        # 1s dig (vs 30s)
  target_material:=2.0       # 2kg target (vs 10kg)

# Mission should complete in ~5 seconds vs 2+ minutes
```

## Extension Points

### 1. **Add Navigation Actions**
```python
# In mission_orchestrator.py, replace NAV_TO_MINE timing with:
self.nav_client = ActionClient(self, NavigateToGoal, '/navigate_to')
goal = NavigateToGoal.Goal()
goal.target_pose = Pose(position=Point(x=10.0, y=0.0))
result = await self.send_action_goal(self.nav_client, goal)
```

### 2. **Add Hardware Load Sensor**
```python
# In load_sensor.py, replace simulated weight with:
# - Real serial read from Arduino
# - ROS driver for load cell sensor
# - Just publish same /load_sensor/weight topic

# Rest of system unchanged!
```

### 3. **Add Actual CAN Motor Control**
```python
# In excavator_action_server.py, replace simulation with:
# - Send CAN commands to SPARK MAX motors
# - Read actual bucket position/current
# - Publish real control feedback

# Keep same action interface for FSM!
```

### 4. **Add Telemetry/Logging**
```python
# Subscribe to all topics and log to database
# - mission state changes
# - material amounts
# - action durations
# - error conditions

# No code changes to orchestration needed
```

## Performance Characteristics

| Metric | Simulated | Notes |
|--------|-----------|-------|
| Mission cycle time | ~15 seconds | (2s nav + 5s dig + 2s nav + 4s deposit) |
| State update rate | 2 Hz | (500ms FSM loop) |
| Load sensor rate | 10 Hz | (100ms publish) |
| Action feedback rate | 10 Hz | (100ms in action servers) |
| Typical mission duration | 30-60 sec | (depends on target_material) |

## Summary

This action-based architecture provides:
- ✅ **Clean separation** between mission logic and subsystem implementation
- ✅ **Testable components** - each can be tested independently
- ✅ **Simulation-ready** - fast, parameterized simulation for testing
- ✅ **Hardware-compatible** - same interface works with real hardware
- ✅ **Scalable** - easy to add navigation, sensors, safety checks
- ✅ **Observable** - rich feedback and status topics for monitoring
