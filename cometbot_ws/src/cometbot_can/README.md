# cometbot_can: SPARK MAX control from the mini PC (SocketCAN)

This package replaces the ESP32 firmware in `microROS_test/`. It does the same
job: listen to ROS topics, turn them into SPARK MAX CAN frames, keep the
heartbeat going, and report motor data back. The difference is that it runs as
a normal ROS 2 node on the mini PC and talks to the CAN bus through a USB-CAN
adapter (like a CANable).

```
OLD:  ROS topics -> micro-ROS over USB serial -> ESP32 -> MCP2515 chip -> CAN bus -> SPARK MAXs
NEW:  ROS topics -> can_bridge node (mini PC) -> USB-CAN adapter (can0) -> CAN bus -> SPARK MAXs
```

The ESP32, micro-ROS, the micro-ROS agent and the MCP2515 all drop out.

## Which new file replaces which old file

| Old (microROS_test/) | New (cometbot_can/) | Notes |
|---|---|---|
| `src/main.cpp` | `src/can_bridge_node.cpp` | Same topics, same timers (25 / 10 / 250 ms), same heartbeat logic |
| `lib/Comet_CAN_Common/` | `include/cometbot_can/spark_protocol.hpp` | Same CAN IDs and numbers |
| `lib/SPARK_MAX/` | `src/spark_max.cpp` | Builds and parses frames; no longer sends anything itself |
| `lib/Comet_CAN_Helper/` + `MCP_CAN` | `src/socket_can.cpp` | Opens `can0`, sends and receives frames |
| `extra_packages/custom_messages/` | `msg/` | Same fields, now `cometbot_can/msg/...` |
| hard-coded CAN IDs and limits | `config/can_bridge.yaml` | Change settings without recompiling |
| `error_loop()` + `ESP.restart()` | `respawn: true` in the launch file | If the adapter is unplugged, the node exits and restarts |

## Topics (unchanged from the main-branch firmware)

| Topic | Type | Meaning |
|---|---|---|
| `cmd_vel` (sub) | geometry_msgs/Twist | Drive base: `linear.x` forward, `angular.z` turn, as -1..1 power |
| `depositor/position_setpoint` (sub) | std_msgs/Float32 | Depositor position in rotations |
| `excavator/actuator_output` (sub) | std_msgs/Float32 | Excavator actuator power, -1..1 |
| `excavator/velocity_setpoint` (sub) | std_msgs/Float32 | Excavator motor speed in RPM |
| `enabled` (sub) | std_msgs/Bool | Master on/off. Motors only move while this is true |
| `robot_data` (pub) | cometbot_can/RobotStatusMessage | Status of all 5 motors, every 250 ms |

## Build

Inside the dev container (or on the mini PC with ROS 2 Humble installed):

```bash
cd /workspace/cometbot_ws
colcon build --packages-select cometbot_can
source install/setup.bash
colcon test --packages-select cometbot_can --event-handlers console_direct+   # unit tests
```

## Try it with NO hardware (virtual CAN bus)

Linux can make a fake CAN bus called `vcan0`. Nothing moves, but you can watch
the exact frames the motors would get.

```bash
# Terminal 1: make the fake bus, then watch it
ros2 run cometbot_can setup_can.sh --virtual   # if modprobe fails in the container, run `sudo modprobe vcan` on the host/VM
candump vcan0

# Terminal 2: start the node on the fake bus
ros2 launch cometbot_can can_bridge.launch.py can_interface:=vcan0

# Terminal 3: enable and drive forward at half power
ros2 topic pub --once /enabled std_msgs/msg/Bool "{data: true}"
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.5}}"
```

In terminal 1 you should see something like:

```
vcan0  02052C80   [8]  FF FF FF FF FF FF FF FF   <- "enabled" heartbeat, every 25 ms
vcan0  0205008B   [8]  00 00 00 3F 00 00 00 00   <- left drive (ID 11): duty cycle 0.5
vcan0  0205008A   [8]  00 00 00 BF 00 00 00 00   <- right drive (ID 10): -0.5 (mirrored)
vcan0  0205004B   [8]  00 00 00 3F 00 00 00 00   <- after the first one: "use current mode" 0.5
```

(`00 00 00 3F` is how the computer stores the decimal number 0.5.)

## Run it on the real robot

1. Plug the USB-CAN adapter into the mini PC and wire it to the CAN bus
   (CAN-H to CAN-H, CAN-L to CAN-L, and the bus needs 120 Ω termination).
2. `ros2 run cometbot_can setup_can.sh` brings up `can0` at 1 Mbit/s.
3. `candump can0`: with the SPARK MAXs powered you should see their status
   frames (IDs starting with `020518`) even before the node runs.
4. Check the CAN IDs in `config/can_bridge.yaml` match the robot.
5. `ros2 launch cometbot_can can_bridge.launch.py`
6. Put the robot on blocks, then publish `enabled: true` and a small `cmd_vel`.

## What's different from the old firmware

- **Safer default:** `start_enabled` is false. The old code started enabled
  ("ONLY FOR TESTING"), so now nothing moves until `enabled` is published true.
- **Sends a disable when it shuts down:** Ctrl+C stops the motors immediately.
- **Reads every waiting status frame** each 10 ms tick. The old code read one,
  which can't keep up with 150 status frames per second.
- **Fixed negative applied output.** It's a signed number. The old `2 - x`
  workaround gave the wrong sign.
- **Fixed a lost "mode" frame.** If two commands arrived before the first was
  sent, the old code could skip ever telling the motor its control mode.
- **Fixed a status-frame ID mismatch.** The MCP2515 library left an extra
  `0x80000000` bit on received IDs, so they may never have matched the status
  frame constants. SocketCAN IDs are cleaned before matching.
- **CAN IDs and limits are parameters** in `config/can_bridge.yaml`.
- **`invert_turn_when_reversing`** parameter: `true` keeps the old joystick
  feel. Nav2 expects `false`.

## Still to confirm with the team

- **CAN IDs.** `main` and `depositor-and-excavator` disagree. Defaults here are main's.
- **Current scaling.** `current` is still the raw number, as before. It's probably amps × 32.
- **SPARK MAX firmware.** These frame IDs are last year's protocol (the same
  ones the ESP32 used). If the SPARK MAXs were updated to newer REV firmware,
  check them against the protocol PDFs in `SPARK MAX CAN PROTOCOL/`.
- **Dev container:** it now uses `--network=host` (so it can see `can0`) and
  installs `can-utils`. Rebuild the container after pulling.
