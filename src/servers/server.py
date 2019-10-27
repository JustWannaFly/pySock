import socket
import selectors
import types
from time import time

HOST = '127.0.0.1'
PORT = 4321

class Client:
  def __init__(self, connection, address):
    self.connection = connection
    self.address = address
    self.input_buffer = None
    self.output_buffer = None
    self.last_input = time()
    self.disconnect = False
  
  def read_input(self):
    self.input_buffer = self.connection.recv(256)
  
  def send_output(self):
    if self.output_buffer:
      print('Output from:', self.address, 'data:', self.output_buffer)
      self.connection.sendall(self.output_buffer)
      self.output_buffer = None

  def step(self):
    if self.input_buffer:
      self.output_buffer = self.input_buffer
      self.input_buffer = None
  
  def close(self):
    print('closing Client:', self.address)
    self.connection.close()

class Server:
  def __init__(self, address, timeout=5):
    self.timeout = timeout
    self.address = address
    self.selector = selectors.DefaultSelector()
    self.socket = None
    self.clients = {}
  
  def __process_connect(self, socket):
    connection, address = socket.accept()
    connection.setblocking(False)
    client = Client(connection, address)
    self.clients[address] = client
    self.selector.register(connection, selectors.EVENT_READ, data=client)
    print('login from', address)
  
  def __process_disconnect(self, client):
    print('disconnecting:', client.address)
    self.selector.unregister(client.connection)
    client.close()
    self.clients.pop(client.address)
    print('new client keys:', self.clients.keys())
  
  def __is_timed_out(self, time, client):
    return time - client.last_input > self.timeout

  def open(self):
    if self.socket:
      return

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.bind(self.address)
    self.socket.listen()
    self.socket.setblocking(False)
    self.selector.register(self.socket, selectors.EVENT_READ, data=None)
    print('Listening on', self.address)

  def read(self):
    events = self.selector.select(0)
    for key, mask in events:
      socket = key.fileobj
      client = key.data
      if client is None:
        self.__process_connect(socket) 
      else:
        client.read_input()
  
  def send(self):
    for client in self.clients.values():
      client.send_output()
  
  def step_clients(self):
    now = time()
    keys = list(self.clients.keys())
    for key in keys:
      client = self.clients[key]
      # check if should close
      if client.disconnect or self.__is_timed_out(now, client):
        self.__process_disconnect(client)
      # steps clients
      else:
        client.step()

  def close(self):
    self.socket.close()
    self.socket = None
    self.clients = {}
    print('Closing socket at', self.address)
  

def main():
  server = Server((HOST, PORT))
  server.open()

  while True:
    server.read()
    server.step_clients()
    server.send()


if __name__ == "__main__":
    main()  
