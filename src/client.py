import socket
from time import sleep

HOST = '127.0.0.1'
PORT = 4321

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  print('sending messages')
  sock.sendall(b'Hello World!\n')
  sock.sendall(b'Time to rise and shine\n')
  sock.sendall(b'mov:dog,cat,fish,bird\n')
  sleep(.5)
  data = sock.recv(256)

print('Recieved: ', data)
