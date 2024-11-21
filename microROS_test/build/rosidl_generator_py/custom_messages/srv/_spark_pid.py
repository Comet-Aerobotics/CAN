# generated from rosidl_generator_py/resource/_idl.py.em
# with input from custom_messages:srv/SparkPID.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SparkPID_Request(type):
    """Metaclass of message 'SparkPID_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'KP': 13,
        'KI': 14,
        'KD': 15,
        'KF': 16,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('custom_messages')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'custom_messages.srv.SparkPID_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__spark_pid__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__spark_pid__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__spark_pid__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__spark_pid__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__spark_pid__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'KP': cls.__constants['KP'],
            'KI': cls.__constants['KI'],
            'KD': cls.__constants['KD'],
            'KF': cls.__constants['KF'],
        }

    @property
    def KP(self):
        """Message constant 'KP'."""
        return Metaclass_SparkPID_Request.__constants['KP']

    @property
    def KI(self):
        """Message constant 'KI'."""
        return Metaclass_SparkPID_Request.__constants['KI']

    @property
    def KD(self):
        """Message constant 'KD'."""
        return Metaclass_SparkPID_Request.__constants['KD']

    @property
    def KF(self):
        """Message constant 'KF'."""
        return Metaclass_SparkPID_Request.__constants['KF']


class SparkPID_Request(metaclass=Metaclass_SparkPID_Request):
    """
    Message class 'SparkPID_Request'.

    Constants:
      KP
      KI
      KD
      KF
    """

    __slots__ = [
        '_id',
        '_type',
        '_setpoint',
        '_slot',
    ]

    _fields_and_field_types = {
        'id': 'uint32',
        'type': 'uint8',
        'setpoint': 'float',
        'slot': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.id = kwargs.get('id', int())
        self.type = kwargs.get('type', int())
        self.setpoint = kwargs.get('setpoint', float())
        self.slot = kwargs.get('slot', int())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.id != other.id:
            return False
        if self.type != other.type:
            return False
        if self.setpoint != other.setpoint:
            return False
        if self.slot != other.slot:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property  # noqa: A003
    def id(self):  # noqa: A003
        """Message field 'id'."""
        return self._id

    @id.setter  # noqa: A003
    def id(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'id' field must be an unsigned integer in [0, 4294967295]"
        self._id = value

    @builtins.property  # noqa: A003
    def type(self):  # noqa: A003
        """Message field 'type'."""
        return self._type

    @type.setter  # noqa: A003
    def type(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'type' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'type' field must be an unsigned integer in [0, 255]"
        self._type = value

    @builtins.property
    def setpoint(self):
        """Message field 'setpoint'."""
        return self._setpoint

    @setpoint.setter
    def setpoint(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'setpoint' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'setpoint' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._setpoint = value

    @builtins.property
    def slot(self):
        """Message field 'slot'."""
        return self._slot

    @slot.setter
    def slot(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'slot' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'slot' field must be an unsigned integer in [0, 255]"
        self._slot = value


# Import statements for member types

# already imported above
# import rosidl_parser.definition


class Metaclass_SparkPID_Response(type):
    """Metaclass of message 'SparkPID_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('custom_messages')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'custom_messages.srv.SparkPID_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__spark_pid__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__spark_pid__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__spark_pid__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__spark_pid__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__spark_pid__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SparkPID_Response(metaclass=Metaclass_SparkPID_Response):
    """Message class 'SparkPID_Response'."""

    __slots__ = [
    ]

    _fields_and_field_types = {
    }

    SLOT_TYPES = (
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)


class Metaclass_SparkPID(type):
    """Metaclass of service 'SparkPID'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('custom_messages')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'custom_messages.srv.SparkPID')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__spark_pid

            from custom_messages.srv import _spark_pid
            if _spark_pid.Metaclass_SparkPID_Request._TYPE_SUPPORT is None:
                _spark_pid.Metaclass_SparkPID_Request.__import_type_support__()
            if _spark_pid.Metaclass_SparkPID_Response._TYPE_SUPPORT is None:
                _spark_pid.Metaclass_SparkPID_Response.__import_type_support__()


class SparkPID(metaclass=Metaclass_SparkPID):
    from custom_messages.srv._spark_pid import SparkPID_Request as Request
    from custom_messages.srv._spark_pid import SparkPID_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
