import socket
import selectors
import types
from time import time
from commands import Command

HOST = '127.0.0.1'
PORT = 4321

class Client:
  def __init__(self, connection, address):
    self.connection = connection
    self.address = address
    self.input_buffer = ''
    self.output_buffer = ''
    self.last_input = time()
    self.input_commands = []
    self.output_commands = []
    self.disconnect = False
  
  def read_input(self):
    self.input_buffer = self.input_buffer + self.connection.recv(32).decode()
    while len(self.input_buffer):
      self.last_input = time()
      command = Command()
      self.input_buffer = command.decode(self.input_buffer)
      self.input_commands.append(command)
  
  def send_output(self):
    while len(self.output_commands):
      command = self.output_commands.pop(0)
      self.output_buffer += command.encode()

    if len(self.output_buffer):
      encoded_output = self.output_buffer.encode()
      print('Output from:', self.address, 'data:', encoded_output)
      self.connection.sendall(encoded_output)
      self.output_buffer = ''

  def step(self):
    while len(self.input_commands):
      command = self.input_commands.pop(0)
      self.output_commands.append(command)
  
  def close(self):
    print('closing Client:', self.address)
    self.connection.close()

class Server:
  def __init__(self, address, timeout=3):
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
    print('Total Clients:', len(self.clients))
  
  def __process_disconnect(self, client):
    print('disconnecting:', client.address)
    self.selector.unregister(client.connection)
    client.close()
    self.clients.pop(client.address)
    print('Total Clients:', len(self.clients))
  
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
        try:
          client.read_input()
        except OSError:
          print('error reading from', client.address)
          client.disconnect = True
  
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