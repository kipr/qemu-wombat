<h1>Creating a Virtual Wombat Image</h1>

<h2>Using the Build Script</h2>

```
sudo apt-get install qemu-system-arm
```

```
sudo python3 build.py
```

<h2> Manually Building the Image</h2>

<h3>Raspberrry Pi OS Downloads:</h3>

https://www.raspberrypi.com/software/operating-systems/

https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2022-09-26/2022-09-22-raspios-bullseye-arm64.img.xz

<h3>Building the image from scratch:</h3>

1. Install QEMU system emulation binaries for ARM processors

```
sudo apt-get install qemu-system-arm
```

2. Create new folder

```
mkdir qemu-wombat
```

3. Download Pi Image with desktop and unzip to qemu-wombat folder

4. Change image name to master_os

```
cp 2022-09-22-raspios-bullseye-arm64.img master_os.img
```

5. Mount the partitions

```
sudo LOOP_NUM=$(losetup --show --find --partscan master_os.img)
```

Note the loop number

```
sudo mkdir /mnt/{raspbian-boot,raspbian-root}
```

```
sudo mount /dev/{$LOOP_NUM}p1 /mnt/raspbian-boot;
sudo mount /dev/{$LOOP_NUM}p2 /mnt/raspbian-root
```

6. Create a userconf.txt file and copy it to raspbian-boot (you can change the password and username if desired)

```
touch userconf.txt ;
echo -n 'kipr:' > userconf.txt ;
echo 'botball' | openssl passwd -6 -stdin >> userconf.txt
```

```
sudo cp userconf.txt /mnt/raspbian-boot/userconf.txt
```

7. Copy the kernel device tree file to Wombat-Bullseye

```
sudo cp /mnt/raspbian-boot/bcm2710-rpi-3-b.dtb .;
sudo cp /mnt/raspbian-boot/kernel8.img .
```

8. Unmount the image

```
sudo umount /dev/{$LOOP_NUM}p1;
sudo umount /dev/{$LOOP_NUM}p2;
sudo rmdir /mnt/{raspbian-boot,raspbian-root};
sudo losetup --detach /dev/{$LOOP_NUM}
```

9. Convert image to qcow2 format

```
qemu-img convert -f raw -O qcow2 master_os.img snapshot.qcow2
```

10. Increase disk size to 8G (or whatever size your SD card is) using qemu-img 
	- Warning: It may be a good idea to create a backup copy of the image before resizing it at this point
	
```
qemu-img resize Wombat-Bullseye.qcow2 8G
```

11. Create Wombat_Start.sh to run with correct dtb and kernel (or use the one in the repository)

```
#!/usr/bin/env bash
sudo qemu-system-aarch64 \
  -M raspi3b \
  -m 1024 \
  -kernel build/firmware/boot/kernel8.img \
  -dtb build/firmware/boot/bcm2710-rpi-3-b.dtb \
  -drive "format=raw,file=build/master_os.img" \
  -append "console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4" \
  -device usb-net,netdev=net0 -netdev user,id=net0,hostfwd=tcp::5555-:22 \
  -serial stdio -usb -device usb-mouse -device usb-kbd
```

12. Run Wombat_Start.sh

```
./Wombat_Start.sh
```

13. Login to the image

14. Run fdisk to recreate the second partition

```
sudo fdisk /dev/mmcblk0
```

15. In fdisk, run these commands:

To show the current disk layout (note the starting sector of the second partition)
```
print
```

Delete the old partition 2

```
d
2
```

Create a new partition and make it the primary partition

```
n
p
2
```

Put in the starting sector of the old partition
```
xxxxx
```

Put in the end sector of the disk so that only 7 GB are used (this number may be different for a different SD card size)
```
15309209
```

Answer no to changing ext4 signature
```
n
```

Write all changes to disk and exit fdisk
```
w
```

16. Complete the resizing operation

```
sudo resize2fs /dev/mmcblk0p2
```

17. Confirm expanded disk size

```
df -h
```

18. Exit the image and convert back to raw format

```
sudo qemu-img convert -f qcow2 -O raw snapshot.qcow2 master_os.img
```

19. Resize to 7 GB
  
```
sudo qemu-img resize master_os.img --shrink 7G
```

