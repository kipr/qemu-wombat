import socket
import time
import fcntl
import os
import select
from operator import concat

"""
Can be used to connect to a serial port and then listen and send commands to a root terminal instance on the serial port.
"""

class ConnectRoot:

  _MAX_PORT_ = 65535
  prev2_buffer = ''
  prev_buffer = ''
  curr_buffer = ''
  root_string = 'root@(none):/# '
  first_root = False

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
    buf = self.conn.recv(1024).decode('utf-8')
    print(buf, end = "")
    return buf

  def wait_for_prompt(self):
    while True:
      r, _, _ = select.select([self.conn], [], [])
      if not r:
        time.sleep(0.5)
        continue

      self.prev2_buffer = self.prev_buffer
      self.prev_buffer = self.curr_buffer
      self.curr_buffer = self.receive()
      if 'cam-dummy-reg: disabling' in self.curr_buffer:
        print('Ignoring buffer... cam-dummy')
        self.curr_buffer = ''
      if 'Timeout waiting for hardware interrupt.' in self.curr_buffer:
        print('Ignoring buffer... timeout')
        self.curr_buffer = ''
      buf = self.prev2_buffer + self.prev_buffer + self.curr_buffer
      if self.root_string in buf:
        if self.first_root == False:
          time.sleep(10)
          self.first_root = True
        time.sleep(1)
        print('Root found!')
        break
      
  def send(self, data):
    if data == 'exit':
      time.sleep(1)
      print('\nExiting...')
      self.conn.close()
      return
    
    self.conn.send(data.encode('utf-8'))
    self.conn.send(b'\r')
    self.wait_for_prompt()

  def send_bulk(self, data):
    for line in data:
      self.send(line)

    
