import socket

HOST = '127.0.0.1'
PORT = 4321

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
  sock.connect((HOST, PORT))
  print('sending "Hello World!"')
  sock.sendall(b'Hello World!')
  data = sock.recv(256)

print('Recieved: ', repr(data))
