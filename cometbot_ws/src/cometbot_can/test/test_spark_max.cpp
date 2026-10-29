// Checks that the new SparkMax class builds the SAME bytes the ESP32 code did,
// and reads status frames correctly. No hardware needed.
// Run with: colcon test --packages-select cometbot_can --event-handlers console_direct+
#include <gtest/gtest.h>

#include <cstring>

#include "cometbot_can/spark_max.hpp"

using cometbot_can::CanMessage;
using cometbot_can::ControlMode;
using cometbot_can::SparkMax;

namespace
{
float float_from(const uint8_t * b)
{
  float f;
  std::memcpy(&f, b, 4);
  return f;
}
}  // namespace

TEST(SparkMax, StatusPeriodFramesMatchOldCode)
{
  SparkMax spark(11);
  auto frames = spark.status_period_frames();  // 100,100,100,1000,1000
  ASSERT_EQ(frames.size(), 5u);
  // Old code: CAN0.sendMsgBuf(device_id + status_1, CAN_EXTID, 2, {period LE})
  EXPECT_EQ(frames[1].id, 0x2051840u + 11u);
  EXPECT_EQ(frames[1].len, 2);
  EXPECT_EQ(frames[1].data[0], 100);
  EXPECT_EQ(frames[1].data[1], 0);
  // 1000 = 0x03E8 -> E8 03
  EXPECT_EQ(frames[4].id, 0x2051900u + 11u);
  EXPECT_EQ(frames[4].data[0], 0xE8);
  EXPECT_EQ(frames[4].data[1], 0x03);
}

TEST(SparkMax, FirstCommandUsesModeIdThenUseCurrentMode)
{
  SparkMax spark(10);
  spark.set_command(ControlMode::DutyCycleSet, 0.5f);
  auto cmd = spark.pending_command();
  ASSERT_TRUE(cmd.has_value());
  EXPECT_EQ(cmd->id, 0x2050080u + 10u);
  EXPECT_EQ(cmd->len, 8);
  EXPECT_FLOAT_EQ(float_from(cmd->data), 0.5f);
  for (int i = 4; i < 8; ++i) {
    EXPECT_EQ(cmd->data[i], 0);
  }

  spark.mark_command_sent();
  EXPECT_FALSE(spark.pending_command().has_value());

  spark.set_command(ControlMode::DutyCycleSet, -0.25f);
  cmd = spark.pending_command();
  ASSERT_TRUE(cmd.has_value());
  EXPECT_EQ(cmd->id, 0x2050040u + 10u);  // Use_Current_Mode
  EXPECT_FLOAT_EQ(float_from(cmd->data), -0.25f);
}

TEST(SparkMax, ModeFrameIsNotLostIfOverwrittenBeforeSending)
{
  SparkMax spark(12);
  spark.set_command(ControlMode::PositionSet, 10.0f);
  spark.set_command(ControlMode::PositionSet, 20.0f);  // before anything was sent
  auto cmd = spark.pending_command();
  ASSERT_TRUE(cmd.has_value());
  EXPECT_EQ(cmd->id, 0x2050C80u + 12u);  // still the Position_Set frame
  EXPECT_FLOAT_EQ(float_from(cmd->data), 20.0f);
}

TEST(SparkMax, SwitchingModesSendsNewModeId)
{
  SparkMax spark(13);
  spark.set_command(ControlMode::DutyCycleSet, 0.1f);
  spark.mark_command_sent();
  spark.set_command(ControlMode::VoltageSet, 6.0f);
  EXPECT_EQ(spark.pending_command()->id, 0x2051080u + 13u);
}

TEST(SparkMax, ParsesStatus1)
{
  SparkMax spark(14);
  CanMessage msg;
  msg.id = 0x2051840 + 14;
  msg.len = 8;
  const float rpm = 1234.5f;
  std::memcpy(msg.data, &rpm, 4);
  msg.data[4] = 40;  // deg C
  // voltage 12.0 V -> 12*128 = 1536 = 0x600 ; current raw 20 = 0x014
  msg.data[5] = 0x00;           // voltage low 8 bits
  msg.data[6] = 0x46;           // high nibble: current low 4 bits (4), low nibble: voltage high 4 bits (6)
  msg.data[7] = 0x01;           // current high 8 bits
  EXPECT_TRUE(spark.handle_frame(msg));
  EXPECT_FLOAT_EQ(spark.status().velocity, 1234.5f);
  EXPECT_EQ(spark.status().temperature, 40);
  EXPECT_FLOAT_EQ(spark.status().voltage, 12.0f);
  EXPECT_FLOAT_EQ(spark.status().current, 20.0f);
}

TEST(SparkMax, ParsesNegativeAppliedOutput)
{
  SparkMax spark(11);
  CanMessage msg;
  msg.id = 0x2051800 + 11;
  msg.len = 8;
  const int16_t raw = -16382;  // about -0.5
  msg.data[0] = static_cast<uint16_t>(raw) & 0xFF;
  msg.data[1] = (static_cast<uint16_t>(raw) >> 8) & 0xFF;
  EXPECT_TRUE(spark.handle_frame(msg));
  EXPECT_NEAR(spark.status().applied_output, -0.5f, 0.001f);
}

TEST(SparkMax, ParsesStatus2Position)
{
  SparkMax spark(11);
  CanMessage msg;
  msg.id = 0x2051880 + 11;
  msg.len = 8;
  const float rotations = -3.75f;
  std::memcpy(msg.data, &rotations, 4);
  EXPECT_TRUE(spark.handle_frame(msg));
  EXPECT_FLOAT_EQ(spark.status().position, -3.75f);
}

TEST(SparkMax, IgnoresOtherDevicesAndUnknownFrames)
{
  SparkMax spark(11);
  CanMessage other;
  other.id = 0x2051840 + 10;  // device 10, not 11
  other.len = 8;
  EXPECT_FALSE(spark.handle_frame(other));

  CanMessage heartbeat;
  heartbeat.id = 0x2052C80;
  heartbeat.len = 8;
  EXPECT_FALSE(spark.handle_frame(heartbeat));
}
