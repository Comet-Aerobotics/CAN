// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_H_
#define CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'left_drivebase'
// Member 'right_drivebase'
#include "custom_messages/msg/detail/spark_max_message__struct.h"

/// Struct defined in msg/RobotStatusMessage in the package custom_messages.
typedef struct custom_messages__msg__RobotStatusMessage
{
  bool enabled;
  custom_messages__msg__SparkMaxMessage left_drivebase;
  custom_messages__msg__SparkMaxMessage right_drivebase;
} custom_messages__msg__RobotStatusMessage;

// Struct for a sequence of custom_messages__msg__RobotStatusMessage.
typedef struct custom_messages__msg__RobotStatusMessage__Sequence
{
  custom_messages__msg__RobotStatusMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_messages__msg__RobotStatusMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__ROBOT_STATUS_MESSAGE__STRUCT_H_
