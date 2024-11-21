// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from custom_messages:msg/SparkMaxMessage.idl
// generated code does not contain a copyright notice

#ifndef CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_H_
#define CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

/// Struct defined in msg/SparkMaxMessage in the package custom_messages.
typedef struct custom_messages__msg__SparkMaxMessage
{
  uint8_t device_id;
  float applied_output;
  float velocity;
  float position;
  uint8_t temperature;
  float voltage;
  float current;
} custom_messages__msg__SparkMaxMessage;

// Struct for a sequence of custom_messages__msg__SparkMaxMessage.
typedef struct custom_messages__msg__SparkMaxMessage__Sequence
{
  custom_messages__msg__SparkMaxMessage * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} custom_messages__msg__SparkMaxMessage__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // CUSTOM_MESSAGES__MSG__DETAIL__SPARK_MAX_MESSAGE__STRUCT_H_
