Resources:
https://gist.github.com/plembo/c4920016312f058209f5765cb9a3a25e

Raspberrry Pi OS Downloads:
https://www.raspberrypi.com/software/operating-systems/
https://downloads.raspberrypi.org/raspios_armhf/images/raspios_armhf-2022-04-07/2022-04-04-raspios-bullseye-armhf.img.xz

Steps:

1. Install QEMU system emulation binaries for ARM processors

`sudo apt-get qemu-system-arm`

2. Create new folder and put these downloads in it

`mkdir Wombat-Bullseye`

3. Download Pi Image with desktop and unzip to Wombat-Bullseye

4. Change image name to Wombat-Bullseye

`mv 2022-04-04-raspios-bullseye-armhf.img Wombat-Bullseye.img`

5. Download matching qemu rpi kernel and device tree file (.dtb) from qemu-rpi-kernel and add to Wombat-Bullseye directory

`https://github.com/dhruvvyas90/qemu-rpi-kernel`

6. Create Wombat_Start.sh for convienence

`#!/usr/bin/env bash
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
`

7. Run Wombat_Start.sh

`./Wombat_Start.sh`

8. Run through Raspberry Pi startup to setup environment
	- Once you click into qemu screen, you can leave it using `Ctrl+Alt+G`
	- Process can be stopped by selecting Machine -> Quit

9. Shut down virtual machine then increase disk size to 8G (or whatever size your SD card is) using qemu-img 
	- Warning: It may be a good idea to create a backup copy of the image before resizing it at this point
	
`qemu-img resize Wombat-Bullseye.img 8G`

10. Start up the image again and then, in the terminal on the image, run fdisk to recreate the second partition

'sudo fdisk /dev/sda`

11. In fdisk, run these commands:

To show the current disk layout (note the starting sector of the second partition)
`print`

Delete the old partition 2
`d
2`

Create a new partition and make it the primary partition
`n
p
2`

Put in the starting sector of the old partition and enter to accept (may need to yes to format raw image)
`xxxxx`

Write all changes to disk and exit fdisk
`w`

12. Complete the resizing operation

`resize2fs /dev/sda2`

13. Confirm expanded disk size

`df -h`

14. Get updates

`sudo apt-get update`
