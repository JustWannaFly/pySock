import socket
from time import sleep

HOST = '127.0.0.1'
PORT = 4321
address = (HOST, PORT)

def send_message(message, socket):
  socket.sendto(message, address)

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
  print('sending messages')
  send_message(b'login~foo;1234;1\n', sock)
  send_message(b'move~s\n', sock)
  sleep(1.5)
  data = sock.recv(256)
  print('Recieved: ', data)
  sleep(.5)
  data = sock.recv(256)
  print('Recieved: ', data)

  print('logging out:')
  send_message(b'logout\n', sock)

