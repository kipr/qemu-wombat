import sys
import subprocess
import urllib.request
import tarfile
import lzma
from tempfile import mktemp
from pathlib import Path
import socket
import time


FIRMWARE_VERSION = '1.20210108'

build_path = Path(__file__).parent / 'build'

# Create build_path if it doesn't exist
if not build_path.exists():
  build_path.mkdir()

firmware_path = build_path / f'firmware-{FIRMWARE_VERSION}'
raspi_os_image_path = build_path / '2022-04-04-raspios-bullseye-arm64.img'

if not firmware_path.exists():
  tmp_file = mktemp('.tar.gz')

  print(f'Downloading firmware {FIRMWARE_VERSION}...')
  urllib.request.urlretrieve(
    f'https://github.com/raspberrypi/firmware/archive/refs/tags/{FIRMWARE_VERSION}.tar.gz',
    tmp_file
  )
  print(f'Extracting firmware {FIRMWARE_VERSION}...')
  with tarfile.open(tmp_file) as tar:
    tar.extractall(path = firmware_path.parent)
else:
  print(f'Firmware {FIRMWARE_VERSION} already downloaded')

if not Path(raspi_os_image_path).exists():
  tmp_file = mktemp('.img.xz')
  
  
  print(f'Downloading Raspberry Pi OS...')
  urllib.request.urlretrieve(
    f'https://downloads.raspberrypi.org/raspios_arm64/images/raspios_arm64-2022-04-07/{raspi_os_image_path.name}.xz',
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

# Create snapshot

snapshot_path = build_path / 'snapshot.qcow2'

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

import passes.recovery

passes.recovery.do_pass(
  kernel = firmware_path / 'boot' / 'kernel8.img',
  dtb = firmware_path / 'boot' / 'bcm2710-rpi-3-b-plus.dtb',
  drive = f'format=qcow2,file={snapshot_path}'
)