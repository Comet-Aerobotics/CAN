// One SPARK MAX motor controller.
//
// Ported from microROS_test/lib/SPARK_MAX (ESP32 version). The big difference:
// this class no longer sends anything itself. It just BUILDS frames
// (pending_command, status_period_frames) and READS frames (handle_frame).
// The node decides when to push them through the SocketCan object. That keeps
// this class free of hardware and easy to test.
#pragma once

#include <cstdint>
#include <optional>
#include <string>
#include <vector>

#include "cometbot_can/spark_protocol.hpp"

namespace cometbot_can
{

// What the SPARK MAX last told us about itself (same fields as before).
struct SparkMaxStatus
{
  float applied_output = 0.0f;  // -1 .. 1
  float velocity = 0.0f;        // RPM
  float position = 0.0f;        // rotations
  uint8_t temperature = 0;      // deg C
  float voltage = 0.0f;         // volts
  float current = 0.0f;         // raw 12-bit value, see note in spark_max.cpp
};

class SparkMax
{
public:
  // device_id = the CAN ID set in REV Hardware Client (1..62).
  explicit SparkMax(uint8_t device_id);

  uint8_t device_id() const {return device_id_;}

  // Frames that tell the SPARK MAX how often (ms) to send each status report.
  // Same defaults as the ESP32 code: 100, 100, 100, 1000, 1000.
  std::vector<CanMessage> status_period_frames(
    uint16_t period0 = 100, uint16_t period1 = 100, uint16_t period2 = 100,
    uint16_t period3 = 1000, uint16_t period4 = 1000) const;

  // Queue a command (was set_control_frame). It isn't sent yet: the node's
  // CAN loop sends it on its next tick, then calls mark_command_sent().
  void set_command(ControlMode mode, float setpoint);

  // The queued command, if there is one.
  std::optional<CanMessage> pending_command() const {return pending_;}

  // Call after the pending command was actually put on the bus.
  void mark_command_sent();

  // Give it any received frame. Returns true if the frame was a status report
  // from THIS device and was understood.
  bool handle_frame(const CanMessage & msg);

  const SparkMaxStatus & status() const {return status_;}
  std::string to_string() const;

private:
  void parse_status_0(const CanMessage & msg);
  void parse_status_1(const CanMessage & msg);
  void parse_status_2(const CanMessage & msg);

  uint8_t device_id_;
  ControlMode pending_mode_ = ControlMode::None;  // mode of the queued command
  ControlMode sent_mode_ = ControlMode::None;     // last mode actually sent
  std::optional<CanMessage> pending_;
  SparkMaxStatus status_;
};

}  // namespace cometbot_can
