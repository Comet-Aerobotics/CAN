// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from custom_messages:msg/SparkMaxMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_HPP_
#define CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__custom_messages__msg__SparkMaxMessage __attribute__((deprecated))
#else
# define DEPRECATED__custom_messages__msg__SparkMaxMessage __declspec(deprecated)
#endif

namespace custom_messages
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct SparkMaxMessage_
{
  using Type = SparkMaxMessage_<ContainerAllocator>;

  explicit SparkMaxMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->device_id = 0;
      this->applied_output = 0.0f;
      this->velocity = 0.0f;
      this->position = 0.0f;
      this->temperature = 0;
      this->voltage = 0.0f;
      this->current = 0.0f;
    }
  }

  explicit SparkMaxMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->device_id = 0;
      this->applied_output = 0.0f;
      this->velocity = 0.0f;
      this->position = 0.0f;
      this->temperature = 0;
      this->voltage = 0.0f;
      this->current = 0.0f;
    }
  }

  // field types and members
  using _device_id_type =
    uint8_t;
  _device_id_type device_id;
  using _applied_output_type =
    float;
  _applied_output_type applied_output;
  using _velocity_type =
    float;
  _velocity_type velocity;
  using _position_type =
    float;
  _position_type position;
  using _temperature_type =
    uint8_t;
  _temperature_type temperature;
  using _voltage_type =
    float;
  _voltage_type voltage;
  using _current_type =
    float;
  _current_type current;

  // setters for named parameter idiom
  Type & set__device_id(
    const uint8_t & _arg)
  {
    this->device_id = _arg;
    return *this;
  }
  Type & set__applied_output(
    const float & _arg)
  {
    this->applied_output = _arg;
    return *this;
  }
  Type & set__velocity(
    const float & _arg)
  {
    this->velocity = _arg;
    return *this;
  }
  Type & set__position(
    const float & _arg)
  {
    this->position = _arg;
    return *this;
  }
  Type & set__temperature(
    const uint8_t & _arg)
  {
    this->temperature = _arg;
    return *this;
  }
  Type & set__voltage(
    const float & _arg)
  {
    this->voltage = _arg;
    return *this;
  }
  Type & set__current(
    const float & _arg)
  {
    this->current = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    custom_messages::msg::SparkMaxMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const custom_messages::msg::SparkMaxMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      custom_messages::msg::SparkMaxMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      custom_messages::msg::SparkMaxMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__custom_messages__msg__SparkMaxMessage
    std::shared_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__custom_messages__msg__SparkMaxMessage
    std::shared_ptr<custom_messages::msg::SparkMaxMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SparkMaxMessage_ & other) const
  {
    if (this->device_id != other.device_id) {
      return false;
    }
    if (this->applied_output != other.applied_output) {
      return false;
    }
    if (this->velocity != other.velocity) {
      return false;
    }
    if (this->position != other.position) {
      return false;
    }
    if (this->temperature != other.temperature) {
      return false;
    }
    if (this->voltage != other.voltage) {
      return false;
    }
    if (this->current != other.current) {
      return false;
    }
    return true;
  }
  bool operator!=(const SparkMaxMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SparkMaxMessage_

// alias to use template instance with default allocator
using SparkMaxMessage =
  custom_messages::msg::SparkMaxMessage_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_HPP_
