cmake_minimum_required(VERSION 3.8)
project(custom_messages)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

find_package(rosidl_default_generators REQUIRED)

file(GLOB SOURCES "src/pid_client.cpp")

add_executable(executable1 src/main.cpp lib/CAN_Device_Interface/CAN_Device_Interface.h lib/Comet_CAN_Common/Comet_CAN_Common.h lib/Comet_CAN_Helper/Comet_CAN_Helper.cpp lib/SPARK_MAX/SPARK_MAX.cpp lib/PDP/PDP.cpp)
add_executable(executable2 pid_client.cpp )

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SparkMaxMessage.msg"
  "msg/RobotStatusMessage.msg"
  "srv/SparkPID.srv"
 )

ament_package()