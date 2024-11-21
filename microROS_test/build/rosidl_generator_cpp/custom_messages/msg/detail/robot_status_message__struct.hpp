// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_HPP_
#define CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'left_drivebase'
// Member 'right_drivebase'
#include "custom_messages/msg/detail/spark_max_message__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__custom_messages__msg__RobotStatusMessage __attribute__((deprecated))
#else
# define DEPRECATED__custom_messages__msg__RobotStatusMessage __declspec(deprecated)
#endif

namespace custom_messages
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct RobotStatusMessage_
{
  using Type = RobotStatusMessage_<ContainerAllocator>;

  explicit RobotStatusMessage_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : left_drivebase(_init),
    right_drivebase(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->enabled = false;
    }
  }

  explicit RobotStatusMessage_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : left_drivebase(_alloc, _init),
    right_drivebase(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->enabled = false;
    }
  }

  // field types and members
  using _enabled_type =
    bool;
  _enabled_type enabled;
  using _left_drivebase_type =
    custom_messages::msg::SparkMaxMessage_<ContainerAllocator>;
  _left_drivebase_type left_drivebase;
  using _right_drivebase_type =
    custom_messages::msg::SparkMaxMessage_<ContainerAllocator>;
  _right_drivebase_type right_drivebase;

  // setters for named parameter idiom
  Type & set__enabled(
    const bool & _arg)
  {
    this->enabled = _arg;
    return *this;
  }
  Type & set__left_drivebase(
    const custom_messages::msg::SparkMaxMessage_<ContainerAllocator> & _arg)
  {
    this->left_drivebase = _arg;
    return *this;
  }
  Type & set__right_drivebase(
    const custom_messages::msg::SparkMaxMessage_<ContainerAllocator> & _arg)
  {
    this->right_drivebase = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    custom_messages::msg::RobotStatusMessage_<ContainerAllocator> *;
  using ConstRawPtr =
    const custom_messages::msg::RobotStatusMessage_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      custom_messages::msg::RobotStatusMessage_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      custom_messages::msg::RobotStatusMessage_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__custom_messages__msg__RobotStatusMessage
    std::shared_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__custom_messages__msg__RobotStatusMessage
    std::shared_ptr<custom_messages::msg::RobotStatusMessage_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const RobotStatusMessage_ & other) const
  {
    if (this->enabled != other.enabled) {
      return false;
    }
    if (this->left_drivebase != other.left_drivebase) {
      return false;
    }
    if (this->right_drivebase != other.right_drivebase) {
      return false;
    }
    return true;
  }
  bool operator!=(const RobotStatusMessage_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct RobotStatusMessage_

// alias to use template instance with default allocator
using RobotStatusMessage =
  custom_messages::msg::RobotStatusMessage_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_HPP_
