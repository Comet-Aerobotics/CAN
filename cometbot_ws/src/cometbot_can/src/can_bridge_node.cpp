// can_bridge: ROS 2 node that drives the SPARK MAXs through a USB-CAN adapter.
//
// This replaces microROS_test/src/main.cpp. Same job, same topics, same
// timers. It just runs on the mini PC as a normal ROS 2 node instead of on the
// ESP32 through micro-ROS, and it talks to CAN through SocketCAN instead of
// the MCP2515 chip.
//
//   Old (ESP32)                         New (mini PC)
//   setup()                             CanBridgeNode constructor
//   loop() / rclc_executor_spin         rclcpp::spin in main()
//   rclc_timer_init_default             create_wall_timer
//   rclc_subscription_init_default      create_subscription
//   MCP_CAN CAN0 + Comet_CAN_Helper     SocketCan bus_
//   error_loop() + ESP.restart()        exit with an error, launch file restarts it
//   micro_ROS_logging topic             normal ROS logs (RCLCPP_INFO etc.)
//
// Topics (unchanged from main branch firmware):
//   sub  cmd_vel                       geometry_msgs/Twist   drive base
//   sub  depositor/position_setpoint   std_msgs/Float32      rotations
//   sub  excavator/actuator_output     std_msgs/Float32      -1..1 duty cycle
//   sub  excavator/velocity_setpoint   std_msgs/Float32      RPM
//   sub  enabled                       std_msgs/Bool         master enable
//   pub  robot_data                    cometbot_can/RobotStatusMessage

#include <algorithm>
#include <cerrno>
#include <chrono>
#include <cmath>
#include <memory>
#include <set>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

#include "geometry_msgs/msg/twist.hpp"
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/bool.hpp"
#include "std_msgs/msg/float32.hpp"

#include "cometbot_can/msg/robot_status_message.hpp"
#include "cometbot_can/msg/spark_max_message.hpp"
#include "cometbot_can/socket_can.hpp"
#include "cometbot_can/spark_max.hpp"

using namespace std::chrono_literals;

namespace cometbot_can
{

class CanBridgeNode : public rclcpp::Node
{
public:
  CanBridgeNode()
  : Node("can_bridge")
  {
    // ------------------------------------------------------------------
    // Parameters: settings you can change in config/can_bridge.yaml
    // without recompiling. CAN IDs are parameters now because the two git
    // branches disagree about them; set them to match the real robot.
    // ------------------------------------------------------------------
    const std::string interface = declare_parameter<std::string>("can_interface", "can0");
    const int64_t left_id = declare_parameter<int64_t>("drive_left_id", 11);
    const int64_t right_id = declare_parameter<int64_t>("drive_right_id", 10);
    const int64_t depositor_id = declare_parameter<int64_t>("depositor_id", 12);
    const int64_t actuator_id = declare_parameter<int64_t>("excavator_actuator_id", 13);
    const int64_t excavator_id = declare_parameter<int64_t>("excavator_motor_id", 14);

    depositor_min_ = declare_parameter<double>("depositor_min_position", -1000.0);
    depositor_max_ = declare_parameter<double>("depositor_max_position", 1000.0);
    actuator_min_ = declare_parameter<double>("excavator_output_min", -1.0);
    actuator_max_ = declare_parameter<double>("excavator_output_max", 1.0);
    excavator_vel_min_ = declare_parameter<double>("excavator_velocity_min", -5000.0);
    excavator_vel_max_ = declare_parameter<double>("excavator_velocity_max", 5000.0);

    // The old firmware swapped the turn direction when driving backwards
    // (feels natural on a joystick). Nav2 expects normal differential drive,
    // so the mapping team will probably want this false.
    invert_turn_when_reversing_ = declare_parameter<bool>("invert_turn_when_reversing", true);

    // Old firmware defaulted to enabled=true "ONLY FOR TESTING". Safer default
    // here is false: motors stay off until someone publishes enabled=true.
    enabled_ = declare_parameter<bool>("start_enabled", false);

    // ------------------------------------------------------------------
    // CAN setup (was setup_CAN)
    // ------------------------------------------------------------------
    bus_ = std::make_unique<SocketCan>(interface);  // throws if can0 isn't there
    RCLCPP_INFO(get_logger(), "Opened CAN interface '%s'", interface.c_str());

    drive_left_ = std::make_unique<SparkMax>(checked_id(left_id, "drive_left_id"));
    drive_right_ = std::make_unique<SparkMax>(checked_id(right_id, "drive_right_id"));
    depositor_ = std::make_unique<SparkMax>(checked_id(depositor_id, "depositor_id"));
    excavator_actuator_ =
      std::make_unique<SparkMax>(checked_id(actuator_id, "excavator_actuator_id"));
    excavator_motor_ =
      std::make_unique<SparkMax>(checked_id(excavator_id, "excavator_motor_id"));
    devices_ = {drive_left_.get(), drive_right_.get(), depositor_.get(),
      excavator_actuator_.get(), excavator_motor_.get()};

    std::set<uint8_t> seen;
    for (auto * device : devices_) {
      if (!seen.insert(device->device_id()).second) {
        throw std::runtime_error(
                "Two motors have the same CAN ID " + std::to_string(device->device_id()));
      }
    }

    // "To wake up the CAN bus" (same as the old code), then tell every
    // SPARK MAX how often to report its status.
    send_or_warn(heartbeat(false), "wake-up heartbeat");
    configure_status_periods();

    // ------------------------------------------------------------------
    // Publishers (was setup_publishers)
    // ------------------------------------------------------------------
    robot_data_pub_ = create_publisher<msg::RobotStatusMessage>("robot_data", 10);

    // ------------------------------------------------------------------
    // Subscribers (was setup_subscribers + setup_executor)
    // ------------------------------------------------------------------
    cmd_vel_sub_ = create_subscription<geometry_msgs::msg::Twist>(
      "cmd_vel", 10,
      [this](geometry_msgs::msg::Twist::SharedPtr msg) {on_cmd_vel(*msg);});

    depositor_sub_ = create_subscription<std_msgs::msg::Float32>(
      "depositor/position_setpoint", 10,
      [this](std_msgs::msg::Float32::SharedPtr msg) {
        const float target = std::clamp<double>(msg->data, depositor_min_, depositor_max_);
        depositor_->set_command(ControlMode::PositionSet, target);
      });

    actuator_sub_ = create_subscription<std_msgs::msg::Float32>(
      "excavator/actuator_output", 10,
      [this](std_msgs::msg::Float32::SharedPtr msg) {
        const float target = std::clamp<double>(msg->data, actuator_min_, actuator_max_);
        excavator_actuator_->set_command(ControlMode::DutyCycleSet, target);
      });

    excavator_sub_ = create_subscription<std_msgs::msg::Float32>(
      "excavator/velocity_setpoint", 10,
      [this](std_msgs::msg::Float32::SharedPtr msg) {
        const float target =
        std::clamp<double>(msg->data, excavator_vel_min_, excavator_vel_max_);
        excavator_motor_->set_command(ControlMode::SpeedSet, target);
      });

    enabled_sub_ = create_subscription<std_msgs::msg::Bool>(
      "enabled", 10,
      [this](std_msgs::msg::Bool::SharedPtr msg) {
        if (msg->data != enabled_) {
          RCLCPP_INFO(get_logger(), "Robot %s", msg->data ? "ENABLED" : "DISABLED");
        }
        enabled_ = msg->data;
      });

    // ------------------------------------------------------------------
    // Timers (was setup_timers). Same rates as the ESP32.
    // rclcpp::spin runs everything on one thread, one callback at a time,
    // so no mutexes are needed (same as the rclc executor).
    // ------------------------------------------------------------------
    can_core_timer_ = create_wall_timer(25ms, [this]() {can_core();});
    read_timer_ = create_wall_timer(10ms, [this]() {read_can();});
    status_timer_ = create_wall_timer(250ms, [this]() {publish_robot_data();});

    RCLCPP_INFO(
      get_logger(), "can_bridge ready (start_enabled=%s)", enabled_ ? "true" : "false");
  }

  ~CanBridgeNode() override
  {
    // On Ctrl+C, tell every motor to stop right away instead of waiting for
    // the heartbeat to time out.
    if (bus_) {
      bus_->send(heartbeat(false));
    }
  }

private:
  // ----------------------------------------------------------------------
  // CAN core, every 25 ms (was CAN_core_callback)
  // ----------------------------------------------------------------------
  void can_core()
  {
    if (enabled_) {
      was_enabled_ = true;
      if (!send_or_warn(heartbeat(true), "enabled heartbeat")) {
        return;
      }
      // Send each motor's queued command (the old code called
      // CAN_Helper.send_message() once per motor; same thing).
      for (auto * device : devices_) {
        auto command = device->pending_command();
        if (command && send_or_warn(*command, "motor command")) {
          device->mark_command_sent();
        }
      }
    } else if (was_enabled_) {
      // Send ONE disabled heartbeat after being enabled. Silence after that
      // also counts as disabled.
      was_enabled_ = false;
      send_or_warn(heartbeat(false), "disabled heartbeat");
    }
  }

  // ----------------------------------------------------------------------
  // Read incoming status frames, every 10 ms (was read_callback).
  // The old code read ONE frame per tick. 5 motors x 3 status frames every
  // 100 ms is 150 frames/s, more than 100 ticks/s, so it could fall behind.
  // Here we read everything that is waiting.
  // ----------------------------------------------------------------------
  void read_can()
  {
    for (int i = 0; i < 500; ++i) {  // cap so one tick can't run forever
      auto frame = bus_->receive();
      if (!frame) {
        break;
      }
      for (auto * device : devices_) {
        if (device->handle_frame(*frame)) {
          break;
        }
      }
    }
  }

  // ----------------------------------------------------------------------
  // Publish motor data, every 250 ms (was robot_status_timer_callback)
  // ----------------------------------------------------------------------
  void publish_robot_data()
  {
    msg::RobotStatusMessage out;
    out.enabled = enabled_;
    fill(out.left_drivebase, *drive_left_);
    fill(out.right_drivebase, *drive_right_);
    fill(out.depositor, *depositor_);
    fill(out.excavator_actuator, *excavator_actuator_);
    fill(out.excavator_motor, *excavator_motor_);
    robot_data_pub_->publish(out);

    // Was log_logging(drive_base_left.to_string()). See it with:
    //   ros2 run cometbot_can can_bridge --ros-args --log-level can_bridge:=debug
    RCLCPP_DEBUG(get_logger(), "%s", drive_left_->to_string().c_str());
    RCLCPP_DEBUG(get_logger(), "%s", drive_right_->to_string().c_str());
  }

  // ----------------------------------------------------------------------
  // Drive base (was cmd_vel_callback). Math is unchanged.
  // ----------------------------------------------------------------------
  void on_cmd_vel(const geometry_msgs::msg::Twist & msg)
  {
    double x = msg.linear.x;   // forward +, backward -
    double z = msg.angular.z;  // left +, right -

    // Normalize so |x| + |z| <= 1
    const double sum = std::fabs(x) + std::fabs(z);
    if (sum > 1.0) {
      x /= sum;
      z /= sum;
    }

    const float output1 = static_cast<float>(x + z);
    const float output2 = static_cast<float>(x - z);

    float left = output2;
    float right = output1;
    if (x < 0 && invert_turn_when_reversing_) {
      left = output1;
      right = output2;
    }
    right = -right;  // right side motors are mounted mirrored

    drive_left_->set_command(ControlMode::DutyCycleSet, left);
    drive_right_->set_command(ControlMode::DutyCycleSet, right);
  }

  // ----------------------------------------------------------------------
  // Helpers
  // ----------------------------------------------------------------------
  static CanMessage heartbeat(bool enabled)
  {
    CanMessage msg;
    msg.id = HEARTBEAT_ID;
    msg.len = HEARTBEAT_LEN;
    std::fill(msg.data, msg.data + HEARTBEAT_LEN, enabled ? 0xFF : 0x00);
    return msg;
  }

  void configure_status_periods()
  {
    for (auto * device : devices_) {
      for (const auto & frame : device->status_period_frames()) {
        send_or_warn(frame, "status period setup");
        // Small gap so the adapter's send queue doesn't overflow
        // (the old code waited 50 ms per frame).
        std::this_thread::sleep_for(10ms);
      }
    }
  }

  // Send a frame. If it fails, log why (at most every 2 s so the terminal
  // isn't flooded) and return false.
  bool send_or_warn(const CanMessage & msg, const char * what)
  {
    if (bus_->send(msg)) {
      return true;
    }
    const int err = bus_->last_errno();
    if (err == ENODEV || err == ENXIO) {
      // Adapter unplugged. Same idea as ESP.restart(): quit, and the launch
      // file (respawn: true) starts us again once it's back.
      RCLCPP_FATAL(
        get_logger(), "CAN adapter '%s' disappeared (%s). Shutting down.",
        bus_->interface_name().c_str(), bus_->last_error().c_str());
      rclcpp::shutdown();
      return false;
    }
    if (err == ENOBUFS || err == EAGAIN) {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 2000,
        "CAN send queue is full while sending %s. Nobody is answering on the bus: "
        "are the SPARK MAXs powered, is the bus terminated, is the bitrate 1 Mbit/s?",
        what);
    } else {
      RCLCPP_WARN_THROTTLE(
        get_logger(), *get_clock(), 2000, "Failed to send %s: %s",
        what, bus_->last_error().c_str());
    }
    return false;
  }

  static void fill(msg::SparkMaxMessage & out, const SparkMax & spark)
  {
    const SparkMaxStatus & s = spark.status();
    out.device_id = spark.device_id();
    out.applied_output = s.applied_output;
    out.velocity = s.velocity;
    out.position = s.position;
    out.temperature = s.temperature;
    out.voltage = s.voltage;
    out.current = s.current;
  }

  static uint8_t checked_id(int64_t id, const std::string & name)
  {
    if (id < 1 || id > 62) {
      throw std::runtime_error(name + " must be between 1 and 62 (got " + std::to_string(id) + ")");
    }
    return static_cast<uint8_t>(id);
  }

  // CAN
  std::unique_ptr<SocketCan> bus_;
  std::unique_ptr<SparkMax> drive_left_, drive_right_, depositor_,
    excavator_actuator_, excavator_motor_;
  std::vector<SparkMax *> devices_;

  // State
  bool enabled_ = false;
  bool was_enabled_ = false;
  bool invert_turn_when_reversing_ = true;
  double depositor_min_, depositor_max_;
  double actuator_min_, actuator_max_;
  double excavator_vel_min_, excavator_vel_max_;

  // ROS
  rclcpp::Publisher<msg::RobotStatusMessage>::SharedPtr robot_data_pub_;
  rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_sub_;
  rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr depositor_sub_, actuator_sub_,
    excavator_sub_;
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr enabled_sub_;
  rclcpp::TimerBase::SharedPtr can_core_timer_, read_timer_, status_timer_;
};

}  // namespace cometbot_can

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  int exit_code = 0;
  try {
    rclcpp::spin(std::make_shared<cometbot_can::CanBridgeNode>());
  } catch (const std::exception & e) {
    RCLCPP_FATAL(rclcpp::get_logger("can_bridge"), "%s", e.what());
    exit_code = 1;
  }
  rclcpp::shutdown();
  return exit_code;
}
