from launch import LaunchDescription
from launch.actions import TimerAction, RegisterEventHandler, EmitEvent
from launch.event_handlers import OnProcessExit
from launch.events import Shutdown
from launch_ros.actions import Node


def generate_launch_description():
    excavator = Node(
        package='cometbot_control',
        executable='excavator_action_server',
        name='excavator_action_server',
        output='screen',
    )

    depositor = Node(
        package='cometbot_control',
        executable='depositor_action_server',
        name='depositor_action_server',
        output='screen',
    )

    mock = Node(
        package='cometbot_control',
        executable='mock_hardware',
        name='mock_hardware',
        output='screen',
    )

    # Start the cycle test client after a short delay
    cycle_client = Node(
        package='cometbot_control',
        executable='cycle_test',
        name='cycle_test_client',
        output='screen',
        arguments=['12', '5.0'],
    )

    delayed_client = TimerAction(period=2.0, actions=[cycle_client])

    # When the cycle client process exits, shut down the whole launch
    shutdown_on_finish = RegisterEventHandler(
        OnProcessExit(
            target_action=cycle_client,
            on_exit=[EmitEvent(event=Shutdown())],
        )
    )

    return LaunchDescription([
        excavator,
        depositor,
        mock,
        delayed_client,
        shutdown_on_finish,
    ])
