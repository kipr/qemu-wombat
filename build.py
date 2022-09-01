import sys
import subprocess
import urllib.request
import tarfile
import pathlib



FIRMWARE_VERSION = '1.20210108'
QEMU_VERSION = '7.1.0'

firmware_path = pathlib.Path(f'firmware-{FIRMWARE_VERSION}')

if not firmware_path.exists():
  print(f'Downloading firmware {FIRMWARE_VERSION}...')
  urllib.request.urlretrieve(
    f'https://github.com/raspberrypi/firmware/archive/refs/tags/{FIRMWARE_VERSION}.tar.gz',
    f'{FIRMWARE_VERSION}.tar.gz'
  )
  print(f'Extracting firmware {FIRMWARE_VERSION}...')
  with tarfile.open(f'{FIRMWARE_VERSION}.tar.gz') as tar:
    tar.extractall()
else:
  print(f'Firmware {FIRMWARE_VERSION} already downloaded')

subprocess.run([
  'qemu-system-aarch64',
  '-m', '1024M',
  '-M', 'raspi3b',
  '-kernel', './build/kernel.elf',
])