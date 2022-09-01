import subprocess
import socket
import time

serial_tcp_port = 4444

def do_pass(**kwargs):
  print(f'Starting Raspberry Pi OS in recovery mode...')
  p = subprocess.Popen([
    'qemu-system-aarch64',
    '-m', '1024M',
    '-M', 'raspi3b',
    '-kernel', kwargs['kernel'],
    '-dtb', kwargs['dtb'],
    '-drive', kwargs['drive'],
    '-append', 'console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4 init=/bin/bash',
    '-display', 'none',
    '-serial', f'tcp::{serial_tcp_port},server'
  ])

  print(f'Waiting for QEMU to start...')
  time.sleep(5)

  print(f'Connecting to QEMU...')
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect(('localhost', serial_tcp_port))

  # Print out what is received
  while p.poll() is None:
    data = s.recv(1024)
    if not data:
      break
    
    


  p.wait()