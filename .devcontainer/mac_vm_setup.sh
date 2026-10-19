#!/usr/bin/env bash
# One-time setup of an Ubuntu VM on an Apple Silicon Mac, so the dev container
# can reach USB devices (OAK-D Pro, ESP32). Docker Desktop on macOS can't pass
# USB through; a VM with USB passthrough can.
#
# On the Mac (UTM or VMware Fusion; Fusion copes better with the OAK, see below):
#   1. Create a VM from the Ubuntu 22.04 Server arm64 ISO (4+ CPUs, 8+ GB RAM,
#      60+ GB disk, enable OpenSSH during install).
#      UTM: pick "Virtualize" with the QEMU backend, not Apple Virtualization
#      (which has no USB passthrough). In the VM's settings set Input > USB
#      Support to USB 3.0 (XHCI) and enable USB sharing.
#   2. The OAK re-enumerates (03e7:2485 -> 03e7:f63b) when its firmware boots,
#      so it must be handed to the VM twice.
#      UTM: accept the "connect to VM" prompt both times, quickly; oak_check.sh
#      gives the driver 60 s to find the booted device.
#      VMware Fusion: shut the VM down and add to its .vmx file
#        usb.autoConnect.device0 = "0x03e7:0x2485"
#        usb.autoConnect.device1 = "0x03e7:0xf63b"
#      and set USB compatibility to USB 3.1 in Settings > USB & Bluetooth.
#
# In the VM:
#   3. git clone <this repo> ~/CAN && bash ~/CAN/.devcontainer/mac_vm_setup.sh
#   4. Log out and back in (docker group).
#
# Back on the Mac:
#   5. VS Code > Remote-SSH: connect to <user>@<vm-ip>, open ~/CAN, then
#      "Dev Containers: Reopen in Container". Port 8080 (Foxglove) is forwarded
#      to the Mac's localhost as before.
#   6. In the container: cometbot_ws/src/mapping/oak_check.sh
set -euo pipefail

if [ "$(uname -m)" != "aarch64" ] && [ "$(uname -m)" != "x86_64" ]; then
  echo "Unexpected architecture $(uname -m)" >&2
  exit 1
fi

echo "[vm-setup] Installing Docker, git, usbutils"
sudo apt-get update
sudo apt-get install -y docker.io docker-buildx git usbutils openssh-server
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

# The container user (uid 1000) opens the OAK through the bind-mounted
# /dev/bus/usb, so the node permissions are set here on the VM.
echo "[vm-setup] Installing OAK udev rule"
echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' \
  | sudo tee /etc/udev/rules.d/80-movidius.rules >/dev/null
sudo udevadm control --reload-rules
sudo udevadm trigger

echo "[vm-setup] Done. Log out and back in, then connect with VS Code Remote-SSH to:"
hostname -I | awk '{print "  " $1}'
if lsusb | grep -q "03e7:"; then
  echo "[vm-setup] OAK visible in the VM:"
  lsusb | grep "03e7:"
else
  echo "[vm-setup] OAK not visible yet; check the VMware USB settings (step 2)."
fi
