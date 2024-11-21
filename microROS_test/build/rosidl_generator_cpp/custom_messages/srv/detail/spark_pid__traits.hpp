// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from custom_messages:srv/SparkPID.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__TRAITS_HPP_
#define CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "custom_messages/srv/detail/spark_pid__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace custom_messages
{

namespace srv
{

inline void to_flow_style_yaml(
  const SparkPID_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: id
  {
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << ", ";
  }

  // member: type
  {
    out << "type: ";
    rosidl_generator_traits::value_to_yaml(msg.type, out);
    out << ", ";
  }

  // member: setpoint
  {
    out << "setpoint: ";
    rosidl_generator_traits::value_to_yaml(msg.setpoint, out);
    out << ", ";
  }

  // member: slot
  {
    out << "slot: ";
    rosidl_generator_traits::value_to_yaml(msg.slot, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SparkPID_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: id
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "id: ";
    rosidl_generator_traits::value_to_yaml(msg.id, out);
    out << "\n";
  }

  // member: type
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "type: ";
    rosidl_generator_traits::value_to_yaml(msg.type, out);
    out << "\n";
  }

  // member: setpoint
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "setpoint: ";
    rosidl_generator_traits::value_to_yaml(msg.setpoint, out);
    out << "\n";
  }

  // member: slot
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "slot: ";
    rosidl_generator_traits::value_to_yaml(msg.slot, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SparkPID_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace custom_messages

namespace rosidl_generator_traits
{

[[deprecated("use custom_messages::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const custom_messages::srv::SparkPID_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  custom_messages::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use custom_messages::srv::to_yaml() instead")]]
inline std::string to_yaml(const custom_messages::srv::SparkPID_Request & msg)
{
  return custom_messages::srv::to_yaml(msg);
}

template<>
inline const char * data_type<custom_messages::srv::SparkPID_Request>()
{
  return "custom_messages::srv::SparkPID_Request";
}

template<>
inline const char * name<custom_messages::srv::SparkPID_Request>()
{
  return "custom_messages/srv/SparkPID_Request";
}

template<>
struct has_fixed_size<custom_messages::srv::SparkPID_Request>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<custom_messages::srv::SparkPID_Request>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<custom_messages::srv::SparkPID_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace custom_messages
{

namespace srv
{

inline void to_flow_style_yaml(
  const SparkPID_Response & msg,
  std::ostream & out)
{
  (void)msg;
  out << "null";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SparkPID_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  (void)msg;
  (void)indentation;
  out << "null\n";
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SparkPID_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace custom_messages

namespace rosidl_generator_traits
{

[[deprecated("use custom_messages::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const custom_messages::srv::SparkPID_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  custom_messages::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use custom_messages::srv::to_yaml() instead")]]
inline std::string to_yaml(const custom_messages::srv::SparkPID_Response & msg)
{
  return custom_messages::srv::to_yaml(msg);
}

template<>
inline const char * data_type<custom_messages::srv::SparkPID_Response>()
{
  return "custom_messages::srv::SparkPID_Response";
}

template<>
inline const char * name<custom_messages::srv::SparkPID_Response>()
{
  return "custom_messages/srv/SparkPID_Response";
}

template<>
struct has_fixed_size<custom_messages::srv::SparkPID_Response>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<custom_messages::srv::SparkPID_Response>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<custom_messages::srv::SparkPID_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<custom_messages::srv::SparkPID>()
{
  return "custom_messages::srv::SparkPID";
}

template<>
inline const char * name<custom_messages::srv::SparkPID>()
{
  return "custom_messages/srv/SparkPID";
}

template<>
struct has_fixed_size<custom_messages::srv::SparkPID>
  : std::integral_constant<
    bool,
    has_fixed_size<custom_messages::srv::SparkPID_Request>::value &&
    has_fixed_size<custom_messages::srv::SparkPID_Response>::value
  >
{
};

template<>
struct has_bounded_size<custom_messages::srv::SparkPID>
  : std::integral_constant<
    bool,
    has_bounded_size<custom_messages::srv::SparkPID_Request>::value &&
    has_bounded_size<custom_messages::srv::SparkPID_Response>::value
  >
{
};

template<>
struct is_service<custom_messages::srv::SparkPID>
  : std::true_type
{
};

template<>
struct is_service_request<custom_messages::srv::SparkPID_Request>
  : std::true_type
{
};

template<>
struct is_service_response<custom_messages::srv::SparkPID_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__TRAITS_HPP_
