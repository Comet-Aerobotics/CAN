// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__TRAITS_HPP_
#define CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "custom_messages/msg/detail/robot_status_message__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'left_drivebase'
// Member 'right_drivebase'
#include "custom_messages/msg/detail/spark_max_message__traits.hpp"

namespace custom_messages
{

namespace msg
{

inline void to_flow_style_yaml(
  const RobotStatusMessage & msg,
  std::ostream & out)
{
  out << "{";
  // member: enabled
  {
    out << "enabled: ";
    rosidl_generator_traits::value_to_yaml(msg.enabled, out);
    out << ", ";
  }

  // member: left_drivebase
  {
    out << "left_drivebase: ";
    to_flow_style_yaml(msg.left_drivebase, out);
    out << ", ";
  }

  // member: right_drivebase
  {
    out << "right_drivebase: ";
    to_flow_style_yaml(msg.right_drivebase, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const RobotStatusMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: enabled
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "enabled: ";
    rosidl_generator_traits::value_to_yaml(msg.enabled, out);
    out << "\n";
  }

  // member: left_drivebase
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "left_drivebase:\n";
    to_block_style_yaml(msg.left_drivebase, out, indentation + 2);
  }

  // member: right_drivebase
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "right_drivebase:\n";
    to_block_style_yaml(msg.right_drivebase, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const RobotStatusMessage & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace custom_messages

namespace rosidl_generator_traits
{

[[deprecated("use custom_messages::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const custom_messages::msg::RobotStatusMessage & msg,
  std::ostream & out, size_t indentation = 0)
{
  custom_messages::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use custom_messages::msg::to_yaml() instead")]]
inline std::string to_yaml(const custom_messages::msg::RobotStatusMessage & msg)
{
  return custom_messages::msg::to_yaml(msg);
}

template<>
inline const char * data_type<custom_messages::msg::RobotStatusMessage>()
{
  return "custom_messages::msg::RobotStatusMessage";
}

template<>
inline const char * name<custom_messages::msg::RobotStatusMessage>()
{
  return "custom_messages/msg/RobotStatusMessage";
}

template<>
struct has_fixed_size<custom_messages::msg::RobotStatusMessage>
  : std::integral_constant<bool, has_fixed_size<custom_messages::msg::SparkMaxMessage>::value> {};

template<>
struct has_bounded_size<custom_messages::msg::RobotStatusMessage>
  : std::integral_constant<bool, has_bounded_size<custom_messages::msg::SparkMaxMessage>::value> {};

template<>
struct is_message<custom_messages::msg::RobotStatusMessage>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__TRAITS_HPP_
