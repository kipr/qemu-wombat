#!/usr/bin/env bash
sudo qemu-system-aarch64 \
  -M raspi3b \
  -m 1024 \
  -kernel kernel8.img \
  -dtb bcm2710-rpi-3-b.dtb \
  -drive "format=qcow2,file=Wombat-Bullseye.qcow2" \
  -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4" \
  -device usb-net,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 \
  -serial stdio -usb -device usb-mouse -device usb-kbd
