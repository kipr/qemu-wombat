#!/usr/bin/env bash

sudo qemu-system-aarch64 \
  -M raspi3b \
  -m 1024M \
  -kernel build/firmware/boot/kernel8.img \
  -dtb build/firmware/boot/bcm2710-rpi-3-b.dtb \
  -drive "format=qcow2,file=build/snapshot.qcow2" \
  -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4 init=/bin/bash" \
  -display 'none' \
  -serial stdio tcp:127.0.0.1:4444,nodelay