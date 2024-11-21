// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__BUILDER_HPP_
#define CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "custom_messages/msg/detail/robot_status_message__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace custom_messages
{

namespace msg
{

namespace builder
{

class Init_RobotStatusMessage_right_drivebase
{
public:
  explicit Init_RobotStatusMessage_right_drivebase(::custom_messages::msg::RobotStatusMessage & msg)
  : msg_(msg)
  {}
  ::custom_messages::msg::RobotStatusMessage right_drivebase(::custom_messages::msg::RobotStatusMessage::_right_drivebase_type arg)
  {
    msg_.right_drivebase = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_messages::msg::RobotStatusMessage msg_;
};

class Init_RobotStatusMessage_left_drivebase
{
public:
  explicit Init_RobotStatusMessage_left_drivebase(::custom_messages::msg::RobotStatusMessage & msg)
  : msg_(msg)
  {}
  Init_RobotStatusMessage_right_drivebase left_drivebase(::custom_messages::msg::RobotStatusMessage::_left_drivebase_type arg)
  {
    msg_.left_drivebase = std::move(arg);
    return Init_RobotStatusMessage_right_drivebase(msg_);
  }

private:
  ::custom_messages::msg::RobotStatusMessage msg_;
};

class Init_RobotStatusMessage_enabled
{
public:
  Init_RobotStatusMessage_enabled()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_RobotStatusMessage_left_drivebase enabled(::custom_messages::msg::RobotStatusMessage::_enabled_type arg)
  {
    msg_.enabled = std::move(arg);
    return Init_RobotStatusMessage_left_drivebase(msg_);
  }

private:
  ::custom_messages::msg::RobotStatusMessage msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_messages::msg::RobotStatusMessage>()
{
  return custom_messages::msg::builder::Init_RobotStatusMessage_enabled();
}

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__BUILDER_HPP_
