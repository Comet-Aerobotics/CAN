// SocketCAN wrapper: talks to the USB-CAN adapter on the mini PC.
//
// This replaces the MCP_CAN object (the MCP2515 chip wired to the ESP32).
// On Linux, a USB-CAN adapter (CANable etc.) shows up as a network interface
// called can0, and you talk to it with a normal socket, like a network
// connection.
#pragma once

#include <optional>
#include <string>

#include "cometbot_can/spark_protocol.hpp"

namespace cometbot_can
{

class SocketCan
{
public:
  // Opens the interface (e.g. "can0"). Throws std::runtime_error with a
  // readable explanation if it can't (adapter unplugged, interface not up...).
  explicit SocketCan(const std::string & interface_name);
  ~SocketCan();

  // Only one object should own the socket, so copying is not allowed.
  SocketCan(const SocketCan &) = delete;
  SocketCan & operator=(const SocketCan &) = delete;

  // Send one extended-ID frame. Returns false if it couldn't be queued;
  // last_errno() / last_error() then say why.
  bool send(const CanMessage & msg);

  // Read one extended-ID frame if one is waiting. Never blocks: returns
  // std::nullopt straight away if nothing has arrived.
  std::optional<CanMessage> receive();

  int last_errno() const {return last_errno_;}
  std::string last_error() const;
  const std::string & interface_name() const {return name_;}

private:
  int fd_ = -1;
  int last_errno_ = 0;
  std::string name_;
};

}  // namespace cometbot_can
