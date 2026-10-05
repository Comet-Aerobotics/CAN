#!/usr/bin/env python3
"""Make a ROS1-converted TUM RGB-D bag usable with ROS 2 tf2 / rtabmap.

- Strips the leading '/' from every frame_id (tf2 rejects them).
- Renames the mocap ground-truth transform world->kinect to world->kinect_gt
  so it doesn't conflict with rtabmap's odom->kinect.
- Drops /cortex_marker_array (does not deserialize after conversion).

Usage: python3 fix_tum_bag.py fr1_xyz fr1_xyz_fixed
Run with /usr/bin/python3 after sourcing /opt/ros/humble/setup.bash.
"""
import sys

import rosbag2_py
from rclpy.serialization import deserialize_message, serialize_message
from rosidl_runtime_py.utilities import get_message

SKIP = {'/cortex_marker_array'}


def fix(frame):
    return frame.lstrip('/')


def main(src, dst):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=src, storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))
    writer = rosbag2_py.SequentialWriter()
    writer.open(rosbag2_py.StorageOptions(uri=dst, storage_id='sqlite3'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))

    types = {}
    for meta in reader.get_all_topics_and_types():
        if meta.name in SKIP:
            continue
        types[meta.name] = get_message(meta.type)
        writer.create_topic(meta)

    while reader.has_next():
        topic, data, stamp = reader.read_next()
        if topic in SKIP:
            continue
        msg = deserialize_message(data, types[topic])
        if topic in ('/tf', '/tf_static'):
            for t in msg.transforms:
                t.header.frame_id = fix(t.header.frame_id)
                t.child_frame_id = fix(t.child_frame_id)
                if t.header.frame_id == 'world' and t.child_frame_id == 'kinect':
                    t.child_frame_id = 'kinect_gt'
        elif hasattr(msg, 'header'):
            msg.header.frame_id = fix(msg.header.frame_id)
        writer.write(topic, serialize_message(msg), stamp)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
