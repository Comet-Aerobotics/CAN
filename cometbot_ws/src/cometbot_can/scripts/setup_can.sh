#!/usr/bin/env bash
# Turn on the USB-CAN adapter so Linux can use it as "can0".
# Run this once each time the mini PC boots or the adapter is plugged in.
#
#   setup_can.sh              real adapter -> can0 at 1 Mbit/s (same speed as the ESP32)
#   setup_can.sh --virtual    fake bus "vcan0" for testing with no hardware
set -euo pipefail

if [ "${1:-}" = "--virtual" ]; then
  sudo modprobe vcan 2>/dev/null || true
  if ! ip link show vcan0 >/dev/null 2>&1; then
    sudo ip link add dev vcan0 type vcan
  fi
  sudo ip link set up vcan0
  echo "vcan0 is up. Watch traffic with: candump vcan0"
  exit 0
fi

IFACE="${1:-can0}"
BITRATE="${2:-1000000}"

if ! ip link show "$IFACE" >/dev/null 2>&1; then
  echo "No '$IFACE' found."
  echo " - Is the adapter plugged in? Check: lsusb"
  echo " - CANable with candleLight firmware shows up as can0 by itself."
  echo " - CANable with slcan firmware needs this instead (s8 = 1 Mbit/s):"
  echo "     sudo slcand -o -c -s8 /dev/ttyACM0 $IFACE && sudo ip link set up $IFACE"
  echo " - Inside the dev container, the container needs --network=host."
  exit 1
fi

sudo ip link set "$IFACE" down || true
sudo ip link set "$IFACE" type can bitrate "$BITRATE"
sudo ip link set "$IFACE" txqueuelen 1000
sudo ip link set up "$IFACE"
ip -details link show "$IFACE" | head -5
echo "$IFACE is up at $BITRATE bit/s. Watch traffic with: candump $IFACE"
