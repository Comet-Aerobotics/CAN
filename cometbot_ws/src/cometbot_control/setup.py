from setuptools import find_packages, setup

package_name = 'cometbot_control'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/mission_sim.launch.py', 'launch/test_excavator.launch.py', 'launch/test_cycle.launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='amadorjosephg',
    maintainer_email='amadorjosephg@gmail.com',
    description='Control Package for test lunabot',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'teleop_publisher = cometbot_control.teleop_publisher:main',
            'mission_orchestrator = cometbot_control.mission_orchestrator:main',
            'excavator_action_server = cometbot_control.excavator_action_server:main',
            'mock_hardware = cometbot_control.scripts.mock_hardware:main',
            'excavator_test_client = cometbot_control.scripts.excavator_test_client:main',
            'cycle_test = cometbot_control.scripts.cycle_test_client:main',
            'depositor_action_server = cometbot_control.depositor_action_server:main',
            'load_sensor = cometbot_control.sensors.load_sensor:main',
        ],
    },
)
