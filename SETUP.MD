WSL Environment Setup (experimental)
From (https://docs.docker.com/desktop/setup/install/windows-install/):
Enable WSL
wsl --install
Install Docker Desktop
Running the client for the first time:
docker run -it --net=host -v /dev:/dev --privileged --name microros ros:humble (from a normal terminal)
Then, follow the instructions at the link here (transcribed here)

Installing ROS 2 and the micro-ROS build system

First of all, install ROS 2 Humble Hawksbill on your Ubuntu 22.04 LTS computer. To do so from binaries, via Debian packages, follow the instructions detailed here.

TIP: Alternatively, you can use a docker container with a fresh ROS 2 Humble installation. The one that serves the purpose is the container run by the command:

docker run -it --net=host -v /dev:/dev --privileged ros:humble

Once you have a ROS 2 installation in the computer, follow these steps to install the micro-ROS build system:

# Source the ROS 2 installation
source /opt/ros/$ROS_DISTRO/setup.bash

# Create a workspace and download the micro-ROS tools
mkdir microros_ws
cd microros_ws
git clone -b $ROS_DISTRO https://github.com/micro-ROS/micro_ros_setup.git src/micro_ros_setup

# Update dependencies using rosdep
sudo apt update && rosdep update
rosdep install --from-paths src --ignore-src -y

# Install pip
sudo apt-get install python3-pip

# Build micro-ROS tools and source them
colcon build
source install/local_setup.bash

These instructions will setup a workspace with a ready-to-use micro-ROS build system. This build system is in charge of downloading the required cross-compilation tools and building the apps for the required platforms.

The build system’s workflow is a four-step procedure:

    Create step: This step is in charge of downloading all the required code repositories and cross-compilation toolchains for the specific hardware platform. Among these repositories, it will also download a collection of ready to use micro-ROS apps.
    Configure step: In this step, the user can select which app is going to be cross-compiled by the toolchain. Some other options, such as transport, agent’s IP address/port (for UDP transport) or device ID (for serial connections) will be also selected in this step.
    Build step: Here is where the cross-compilation takes place and the platform-specific binaries are generated.
    Flash step: The binaries generated in the previous step are flashed onto the hardware platform memory, in order to allow the execution of the micro-ROS app. Further information about micro-ROS build system can be found here.

Creating a new firmware workspace

Once the build system is installed, let’s create a firmware workspace that targets all the required code and tools:

# Create firmware step
ros2 run micro_ros_setup create_firmware_ws.sh host

Once the command is executed, a folder named firmware must be present in your workspace.

This step is in charge, among other things, of downloading a set of micro-ROS apps for Linux, that are located at src/uros/micro-ROS-demos/rclc. Each app is represented by a folder containing the following files:

    main.c: This file contains the logic of the application.
    CMakeLists.txt: This is the CMake file containing the script to compile the application.

For the user to create a custom application, a folder <my_app> will need to be registered in this location, containing the two files just described. Also, any such new application folder needs to be registered in src/uros/micro-ROS-demos/rclc/CMakeLists.txt by adding the following line:

export_executable(<my_app>)

In this tutorial, we will focus on the out-of-the-box ping_pong application located at src/uros/micro-ROS-demos/rclc/ping_pong. You can check the complete content of this app here.

This example showcases a micro-ROS node with two publisher-subscriber pairs associated with a ping and a pong topics, respectively. The node sends a ping package with a unique identifier, using a ping publisher. If the ping subscriber receives a ping from an external node, the pong publisher responds to the incoming ping with a pong. To test that this logic is correctly functioning, we implement communication with a ROS 2 node that:

    Listens to the topics published by the ping subscriber.
    Publishes a fake_ping package, that is received by the micro-ROS ping subscriber. As a consequence, the pong publisher on the micro-ROS application will publish a pong, to signal that it received the fake_ping correctly.

The diagram below clarifies the communication flow between these entities:

pingpong

The contents of the host app specific files can be found here: main.c and CMakeLists.txt. A thorough review of these files is illustrative of how to create a micro-ROS app in this RTOS.
Building the firmware

Once the app has been created, the build step is in order. Notice that, with respect to the four-steps workflow delined above, we would expect a configuration step to happen before building the app. However, given that we are compiling micro-ROS in the host machine rather than in a board, the cross-compilation implemented by the configuration step is not required in this case. We can therefore proceed to build the firmware and source the local installation:

# Build step
ros2 run micro_ros_setup build_firmware.sh
source install/local_setup.bash

Creating the micro-ROS agent

The micro-ROS app is now ready to be connected to a micro-ROS agent to start talking with the rest of the ROS 2 world. To do that, let’s first of all create a micro-ROS agent:

# Download micro-ROS-Agent packages
ros2 run micro_ros_setup create_agent_ws.sh

Now, let’s build the agent packages and, when this is done, source the installation:

# Build step
ros2 run micro_ros_setup build_agent.sh
source install/local_setup.bash

Add micro-ROS environment to bashrc (optional)

You can add the ROS 2 and micro-ROS workspace setup files to your .bashrc so the files do not have to be sourced every time a new command line is opened.

echo source /opt/ros/$ROS_DISTRO/setup.bash >> ~/.bashrc
echo source ~/microros_ws/install/local_setup.bash >> ~/.bashrc



Once you have setup the client for the first time, you can simply use docker exec -it microros /bin/bash from a terminal to get an interactive session, or use docker desktop if you’re a PSYCHOPATH 
On windows, use settings (ctrl + ,) within a terminal, then create a new profile with %SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe docker exec -it microros /bin/bash for one click awesomeness
Install VSCode, and integrate with WSL on windows
Get platformio, remote extension pack, etc
(see steps starting from step 3 0.1.0 UPDATED Environment Setup)
From a VSCode terminal:(open with wsl by cloning git, navigating to folder, and code .)
Test by cloning github: git clone https://github.com/Comet-Aerobotics/CAN.git 
sudo apt-get update
sudo apt install cmake ninja
sudo apt-get install libpython3-dev
sudo apt-get install python3-venv
Then install platformbuild microros-test using platformio
Test Build
Microros Build
Press Control+Shift+P and run CMake:Configure. Then open src/main.cpp and see if you can run pio build (from checkmark in corner)
Python Build
In VScode, open ~/CAN/cometbot_ws. Then, in a terminal run colcon build. Then, see if you can run “ros2 run joy joy_node”, control+c out of it, then run ros2 run cometbot_control teleop_publisher

