// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from custom_messages:msg/SparkMaxMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__BUILDER_HPP_
#define CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "custom_messages/msg/detail/spark_max_message__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace custom_messages
{

namespace msg
{

namespace builder
{

class Init_SparkMaxMessage_current
{
public:
  explicit Init_SparkMaxMessage_current(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  ::custom_messages::msg::SparkMaxMessage current(::custom_messages::msg::SparkMaxMessage::_current_type arg)
  {
    msg_.current = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_voltage
{
public:
  explicit Init_SparkMaxMessage_voltage(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  Init_SparkMaxMessage_current voltage(::custom_messages::msg::SparkMaxMessage::_voltage_type arg)
  {
    msg_.voltage = std::move(arg);
    return Init_SparkMaxMessage_current(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_temperature
{
public:
  explicit Init_SparkMaxMessage_temperature(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  Init_SparkMaxMessage_voltage temperature(::custom_messages::msg::SparkMaxMessage::_temperature_type arg)
  {
    msg_.temperature = std::move(arg);
    return Init_SparkMaxMessage_voltage(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_position
{
public:
  explicit Init_SparkMaxMessage_position(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  Init_SparkMaxMessage_temperature position(::custom_messages::msg::SparkMaxMessage::_position_type arg)
  {
    msg_.position = std::move(arg);
    return Init_SparkMaxMessage_temperature(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_velocity
{
public:
  explicit Init_SparkMaxMessage_velocity(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  Init_SparkMaxMessage_position velocity(::custom_messages::msg::SparkMaxMessage::_velocity_type arg)
  {
    msg_.velocity = std::move(arg);
    return Init_SparkMaxMessage_position(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_applied_output
{
public:
  explicit Init_SparkMaxMessage_applied_output(::custom_messages::msg::SparkMaxMessage & msg)
  : msg_(msg)
  {}
  Init_SparkMaxMessage_velocity applied_output(::custom_messages::msg::SparkMaxMessage::_applied_output_type arg)
  {
    msg_.applied_output = std::move(arg);
    return Init_SparkMaxMessage_velocity(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

class Init_SparkMaxMessage_device_id
{
public:
  Init_SparkMaxMessage_device_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SparkMaxMessage_applied_output device_id(::custom_messages::msg::SparkMaxMessage::_device_id_type arg)
  {
    msg_.device_id = std::move(arg);
    return Init_SparkMaxMessage_applied_output(msg_);
  }

private:
  ::custom_messages::msg::SparkMaxMessage msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_messages::msg::SparkMaxMessage>()
{
  return custom_messages::msg::builder::Init_SparkMaxMessage_device_id();
}

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__BUILDER_HPP_
