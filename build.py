import os
import re
import subprocess
import urllib.request
import tarfile
import lzma
from tempfile import mktemp
from pathlib import Path
import socket
import time
from classes.commandList import CommandList
from classes.recovery import Pass
from classes.command import Command


# FIRMWARE_VERSION = '1.20210108'
# File Paths
build_path = Path(__file__).parent / 'build'
boot_mount_path = Path('/mnt/raspbian_boot')
firmware_path = build_path / 'firmware'
boot_path = firmware_path / 'boot'
raspi_os_image_path = build_path / '2022-09-22-raspios-bullseye-arm64.img'

# Create if file paths exist
if not build_path.exists():
  build_path.mkdir()

if not boot_mount_path.exists():
  boot_mount_path.mkdir()

if not firmware_path.exists():
  firmware_path.mkdir()

if not boot_path.exists():
  boot_path.mkdir()

if not Path(raspi_os_image_path).exists():
  tmp_file = mktemp('.img.xz')
  
  
  print(f'Downloading Raspberry Pi OS...')
  urllib.request.urlretrieve(
    f'https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2022-09-26/{raspi_os_image_path.name}.xz',
    tmp_file
  )

  # Decompress incrementally
  print(f'Decompressing Raspberry Pi OS...')
  with lzma.open(tmp_file) as xz_file:
    with open(raspi_os_image_path, 'wb') as out_file:
      while True:
        data = xz_file.read(1024 * 1024)
        if not data:
          break
        out_file.write(data)
else:
  print(f'Raspberry Pi OS already downloaded')

# Mount partitions
print("Mounting partitions...")
loop_num = subprocess.run(
    [
        'losetup',
        '--show',
        '--find',
        '--partscan',
        f'{raspi_os_image_path}'
    ],
    check=True,
    capture_output=True
).stdout.strip().decode('utf-8')

loop_p1 = loop_num + 'p1'

if not boot_mount_path.exists():
  boot_mount_path.mkdir()

subprocess.run([
  'mount',
  f'{loop_p1}',
  f'{boot_mount_path}'
],check=True)

#Adds user config file to boot
print('Configuring user...')
pwd = subprocess.run([
    'openssl', 'passwd', '-6','botball'
], check=True, capture_output=True).stdout.strip().decode('utf-8')

try:
  with open(f'{boot_mount_path}/userconf.txt', 'w') as f:
    f.write(f'kipr:{pwd}')
except FileNotFoundError:
  print("The boot directory does not exist")


# Grab kernel and device tree fille
print("Grabbing kernel and device tree fille...")
subprocess.run([
  'cp', f'{boot_mount_path}/bcm2710-rpi-3-b.dtb', f'{boot_path}/bcm2710-rpi-3-b.dtb'
], check=True)

subprocess.run([
  'cp', f'{boot_mount_path}/kernel8.img', f'{boot_path}/kernel8.img'
], check=True)

# Unmount image
print('Unmounting image...')
subprocess.run([
  'umount', f'{loop_p1}'
], check=True)

boot_mount_path.rmdir()

subprocess.run([
  'losetup',
  '--detach',
  f'{loop_num}'
], check=True)

# Create snapshot

snapshot_path = build_path / 'snapshot.qcow2'

if snapshot_path.exists():
  snapshot_path.unlink()

print(f'Creating snapshot...')
subprocess.run([
  'qemu-img',
  'create',
  '-f', 'qcow2',
  '-F', 'raw',
  '-b', raspi_os_image_path,
  snapshot_path,
], check = True)


subprocess.run([
  'qemu-img',
  'resize',
  snapshot_path,
  '8G'
], check = True)

# Create recovery image
print('Creating recovery image...')

#Resize partition

commands = CommandList()
commands.append(Command('python3 --version', 'Python 3'))
commands.append(Command('fdisk /dev/mmcblk0','Command (m for help)', 'Command (m for help): '))

def print_fdisk_parse(buffer: str):
  locator = 'mmcblk0p2'
  return re.search('\d+', buffer[(buffer.index(locator) + len(locator)):])[0]

commands.append(Command('print', '/dev/mmcblk0p2 ', 'Command (m for help): ', 'partition2_start', print_fdisk_parse))
commands.append(Command('d', 'Partition number (1,2, default 2):', 'Partition number (1,2, default 2): '))
commands.append(Command('2', 'Partition 2 has been deleted.', 'Command (m for help): '))
commands.append(Command('n', 'Partition type', 'Select (default p): '))
commands.append(Command('p', 'Partition number (2-4, default 2):', 'Partition number (2-4, default 2): '))
commands.append(Command('2', 'First sector', 'First sector (2048-16777215, default 2048): '))
commands.append(Command('', 'Last sector', 'default 16777215): ', store_used='partition2_start'))
commands.append(Command('', 'remove the signature', '[Y]es/[N]o: '))
commands.append(Command('n', 'Command (m for help):', 'Command (m for help): '))
commands.append(Command('w', 'The partition table has been altered.'))
commands.append(Command('resize2fs /dev/mmcblk0p2', 'resize2fs 1'))
commands.append(Command('df -h'))

recovery = Pass(
  commands,
  kernel = firmware_path / 'boot' / 'kernel8.img',
  dtb = firmware_path / 'boot' / 'bcm2710-rpi-3-b.dtb',
  drive = f'format=qcow2,file={snapshot_path}'
)

recovery.run()