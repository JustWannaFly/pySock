import socket
import selectors
import types

HOST = '127.0.0.1'
PORT = 45678

def accept_wrapper(sock):
  conn, addr = sock.accept()
  print('Accepted connection from: ', addr)
  conn.setblocking(False)
  data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'', test='')
  events = selectors.EVENT_READ | selectors.EVENT_WRITE
  selector.register(conn, events, data=data)

def service_connection(key, mask):
  sock = key.fileobj
  data = key.data
  print('key:', key)
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(256)
    if recv_data:
      data.outb += recv_data
    else:
      print('closing connection to: ', data.addr)
      selector.unregister(sock)
      sock.close()
  if mask & selectors.EVENT_WRITE:
    if data.outb:
      print('echoing', repr(data.outb), 'to', data.addr)
      sent = sock.send(data.outb)
      data.outb = data.outb[sent:]

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen()
print('Listening on', (HOST, PORT))
sock.setblocking(False)

selector = selectors.DefaultSelector()
selector.register(sock, selectors.EVENT_READ, data=None)

while True:
  events = selector.select(timeout=None)
  for key, mask in events:
    if key.data is None:
      accept_wrapper(key.fileobj) 
    else:
      service_connection(key, mask)
