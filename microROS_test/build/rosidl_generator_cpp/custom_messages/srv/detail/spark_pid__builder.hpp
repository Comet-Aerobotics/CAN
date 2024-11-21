// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from custom_messages:srv/SparkPID.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__BUILDER_HPP_
#define CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "custom_messages/srv/detail/spark_pid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace custom_messages
{

namespace srv
{

namespace builder
{

class Init_SparkPID_Request_slot
{
public:
  explicit Init_SparkPID_Request_slot(::custom_messages::srv::SparkPID_Request & msg)
  : msg_(msg)
  {}
  ::custom_messages::srv::SparkPID_Request slot(::custom_messages::srv::SparkPID_Request::_slot_type arg)
  {
    msg_.slot = std::move(arg);
    return std::move(msg_);
  }

private:
  ::custom_messages::srv::SparkPID_Request msg_;
};

class Init_SparkPID_Request_setpoint
{
public:
  explicit Init_SparkPID_Request_setpoint(::custom_messages::srv::SparkPID_Request & msg)
  : msg_(msg)
  {}
  Init_SparkPID_Request_slot setpoint(::custom_messages::srv::SparkPID_Request::_setpoint_type arg)
  {
    msg_.setpoint = std::move(arg);
    return Init_SparkPID_Request_slot(msg_);
  }

private:
  ::custom_messages::srv::SparkPID_Request msg_;
};

class Init_SparkPID_Request_type
{
public:
  explicit Init_SparkPID_Request_type(::custom_messages::srv::SparkPID_Request & msg)
  : msg_(msg)
  {}
  Init_SparkPID_Request_setpoint type(::custom_messages::srv::SparkPID_Request::_type_type arg)
  {
    msg_.type = std::move(arg);
    return Init_SparkPID_Request_setpoint(msg_);
  }

private:
  ::custom_messages::srv::SparkPID_Request msg_;
};

class Init_SparkPID_Request_id
{
public:
  Init_SparkPID_Request_id()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SparkPID_Request_type id(::custom_messages::srv::SparkPID_Request::_id_type arg)
  {
    msg_.id = std::move(arg);
    return Init_SparkPID_Request_type(msg_);
  }

private:
  ::custom_messages::srv::SparkPID_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_messages::srv::SparkPID_Request>()
{
  return custom_messages::srv::builder::Init_SparkPID_Request_id();
}

}  // namespace custom_messages


namespace custom_messages
{

namespace srv
{


}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::custom_messages::srv::SparkPID_Response>()
{
  return ::custom_messages::srv::SparkPID_Response(rosidl_runtime_cpp::MessageInitialization::ZERO);
}

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__BUILDER_HPP_
