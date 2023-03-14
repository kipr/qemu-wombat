#!/usr/bin/env bash

# sudo qemu-system-aarch64 \
#   -M raspi3b \
#   -m 1024M \
#   -kernel build/firmware/boot/kernel8.img \
#   -dtb build/firmware/boot/bcm2710-rpi-3-b.dtb \
#   -drive "format=raw,file=build/2022-09-22-raspios-bullseye-arm64.img" \
#   -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4 init=/bin/bash" \
#   -display 'none' \
#   -serial tcp:127.0.0.1:4444,nodelay

#Master OS
sudo qemu-system-aarch64 \
  -M raspi3b \
  -m 1024 \
  -kernel build/firmware/boot/kernel8.img \
  -dtb build/firmware/boot/bcm2710-rpi-3-b.dtb \
  -drive "format=raw,file=build/master_os.img" \
  -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4" \
  -device usb-net,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 \
  -serial stdio -usb -device usb-mouse -device usb-kbd

#Snapshot
# sudo qemu-system-aarch64 \
#   -M raspi3b \
#   -m 1024 \
#   -kernel build/firmware/boot/kernel8.img \
#   -dtb build/firmware/boot/bcm2710-rpi-3-b.dtb \
#   -drive "format=qcow2,file=build/snapshot.qcow2" \
#   -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4" \
#   -device usb-net,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 \
#   -serial stdio -usb -device usb-mouse -device usb-kbd