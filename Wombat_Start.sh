#!/usr/bin/env bash
sudo qemu-system-arm \
  -M versatilepb \
  -cpu arm1176 \
  -m 256 \
  -hda Wombat-Bullseye.img \
  -net nic \
  -net user,hostfwd=tcp::5022-:22 \
  -dtb versatile-pb-buster.dtb \
  -kernel kernel-qemu-4.19.50-buster \
  -append 'root=/dev/sda2 panic=1' \
  -no-reboot
