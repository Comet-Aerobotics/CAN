// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from custom_messages:msg/RobotStatusMessage.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "custom_messages/msg/detail/robot_status_message__struct.h"
#include "custom_messages/msg/detail/robot_status_message__functions.h"

bool custom_messages__msg__spark_max_message__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * custom_messages__msg__spark_max_message__convert_to_py(void * raw_ros_message);
bool custom_messages__msg__spark_max_message__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * custom_messages__msg__spark_max_message__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool custom_messages__msg__robot_status_message__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[61];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("custom_messages.msg._robot_status_message.RobotStatusMessage", full_classname_dest, 60) == 0);
  }
  custom_messages__msg__RobotStatusMessage * ros_message = _ros_message;
  {  // enabled
    PyObject * field = PyObject_GetAttrString(_pymsg, "enabled");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->enabled = (Py_True == field);
    Py_DECREF(field);
  }
  {  // left_drivebase
    PyObject * field = PyObject_GetAttrString(_pymsg, "left_drivebase");
    if (!field) {
      return false;
    }
    if (!custom_messages__msg__spark_max_message__convert_from_py(field, &ros_message->left_drivebase)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // right_drivebase
    PyObject * field = PyObject_GetAttrString(_pymsg, "right_drivebase");
    if (!field) {
      return false;
    }
    if (!custom_messages__msg__spark_max_message__convert_from_py(field, &ros_message->right_drivebase)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * custom_messages__msg__robot_status_message__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of RobotStatusMessage */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("custom_messages.msg._robot_status_message");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "RobotStatusMessage");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  custom_messages__msg__RobotStatusMessage * ros_message = (custom_messages__msg__RobotStatusMessage *)raw_ros_message;
  {  // enabled
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->enabled ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "enabled", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // left_drivebase
    PyObject * field = NULL;
    field = custom_messages__msg__spark_max_message__convert_to_py(&ros_message->left_drivebase);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "left_drivebase", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // right_drivebase
    PyObject * field = NULL;
    field = custom_messages__msg__spark_max_message__convert_to_py(&ros_message->right_drivebase);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "right_drivebase", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
