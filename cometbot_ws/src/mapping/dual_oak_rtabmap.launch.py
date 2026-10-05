"""RTAB-Map SLAM with two OAK-D Pro cameras (front + back), viewed in Foxglove.

Pipeline:
  oak_front / oak_back (depthai_ros_driver, RGB + aligned depth)
    -> rgbd_sync per camera -> rgbdx_sync (combines both)
    -> rgbd_odometry (odom -> base_link) -> rtabmap (map -> odom)
  imu_filter_madgwick turns the front camera's raw IMU into /imu/data.
  foxglove_bridge serves everything on ws://localhost:<foxglove_port>.

Run through run_dual_oak_rtabmap.sh, or directly:
  ros2 launch dual_oak_rtabmap.launch.py front_mxid:=<id> back_mxid:=<id>
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

HERE = os.path.dirname(os.path.abspath(__file__))

# Each entry: camera name -> prefix of its mounting launch arguments.
CAMERAS = {'oak_front': 'front', 'oak_back': 'back'}


def camera_driver(name, prefix, params_file):
    depthai_launch = os.path.join(
        get_package_share_directory('depthai_ros_driver'), 'launch', 'camera.launch.py')
    return IncludeLaunchDescription(
        PythonLaunchDescriptionSource(depthai_launch),
        launch_arguments={
            'name': name,
            'camera_model': 'OAK-D-PRO',
            'parent_frame': 'base_link',
            'params_file': params_file,
            'cam_pos_x': LaunchConfiguration(f'{prefix}_x'),
            'cam_pos_y': LaunchConfiguration(f'{prefix}_y'),
            'cam_pos_z': LaunchConfiguration(f'{prefix}_z'),
            'cam_roll': '0.0',
            'cam_pitch': LaunchConfiguration(f'{prefix}_pitch'),
            'cam_yaw': LaunchConfiguration(f'{prefix}_yaw'),
        }.items(),
    )


def rgbd_sync(name):
    return Node(
        package='rtabmap_sync', executable='rgbd_sync', name='rgbd_sync',
        namespace=name, output='screen',
        parameters=[{'approx_sync': True, 'approx_sync_max_interval': 0.02}],
        remappings=[
            ('rgb/image', f'/{name}/rgb/image_rect'),
            ('rgb/camera_info', f'/{name}/rgb/camera_info'),
            ('depth/image', f'/{name}/stereo/image_raw'),
            ('rgbd_image', f'/{name}/rgbd_image'),
        ],
    )


def launch_setup(context):
    use_imu = LaunchConfiguration('use_imu').perform(context) == 'true'
    localization = LaunchConfiguration('localization').perform(context) == 'true'
    fresh_map = LaunchConfiguration('fresh_map').perform(context) == 'true'

    # The apt build of rtabmap has no OpenGV, so multi-camera registration
    # must be 3D->3D (Vis/EstimationType 0) instead of PnP.
    common = {
        'frame_id': 'base_link',
        'Vis/EstimationType': '0',
        'wait_imu_to_init': use_imu,
    }
    imu_remap = [('imu', '/imu/data')] if use_imu else []

    slam_params = dict(common, **{
        'subscribe_sensor_data': True,
        'subscribe_odom_info': True,
        'approx_sync': False,
        'database_path': LaunchConfiguration('database_path').perform(context),
        'Mem/IncrementalMemory': 'false' if localization else 'true',
        'Mem/InitWMWithAllNodes': 'true' if localization else 'false',
        'Grid/3D': 'false',
        'Grid/RayTracing': 'true',
        'Grid/RangeMax': '4.0',
        'Grid/MaxGroundHeight': '0.05',
        'Grid/MaxObstacleHeight': '1.0',
    })

    actions = [
        camera_driver(name, prefix, LaunchConfiguration('params_file'))
        for name, prefix in CAMERAS.items()
    ]
    actions += [rgbd_sync(name) for name in CAMERAS]

    actions += [
        # The two OAKs are not hardware-synced, so pair frames within half a
        # frame period (30 fps).
        Node(
            package='rtabmap_sync', executable='rgbdx_sync', namespace='rtabmap',
            output='screen',
            parameters=[{
                'rgbd_cameras': 2,
                'approx_sync': True,
                'approx_sync_max_interval': 0.017,
            }],
            remappings=[
                ('rgbd_image0', '/oak_front/rgbd_image'),
                ('rgbd_image1', '/oak_back/rgbd_image'),
            ],
        ),
        Node(
            package='rtabmap_odom', executable='rgbd_odometry', namespace='rtabmap',
            output='screen',
            parameters=[dict(common, **{
                'subscribe_rgbd': True,
                'rgbd_cameras': 0,  # 0 = subscribe to rgbd_images from rgbdx_sync
                'odom_frame_id': 'odom',
                'publish_tf': True,
            })],
            remappings=imu_remap,
        ),
        Node(
            package='rtabmap_slam', executable='rtabmap', namespace='rtabmap',
            output='screen',
            parameters=[slam_params],
            remappings=[('sensor_data', 'odom_sensor_data/raw')] + imu_remap,
            arguments=['--delete_db_on_start'] if fresh_map and not localization else [],
        ),
        Node(
            package='foxglove_bridge', executable='foxglove_bridge', output='screen',
            parameters=[{
                'port': int(LaunchConfiguration('foxglove_port').perform(context)),
                'address': '0.0.0.0',
            }],
        ),
    ]

    if use_imu:
        actions.append(Node(
            package='imu_filter_madgwick', executable='imu_filter_madgwick_node',
            output='screen',
            parameters=[{'use_mag': False, 'world_frame': 'enu', 'publish_tf': False}],
            remappings=[('imu/data_raw', '/oak_front/imu/data'), ('imu/data', '/imu/data')],
        ))

    return actions


def generate_launch_description():
    args = [
        DeclareLaunchArgument('front_mxid', default_value='',
                              description='MXID of the front OAK (empty = first found)'),
        DeclareLaunchArgument('back_mxid', default_value='',
                              description='MXID of the back OAK (empty = first found)'),
        DeclareLaunchArgument('params_file',
                              default_value=os.path.join(HERE, 'config', 'dual_oak.yaml')),
        # Camera mounting relative to base_link (metres / radians).
        # PLACEHOLDERS: measure these on the robot.
        DeclareLaunchArgument('front_x', default_value='0.30'),
        DeclareLaunchArgument('front_y', default_value='0.0'),
        DeclareLaunchArgument('front_z', default_value='0.20'),
        DeclareLaunchArgument('front_pitch', default_value='0.0'),
        DeclareLaunchArgument('front_yaw', default_value='0.0'),
        DeclareLaunchArgument('back_x', default_value='-0.30'),
        DeclareLaunchArgument('back_y', default_value='0.0'),
        DeclareLaunchArgument('back_z', default_value='0.20'),
        DeclareLaunchArgument('back_pitch', default_value='0.0'),
        DeclareLaunchArgument('back_yaw', default_value='3.14159265'),
        DeclareLaunchArgument('use_imu', default_value='true',
                              description='Use the front OAK IMU for odometry and SLAM'),
        DeclareLaunchArgument('localization', default_value='false',
                              description='Localize in an existing map instead of mapping'),
        DeclareLaunchArgument('fresh_map', default_value='true',
                              description='Delete the database on start (mapping mode only)'),
        DeclareLaunchArgument('database_path',
                              default_value=os.path.expanduser('~/.ros/rtabmap_dual_oak.db')),
        DeclareLaunchArgument('foxglove_port', default_value='8765'),
    ]
    return LaunchDescription(args + [OpaqueFunction(function=launch_setup)])
