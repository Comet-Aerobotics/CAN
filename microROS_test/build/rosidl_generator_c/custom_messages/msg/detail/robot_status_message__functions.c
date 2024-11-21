// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice
#include "custom_messages/msg/detail/robot_status_message__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `left_drivebase`
// Member `right_drivebase`
#include "custom_messages/msg/detail/spark_max_message__functions.h"

bool
custom_messages__msg__RobotStatusMessage__init(custom_messages__msg__RobotStatusMessage * msg)
{
  if (!msg) {
    return false;
  }
  // enabled
  // left_drivebase
  if (!custom_messages__msg__SparkMaxMessage__init(&msg->left_drivebase)) {
    custom_messages__msg__RobotStatusMessage__fini(msg);
    return false;
  }
  // right_drivebase
  if (!custom_messages__msg__SparkMaxMessage__init(&msg->right_drivebase)) {
    custom_messages__msg__RobotStatusMessage__fini(msg);
    return false;
  }
  return true;
}

void
custom_messages__msg__RobotStatusMessage__fini(custom_messages__msg__RobotStatusMessage * msg)
{
  if (!msg) {
    return;
  }
  // enabled
  // left_drivebase
  custom_messages__msg__SparkMaxMessage__fini(&msg->left_drivebase);
  // right_drivebase
  custom_messages__msg__SparkMaxMessage__fini(&msg->right_drivebase);
}

bool
custom_messages__msg__RobotStatusMessage__are_equal(const custom_messages__msg__RobotStatusMessage * lhs, const custom_messages__msg__RobotStatusMessage * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // enabled
  if (lhs->enabled != rhs->enabled) {
    return false;
  }
  // left_drivebase
  if (!custom_messages__msg__SparkMaxMessage__are_equal(
      &(lhs->left_drivebase), &(rhs->left_drivebase)))
  {
    return false;
  }
  // right_drivebase
  if (!custom_messages__msg__SparkMaxMessage__are_equal(
      &(lhs->right_drivebase), &(rhs->right_drivebase)))
  {
    return false;
  }
  return true;
}

bool
custom_messages__msg__RobotStatusMessage__copy(
  const custom_messages__msg__RobotStatusMessage * input,
  custom_messages__msg__RobotStatusMessage * output)
{
  if (!input || !output) {
    return false;
  }
  // enabled
  output->enabled = input->enabled;
  // left_drivebase
  if (!custom_messages__msg__SparkMaxMessage__copy(
      &(input->left_drivebase), &(output->left_drivebase)))
  {
    return false;
  }
  // right_drivebase
  if (!custom_messages__msg__SparkMaxMessage__copy(
      &(input->right_drivebase), &(output->right_drivebase)))
  {
    return false;
  }
  return true;
}

custom_messages__msg__RobotStatusMessage *
custom_messages__msg__RobotStatusMessage__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  custom_messages__msg__RobotStatusMessage * msg = (custom_messages__msg__RobotStatusMessage *)allocator.allocate(sizeof(custom_messages__msg__RobotStatusMessage), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(custom_messages__msg__RobotStatusMessage));
  bool success = custom_messages__msg__RobotStatusMessage__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
custom_messages__msg__RobotStatusMessage__destroy(custom_messages__msg__RobotStatusMessage * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    custom_messages__msg__RobotStatusMessage__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
custom_messages__msg__RobotStatusMessage__Sequence__init(custom_messages__msg__RobotStatusMessage__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  custom_messages__msg__RobotStatusMessage * data = NULL;

  if (size) {
    data = (custom_messages__msg__RobotStatusMessage *)allocator.zero_allocate(size, sizeof(custom_messages__msg__RobotStatusMessage), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = custom_messages__msg__RobotStatusMessage__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        custom_messages__msg__RobotStatusMessage__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
custom_messages__msg__RobotStatusMessage__Sequence__fini(custom_messages__msg__RobotStatusMessage__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      custom_messages__msg__RobotStatusMessage__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

custom_messages__msg__RobotStatusMessage__Sequence *
custom_messages__msg__RobotStatusMessage__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  custom_messages__msg__RobotStatusMessage__Sequence * array = (custom_messages__msg__RobotStatusMessage__Sequence *)allocator.allocate(sizeof(custom_messages__msg__RobotStatusMessage__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = custom_messages__msg__RobotStatusMessage__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
custom_messages__msg__RobotStatusMessage__Sequence__destroy(custom_messages__msg__RobotStatusMessage__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    custom_messages__msg__RobotStatusMessage__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
custom_messages__msg__RobotStatusMessage__Sequence__are_equal(const custom_messages__msg__RobotStatusMessage__Sequence * lhs, const custom_messages__msg__RobotStatusMessage__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!custom_messages__msg__RobotStatusMessage__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
custom_messages__msg__RobotStatusMessage__Sequence__copy(
  const custom_messages__msg__RobotStatusMessage__Sequence * input,
  custom_messages__msg__RobotStatusMessage__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(custom_messages__msg__RobotStatusMessage);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    custom_messages__msg__RobotStatusMessage * data =
      (custom_messages__msg__RobotStatusMessage *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!custom_messages__msg__RobotStatusMessage__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          custom_messages__msg__RobotStatusMessage__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!custom_messages__msg__RobotStatusMessage__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
