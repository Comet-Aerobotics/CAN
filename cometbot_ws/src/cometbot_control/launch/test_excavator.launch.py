from launch import LaunchDescription
from launch.actions import TimerAction, RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.actions import Node


def generate_launch_description():
    server_node = Node(
        package='cometbot_control',
        executable='excavator_action_server',
        name='excavator_action_server',
        output='screen',
    )

    mock_node = Node(
        package='cometbot_control',
        executable='mock_hardware',
        name='mock_hardware',
        output='screen',
    )

    # Start test client after a short delay so server and mock initialize
    test_client_node = Node(
        package='cometbot_control',
        executable='excavator_test_client',
        name='excavator_test_client',
        output='screen',
        arguments=['12'],
    )

    delayed_test = TimerAction(period=2.0, actions=[test_client_node])

    shutdown_on_finish = RegisterEventHandler(
        OnProcessExit(
            target_action=test_client_node,
            on_exit=[EmitEvent(event=Shutdown())],
        )
    )

    return LaunchDescription([
        server_node,
        mock_node,
        delayed_test,
        shutdown_on_finish,
    ])
