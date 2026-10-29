// SPARK MAX / FRC CAN protocol constants.
//
// Ported from microROS_test/lib/Comet_CAN_Common.h (ESP32 version).
// The numbers are exactly the same as before, so the motors see the same frames.
#pragma once

#include <cstdint>

namespace cometbot_can
{

// One CAN frame (an "envelope" with an address and up to 8 bytes inside).
// Called CanMessage instead of can_frame so it doesn't clash with Linux's own
// `struct can_frame` from <linux/can.h>.
struct CanMessage
{
  uint32_t id = 0;        // 29-bit extended CAN ID, no flag bits
  uint8_t len = 0;        // how many data bytes are used (0..8)
  uint8_t data[8] = {0};
};

// FRC CAN IDs: the lowest 6 bits are the device number (the SPARK MAX's CAN ID),
// the other bits say what kind of message it is.
constexpr uint32_t DEVICE_ID_BITS = 0x3F;
constexpr uint32_t EXTENDED_ID_BITS = 0x1FFFFFFF;
constexpr uint32_t MESSAGE_TYPE_BITS = EXTENDED_ID_BITS & ~DEVICE_ID_BITS;

// "Robot is enabled" heartbeat. SPARK MAXs only drive while they keep hearing
// the enabled version of this (8 bytes of 0xFF). 8 bytes of 0x00 = disabled.
constexpr uint32_t HEARTBEAT_ID = 0x2052C80;
constexpr uint8_t HEARTBEAT_LEN = 8;

// Ways to command a SPARK MAX (same values as the old `control_mode` enum).
// The device ID gets added on top of these to make the final CAN ID.
enum class ControlMode : uint32_t
{
  UseCurrentMode = 0x2050040,
  DutyCycleSet = 0x2050080,       // -1.0 .. 1.0 "percent power"
  SpeedSet = 0x2050480,           // RPM
  SmartVelocitySet = 0x20504C0,
  PositionSet = 0x2050C80,        // rotations
  VoltageSet = 0x2051080,         // volts
  CurrentSet = 0x20510C0,         // amps
  SmartMotionSet = 0x2051480,
  None = 0x0000000,
};

// Status reports the SPARK MAX sends back on its own every N ms.
enum class StatusFrame : uint32_t
{
  Status0 = 0x2051800,  // applied output
  Status1 = 0x2051840,  // velocity, temperature, voltage, current
  Status2 = 0x2051880,  // position
  Status3 = 0x20518C0,
  Status4 = 0x2051900,
};

}  // namespace cometbot_can
