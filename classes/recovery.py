from imaplib import Commands
import subprocess
from classes.command import Command
from classes.commandList import CommandList
from classes.qemuSocket import QemuSocket

class Pass:
  """
  Runs a qemu isntance in recovery mode and waits for the user to connect to the serial port.

  The serial port is exposed via TCP on localhost:4444 or the port specified by the serial_tcp_port argument.
  """

  prev_buffer = ''
  curr_buffer = ''

  def __init__(self, commands: CommandList = None, serial_tcp_port = 4444, **kwargs):
    self.commands = commands
    self.kernel = kwargs.get('kernel', None)
    self.dtb = kwargs.get('dtb', None)
    self.drive = kwargs.get('drive', None)
    self.serial_tcp_port = serial_tcp_port
    self.root = QemuSocket(self.serial_tcp_port)
    self.root.serial_tcp()
    self.root.listen()
  
  def __str__(self) -> str:
    return f'Kernel: {self.kernel}, DTB: {self.dtb}, Drive: {self.drive}, Serial TCP Port: {self.serial_tcp_port}'

  def run(self):
    self.do_pass()

  def do_pass(self):
    print(f'Starting Raspberry Pi OS in recovery mode...')
    p = subprocess.Popen([
      'qemu-system-aarch64',
      '-m', '1024M',
      '-M', 'raspi3b',
      '-kernel', self.kernel,
      '-dtb', self.dtb,
      '-drive', self.drive,
      '-append', 'console=ttyAMA0 root=/dev/mmcblk0p2 rw rootwait rootfstype=ext4 init=/bin/bash',
      '-display', 'none',
      '-serial', f'tcp:127.0.0.1:{self.serial_tcp_port},nodelay',
    ])

    print('Waiting for QEMU to start...')

    self.root.accept()

    print('QEMU started, waiting for prompt...')
    self.root.wait_for_prompt()
    if self.commands != None:
      self.root.send_bulk(self.commands)
    self.root.send(Command('exit'))
