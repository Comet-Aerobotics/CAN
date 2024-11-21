// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from custom_messages:srv/SparkPID.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_HPP_
#define CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__custom_messages__srv__SparkPID_Request __attribute__((deprecated))
#else
# define DEPRECATED__custom_messages__srv__SparkPID_Request __declspec(deprecated)
#endif

namespace custom_messages
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SparkPID_Request_
{
  using Type = SparkPID_Request_<ContainerAllocator>;

  explicit SparkPID_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0ul;
      this->type = 0;
      this->setpoint = 0.0f;
      this->slot = 0;
    }
  }

  explicit SparkPID_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->id = 0ul;
      this->type = 0;
      this->setpoint = 0.0f;
      this->slot = 0;
    }
  }

  // field types and members
  using _id_type =
    uint32_t;
  _id_type id;
  using _type_type =
    uint8_t;
  _type_type type;
  using _setpoint_type =
    float;
  _setpoint_type setpoint;
  using _slot_type =
    uint8_t;
  _slot_type slot;

  // setters for named parameter idiom
  Type & set__id(
    const uint32_t & _arg)
  {
    this->id = _arg;
    return *this;
  }
  Type & set__type(
    const uint8_t & _arg)
  {
    this->type = _arg;
    return *this;
  }
  Type & set__setpoint(
    const float & _arg)
  {
    this->setpoint = _arg;
    return *this;
  }
  Type & set__slot(
    const uint8_t & _arg)
  {
    this->slot = _arg;
    return *this;
  }

  // constant declarations
  static constexpr uint8_t KP =
    13u;
  static constexpr uint8_t KI =
    14u;
  static constexpr uint8_t KD =
    15u;
  static constexpr uint8_t KF =
    16u;

  // pointer types
  using RawPtr =
    custom_messages::srv::SparkPID_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const custom_messages::srv::SparkPID_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      custom_messages::srv::SparkPID_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      custom_messages::srv::SparkPID_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__custom_messages__srv__SparkPID_Request
    std::shared_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__custom_messages__srv__SparkPID_Request
    std::shared_ptr<custom_messages::srv::SparkPID_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SparkPID_Request_ & other) const
  {
    if (this->id != other.id) {
      return false;
    }
    if (this->type != other.type) {
      return false;
    }
    if (this->setpoint != other.setpoint) {
      return false;
    }
    if (this->slot != other.slot) {
      return false;
    }
    return true;
  }
  bool operator!=(const SparkPID_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SparkPID_Request_

// alias to use template instance with default allocator
using SparkPID_Request =
  custom_messages::srv::SparkPID_Request_<std::allocator<void>>;

// constant definitions
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SparkPID_Request_<ContainerAllocator>::KP;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SparkPID_Request_<ContainerAllocator>::KI;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SparkPID_Request_<ContainerAllocator>::KD;
#endif  // __cplusplus < 201703L
#if __cplusplus < 201703L
// static constexpr member variable definitions are only needed in C++14 and below, deprecated in C++17
template<typename ContainerAllocator>
constexpr uint8_t SparkPID_Request_<ContainerAllocator>::KF;
#endif  // __cplusplus < 201703L

}  // namespace srv

}  // namespace custom_messages


#ifndef _WIN32
# define DEPRECATED__custom_messages__srv__SparkPID_Response __attribute__((deprecated))
#else
# define DEPRECATED__custom_messages__srv__SparkPID_Response __declspec(deprecated)
#endif

namespace custom_messages
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SparkPID_Response_
{
  using Type = SparkPID_Response_<ContainerAllocator>;

  explicit SparkPID_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  explicit SparkPID_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    (void)_alloc;
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->structure_needs_at_least_one_member = 0;
    }
  }

  // field types and members
  using _structure_needs_at_least_one_member_type =
    uint8_t;
  _structure_needs_at_least_one_member_type structure_needs_at_least_one_member;


  // constant declarations

  // pointer types
  using RawPtr =
    custom_messages::srv::SparkPID_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const custom_messages::srv::SparkPID_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      custom_messages::srv::SparkPID_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      custom_messages::srv::SparkPID_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__custom_messages__srv__SparkPID_Response
    std::shared_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__custom_messages__srv__SparkPID_Response
    std::shared_ptr<custom_messages::srv::SparkPID_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SparkPID_Response_ & other) const
  {
    if (this->structure_needs_at_least_one_member != other.structure_needs_at_least_one_member) {
      return false;
    }
    return true;
  }
  bool operator!=(const SparkPID_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SparkPID_Response_

// alias to use template instance with default allocator
using SparkPID_Response =
  custom_messages::srv::SparkPID_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace custom_messages

namespace custom_messages
{

namespace srv
{

struct SparkPID
{
  using Request = custom_messages::srv::SparkPID_Request;
  using Response = custom_messages::srv::SparkPID_Response;
};

}  // namespace srv

}  // namespace custom_messages

#endif  // CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_HPP_
