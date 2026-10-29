cmake_minimum_required(VERSION 3.8)
project(cometbot_can)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# Custom messages (moved here from microROS_test/extra_packages/custom_messages)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/SparkMaxMessage.msg"
  "msg/RobotStatusMessage.msg"
)

# SocketCAN + SPARK MAX code. No ROS inside, so it can be unit tested alone.
add_library(spark_can STATIC
  src/socket_can.cpp
  src/spark_max.cpp
)
target_include_directories(spark_can PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
)

# The ROS 2 node (replaces microROS_test/src/main.cpp)
add_executable(can_bridge src/can_bridge_node.cpp)
target_link_libraries(can_bridge spark_can)
ament_target_dependencies(can_bridge rclcpp std_msgs geometry_msgs)
rosidl_get_typesupport_target(cpp_typesupport_target ${PROJECT_NAME} "rosidl_typesupport_cpp")
target_link_libraries(can_bridge "${cpp_typesupport_target}")

install(TARGETS can_bridge DESTINATION lib/${PROJECT_NAME})
install(DIRECTORY launch config DESTINATION share/${PROJECT_NAME})
install(PROGRAMS scripts/setup_can.sh DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_cmake_gtest REQUIRED)
  ament_add_gtest(test_spark_max test/test_spark_max.cpp)
  target_link_libraries(test_spark_max spark_can)
endif()

ament_export_dependencies(rosidl_default_runtime)
ament_package()
