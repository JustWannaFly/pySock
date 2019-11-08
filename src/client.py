import socket
from time import sleep

HOST = '127.0.0.1'
PORT = 4321

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print('sending messages')
    sock.sendall(b'login:foo,1234,1\n')
    sock.sendall(b'mov:dog,cat,fish,bird\n')
    sleep(.5)
    data = sock.recv(256)
    sleep(.5)
    sock.sendall(b'logout\n')

print('Recieved: ', data)
