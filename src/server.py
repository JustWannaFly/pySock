import shelve
import socket
import selectors
import types
from time import time
from commands import Command, SERVER_COMMANDS

HOST = '127.0.0.1'
PORT = 4321
PROTOCOL_VERSION = '1'


class Client:
  
  def __init__(self, connection, address):
    self.output_buffer = ''
    self.input_commands = []
    self.output_commands = []
    self.disconnect = False
    self.player = None
    self.connection = connection
    self.address = address
    self.last_input = time()
    self.commands = {
      SERVER_COMMANDS.login: Client.do_login,
      SERVER_COMMANDS.logout: Client.close
    }
  
  def read_input(self):
    # read all bytes into an input_buffer
    input_data = self.connection.recv(2048)
    if len(input_data) > 1024:
      print('Client sending too much data. Closing client:', self.address)
      self.disconnect = True
      input_data = b''
    # parse input_buffer into commands
    while len(input_data):
      self.last_input = time()
      command = Command()
      input_data = command.parse(input_data)
      self.input_commands.append(command)
  
  def send_output(self):
    # encode output_commands into an output_buffer
    output_buffer = ''
    while len(self.output_commands):
      command = self.output_commands.pop(0)
      output_buffer += command.encode()
    # send output_buffer to client as bytes
    if output_buffer:
      encoded_output = output_buffer.encode()
      print('Output from:', self.address, 'data:', encoded_output)
      self.connection.sendall(encoded_output)

  def step(self):
    if len(self.input_commands):
      command = self.input_commands.pop(0)
      if command.command in self.commands:
        (self.commands[command.command])(self, command.args)
      elif self.player:
        self.player.do_command(command)
        if len(self.player.output_queue):
          self.output_commands.append(self.player.output_queue)
  
  def do_login(self, args):
    if not len(args) == 3:
      print('Malformed login request from', self.address)
      self.close()
      return
    username = args[0]
    password = args[1]
    version = args[2]
    if not version == PROTOCOL_VERSION:
      print('login request with bad version from', self.address)
      self.close()
      return
    with shelve.open('data/users') as users:
      if not username in users:
        self.disconnect = True
        print('User not found:', username)
      else:
        player = users[username]
        if not player.check_password(password):
          self.disconnect = True
          print('Bad credentials for "', username, '"')
        else:
          print('Logging in "', username, '" from', self.address)
          self.player = player
    

  def close(self, args=[]):
    print('logging out', self.address)
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
    print('Initial connection from', address)
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
