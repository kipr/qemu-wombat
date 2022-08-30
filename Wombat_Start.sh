#!/usr/bin/env bash
sudo qemu-system-arm -kernel kernel-qemu \
-cpu arm1176 -m 256 \
-M versatilepb -dtb versatile-pb-buster.dtb \
-no-reboot \
-serial stdio \
-append "root=/dev/sda2 panic=1 rootfstype=ext4 rw" \
-hda Wombat-Bullseye.qcow2 \
-net nic -net user \
-net tap,ifname=vnet0,script=no,downscript=no
