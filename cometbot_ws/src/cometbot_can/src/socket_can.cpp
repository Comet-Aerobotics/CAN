#include "cometbot_can/socket_can.hpp"

#include <fcntl.h>
#include <linux/can.h>
#include <linux/can/raw.h>
#include <net/if.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <cstring>
#include <stdexcept>

namespace cometbot_can
{

namespace
{
std::string errno_text(int err)
{
  return std::string(std::strerror(err));
}
}  // namespace

SocketCan::SocketCan(const std::string & interface_name)
: name_(interface_name)
{
  if (name_.empty() || name_.size() >= IFNAMSIZ) {
    throw std::runtime_error("Bad CAN interface name: '" + name_ + "'");
  }

  // 1. Make a raw CAN socket (like opening a file, but for the CAN bus).
  fd_ = ::socket(PF_CAN, SOCK_RAW, CAN_RAW);
  if (fd_ < 0) {
    throw std::runtime_error(
            "Could not open a CAN socket (" + errno_text(errno) +
            "). This Linux kernel may not have CAN support.");
  }

  // 2. Look up the interface number for "can0".
  struct ifreq ifr;
  std::memset(&ifr, 0, sizeof(ifr));
  std::strncpy(ifr.ifr_name, name_.c_str(), IFNAMSIZ - 1);
  if (::ioctl(fd_, SIOCGIFINDEX, &ifr) < 0) {
    const int err = errno;
    ::close(fd_);
    fd_ = -1;
    throw std::runtime_error(
            "CAN interface '" + name_ + "' not found (" + errno_text(err) +
            "). Is the USB-CAN adapter plugged in, and did you run setup_can.sh? "
            "Inside the dev container, it also needs --network=host.");
  }

  // 3. Attach ("bind") the socket to that interface.
  struct sockaddr_can addr;
  std::memset(&addr, 0, sizeof(addr));
  addr.can_family = AF_CAN;
  addr.can_ifindex = ifr.ifr_ifindex;
  if (::bind(fd_, reinterpret_cast<struct sockaddr *>(&addr), sizeof(addr)) < 0) {
    const int err = errno;
    ::close(fd_);
    fd_ = -1;
    throw std::runtime_error("Could not bind to '" + name_ + "': " + errno_text(err));
  }

  // 4. Non-blocking: reading when nothing has arrived returns immediately
  //    instead of freezing the program.
  const int flags = ::fcntl(fd_, F_GETFL, 0);
  if (flags < 0 || ::fcntl(fd_, F_SETFL, flags | O_NONBLOCK) < 0) {
    const int err = errno;
    ::close(fd_);
    fd_ = -1;
    throw std::runtime_error("Could not make CAN socket non-blocking: " + errno_text(err));
  }
}

SocketCan::~SocketCan()
{
  if (fd_ >= 0) {
    ::close(fd_);
  }
}

bool SocketCan::send(const CanMessage & msg)
{
  if (msg.len > 8) {
    last_errno_ = EINVAL;
    return false;
  }

  struct can_frame frame;
  std::memset(&frame, 0, sizeof(frame));
  // SPARK MAX frames use 29-bit "extended" IDs, so set the extended flag.
  // (The MCP2515 library did this when you passed CAN_EXTID.)
  frame.can_id = (msg.id & CAN_EFF_MASK) | CAN_EFF_FLAG;
  frame.can_dlc = msg.len;
  std::memcpy(frame.data, msg.data, msg.len);

  const ssize_t written = ::write(fd_, &frame, sizeof(frame));
  if (written != static_cast<ssize_t>(sizeof(frame))) {
    last_errno_ = (written < 0) ? errno : EIO;
    return false;
  }
  last_errno_ = 0;
  return true;
}

std::optional<CanMessage> SocketCan::receive()
{
  struct can_frame frame;
  while (true) {
    const ssize_t got = ::read(fd_, &frame, sizeof(frame));
    if (got < 0) {
      if (errno != EAGAIN && errno != EWOULDBLOCK) {
        last_errno_ = errno;
      }
      return std::nullopt;  // nothing waiting (or an error)
    }
    if (got != static_cast<ssize_t>(sizeof(frame))) {
      continue;  // incomplete frame, skip
    }
    // Skip bus-error reports, remote requests, and 11-bit IDs: SPARK MAX
    // status frames are always normal extended data frames.
    if ((frame.can_id & CAN_ERR_FLAG) || (frame.can_id & CAN_RTR_FLAG) ||
      !(frame.can_id & CAN_EFF_FLAG))
    {
      continue;
    }

    CanMessage msg;
    // Strip the flag bits so the ID is just the 29-bit number. (The old
    // MCP2515 library left an extra 0x80000000 bit on extended IDs.)
    msg.id = frame.can_id & CAN_EFF_MASK;
    msg.len = frame.can_dlc > 8 ? 8 : frame.can_dlc;
    std::memcpy(msg.data, frame.data, msg.len);
    return msg;
  }
}

std::string SocketCan::last_error() const
{
  return last_errno_ == 0 ? std::string("no error") : errno_text(last_errno_);
}

}  // namespace cometbot_can
