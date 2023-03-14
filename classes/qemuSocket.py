import socket
import time
import fcntl
import os
import select
from operator import concat
from classes.command import Command
from classes.commandList import CommandList

"""
Can be used to connect to a serial port and then listen and send commands to a root terminal instance on the serial port.
"""

class QemuSocket:

  _MAX_PORT_ = 65535
  curr_buffer = ''
  len_buffer = ''
  root_string = 'root@(none):/# '
  alt_wait_string = ''

  def __init__(self, serial_tcp_port = 4444):
    if serial_tcp_port > self._MAX_PORT_:
        raise ValueError(f'Invalid serial TCP port: {serial_tcp_port}')
    else:
        self.serial_tcp_port = serial_tcp_port

  def serial_tcp(self):
    self.serial_tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.serial_tcp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.serial_tcp_sock.bind(('127.0.0.1', self.serial_tcp_port))

  def listen(self):
    self.serial_tcp_sock.listen()

  def accept(self):
    self.conn, addr = self.serial_tcp_sock.accept()
    fcntl.fcntl(self.conn, fcntl.F_SETFL, os.O_NONBLOCK)

  def receive(self):
    buf = self.conn.recv(1024).decode('utf-8', 'ignore')
    print(buf, end = "")
    return buf

  def wait_for_prompt(self):
    while True:
      r, _, _ = select.select([self.conn], [], [])
      if not r:
        time.sleep(0.5)
        continue
      buf = self.receive()
      self.curr_buffer = concat(self.curr_buffer,buf)
      wait_string = self.root_string if self.alt_wait_string == '' else self.alt_wait_string
      self.len_buffer = (self.len_buffer + buf)[-len(wait_string):]
      if self.len_buffer == wait_string:
        time.sleep(1)
        break
      
  def send(self, command: Command):
    command_str = command.command
    if command_str == 'exit':
      time.sleep(1)
      print('\nExiting...')
      self.conn.close()
      self.serial_tcp_sock.close()
      time.sleep(1)
      return
    
    if command_str == 'switch_user':
      time.sleep(1)
      print('\nSwitching user...')
      root_string = 'kipr@raspberrypi:/ $'

    if command.alt_wait_string != '':
      self.alt_wait_string = command.alt_wait_string

    self.conn.send(command_str.encode('utf-8'))
    self.conn.send(b'\r')
    self.wait_for_prompt()
    if command.validate(self.curr_buffer) == False:
      raise ValueError(f'Command {command_str} failed to validate')
    command.buffer = self.curr_buffer
    self.curr_buffer = ''
    self.alt_wait_string = ''

  def send_bulk(self, data: CommandList):
    for command in data:
      self.send(command)
      if command.buffer != '' and command.buf_func != None:
        data.store[command.name] = command.buf_func(command.buffer)
        data.get_store_update()
