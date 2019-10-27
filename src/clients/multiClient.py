import socket
import selectors
import types

HOST = '127.0.0.1'
PORT = 4321
NUM_CONNS = 2
sel = selectors.DefaultSelector()
messages = [b'Message1', b'Message2', b'Message3', b'Message4', b'Message5', b'Message6']

def start_connections():
  server_addr = (HOST, PORT)
  for i in range(0, NUM_CONNS):
    connid = i + 1
    print('Starting connection', connid, 'to', server_addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(server_addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(connid=connid,
                                  msg_total=sum(len(m) for m in messages),
                                  recv_total=0,
                                  messages=list(messages),
                                  outb=b'')
    sel.register(sock, events, data=data)

def service_connection(key, mask):
  sock = key.fileobj
  data = key.data
  if mask & selectors.EVENT_READ:
    recv_data = sock.recv(256)
    if recv_data:
      print('received', repr(recv_data), 'from connection', data.connid)
      data.recv_total += len(recv_data)
    if not recv_data or data.recv_total == data.msg_total:
      print('closing connection', data.connid)
      sel.unregister(sock)
      sock.close()
  if mask & selectors.EVENT_WRITE:
    if not data.outb and data.messages:
      data.outb = data.messages.pop(0)
    if data.outb:
      print('sending', repr(data.outb), 'to connection', data.connid)
      sent = sock.send(data.outb)
      data.outb = data.outb[sent:]

start_connections()
while True:
    events = sel.select(timeout=None)
    for key, mask in events:
      service_connection(key, mask)
