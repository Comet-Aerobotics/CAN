cmake_minimum_required(VERSION 3.8)
project(cometbot_msgs)

# 1. Compilation Options
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# 2. Find Dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(action_msgs REQUIRED)

# 3. Generate Interfaces 
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Excavate.action"
  "action/Deposit.action"
  "msg/RobotStatusMessage.msg"
  DEPENDENCIES action_msgs
)

# 4. Testing 
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# 5. Export Package
ament_package()