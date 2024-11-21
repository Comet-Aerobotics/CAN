// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from custom_messages:srv/SparkPID.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_H_
#define CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Constant 'KP'.
enum
{
  custom_messages__srv__SparkPID_Request__KP = 13
};

/// Constant 'KI'.
enum
{
  custom_messages__srv__SparkPID_Request__KI = 14
};

/// Constant 'KD'.
enum
{
  custom_messages__srv__SparkPID_Request__KD = 15
};

/// Constant 'KF'.
enum
{
  custom_messages__srv__SparkPID_Request__KF = 16
};

/// Struct defined in srv/SparkPID in the package custom_messages.
typedef struct custom_messages__srv__SparkPID_Request
{
  /// Request Fields
  uint32_t id;
  uint8_t type;
  float setpoint;
  uint8_t slot;
} custom_messages__srv__SparkPID_Request;

// Struct for a sequence of custom_messages__srv__SparkPID_Request.
typedef struct custom_messages__srv__SparkPID_Request__Sequence
{
  custom_messages__srv__SparkPID_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_messages__srv__SparkPID_Request__Sequence;


// Constants defined in the message

/// Struct defined in srv/SparkPID in the package custom_messages.
typedef struct custom_messages__srv__SparkPID_Response
{
  uint8_t structure_needs_at_least_one_member;
} custom_messages__srv__SparkPID_Response;

// Struct for a sequence of custom_messages__srv__SparkPID_Response.
typedef struct custom_messages__srv__SparkPID_Response__Sequence
{
  custom_messages__srv__SparkPID_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_messages__srv__SparkPID_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CUSTOM_MESSAGES__SRV__DETAIL__SPARK_PID__STRUCT_H_
