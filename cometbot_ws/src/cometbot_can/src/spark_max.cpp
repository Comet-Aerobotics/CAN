#include "cometbot_can/spark_max.hpp"

#include <cstring>
#include <sstream>

namespace cometbot_can
{

namespace
{
// Read 4 bytes (little-endian) as a float. Same as data_to_float_32_bit().
float read_float(const uint8_t * bytes)
{
  uint32_t raw = static_cast<uint32_t>(bytes[0]) |
    (static_cast<uint32_t>(bytes[1]) << 8) |
    (static_cast<uint32_t>(bytes[2]) << 16) |
    (static_cast<uint32_t>(bytes[3]) << 24);
  float value;
  std::memcpy(&value, &raw, sizeof(value));
  return value;
}

// Write a float as 4 little-endian bytes. Same as create_data() on the ESP32.
void write_float(uint8_t * bytes, float value)
{
  uint32_t raw;
  std::memcpy(&raw, &value, sizeof(raw));
  bytes[0] = raw & 0xFF;
  bytes[1] = (raw >> 8) & 0xFF;
  bytes[2] = (raw >> 16) & 0xFF;
  bytes[3] = (raw >> 24) & 0xFF;
}
}  // namespace

SparkMax::SparkMax(uint8_t device_id)
: device_id_(device_id)
{
}

std::vector<CanMessage> SparkMax::status_period_frames(
  uint16_t period0, uint16_t period1, uint16_t period2,
  uint16_t period3, uint16_t period4) const
{
  const StatusFrame frames[5] = {
    StatusFrame::Status0, StatusFrame::Status1, StatusFrame::Status2,
    StatusFrame::Status3, StatusFrame::Status4};
  const uint16_t periods[5] = {period0, period1, period2, period3, period4};

  std::vector<CanMessage> out;
  for (int i = 0; i < 5; ++i) {
    CanMessage msg;
    msg.id = static_cast<uint32_t>(frames[i]) + device_id_;
    msg.len = 2;
    msg.data[0] = periods[i] & 0xFF;         // low byte first (little-endian)
    msg.data[1] = (periods[i] >> 8) & 0xFF;
    out.push_back(msg);
  }
  return out;
}

void SparkMax::set_command(ControlMode mode, float setpoint)
{
  if (mode == ControlMode::None) {
    return;
  }

  CanMessage msg;
  msg.len = 8;
  write_float(msg.data, setpoint);  // bytes 4..7 stay 0

  // Same trick as the ESP32 code: the first command in a new mode uses that
  // mode's ID; after that, "use current mode" is enough.
  //
  // Fix vs. the old code: the old code switched to "use current mode" as soon
  // as the mode frame was QUEUED. If a second command arrived before the first
  // one was sent (e.g. while the robot was disabled), the mode frame was
  // overwritten and never reached the motor. Now we only switch after the mode
  // frame has really been SENT.
  if (mode == sent_mode_) {
    msg.id = static_cast<uint32_t>(ControlMode::UseCurrentMode) + device_id_;
  } else {
    msg.id = static_cast<uint32_t>(mode) + device_id_;
  }
  pending_mode_ = mode;
  pending_ = msg;
}

void SparkMax::mark_command_sent()
{
  if (pending_) {
    sent_mode_ = pending_mode_;
  }
  pending_.reset();  // same as clear_current_frame()
}

bool SparkMax::handle_frame(const CanMessage & msg)
{
  if ((msg.id & DEVICE_ID_BITS) != device_id_) {
    return false;  // someone else's frame
  }

  const uint32_t type = msg.id & MESSAGE_TYPE_BITS;
  if (type == static_cast<uint32_t>(StatusFrame::Status0)) {
    parse_status_0(msg);
  } else if (type == static_cast<uint32_t>(StatusFrame::Status1)) {
    parse_status_1(msg);
  } else if (type == static_cast<uint32_t>(StatusFrame::Status2)) {
    parse_status_2(msg);
  } else {
    return false;
  }
  return true;
}

void SparkMax::parse_status_0(const CanMessage & msg)
{
  if (msg.len < 2) {
    return;
  }
  // Applied output is a SIGNED 16-bit number. The old code read it as
  // unsigned, which is why negative values came out "backwards" and needed the
  // `2 - x` hack. Reading it as int16_t fixes that properly.
  const int16_t raw = static_cast<int16_t>(
    static_cast<uint16_t>(msg.data[0]) | (static_cast<uint16_t>(msg.data[1]) << 8));
  status_.applied_output = raw / 32764.0f;  // same scale as the old code
}

void SparkMax::parse_status_1(const CanMessage & msg)
{
  if (msg.len < 8) {
    return;
  }
  status_.velocity = read_float(&msg.data[0]);  // RPM
  status_.temperature = msg.data[4];            // deg C

  // Voltage and current are 12-bit numbers packed into bytes 5..7.
  const uint16_t voltage_raw =
    ((static_cast<uint16_t>(msg.data[6]) & 0x0F) << 8) | msg.data[5];
  const uint16_t current_raw =
    (static_cast<uint16_t>(msg.data[7]) << 4) | (msg.data[6] >> 4);
  status_.voltage = voltage_raw / 128.0f;
  // TODO(controls): still the raw number, same as the old code ("need to graph
  // to find constant"). REV's older docs suggest amps = raw / 32. Check
  // against REV Hardware Client before trusting it.
  status_.current = static_cast<float>(current_raw);
}

void SparkMax::parse_status_2(const CanMessage & msg)
{
  if (msg.len < 4) {
    return;
  }
  status_.position = read_float(&msg.data[0]);  // rotations
}

std::string SparkMax::to_string() const
{
  std::ostringstream out;
  out << "SPARK MAX " << static_cast<int>(device_id_)
      << " | output " << status_.applied_output
      << " | vel " << status_.velocity
      << " | pos " << status_.position
      << " | temp " << static_cast<int>(status_.temperature)
      << " | volt " << status_.voltage
      << " | current(raw) " << status_.current;
  return out.str();
}

}  // namespace cometbot_can
