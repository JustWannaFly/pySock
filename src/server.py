import shelve
import socket
import selectors
import types
from time import time
from commands import Message, SERVER_COMMANDS

HOST = '127.0.0.1'
PORT = 4321
PROTOCOL_VERSION = '1'


class Client:
  
  def __init__(self, address):
    self.input_messages = []
    self.output_messages = []
    self.disconnect = False
    self.player = None
    self.address = address
    self.last_input = time()
  
  def read_input(self):
    print('boo')
    # read all bytes into an input_buffer
    #input_data = self.connection.recv(2048)
    #if len(input_data) > 1024:
      #print('Client sending too much data. Closing client:', self.address)
      #self.disconnect = True
      #input_data = b''
    # parse input_buffer into messages
    #while len(input_data):
      #self.last_input = time()
      #message = Message()
      #input_data = message.parse(input_data)
      #self.input_messages.append(message)
  
  def send_output(self):
    self.output_messages.clear()
    # encode output_messages into an output_buffer
    #output_buffer = ''
    #while len(self.output_messages):
      #message = self.output_messages.pop(0)
      #output_buffer += message.encode()
    # send output_buffer to client as bytes
    #if output_buffer:
      #encoded_output = output_buffer.encode()
      #print('Output from:', self.address, 'data:', encoded_output)
      #self.connection.sendall(encoded_output)

  def step(self):
    if len(self.input_messages):
      message = self.input_messages.pop(0)
      self.output_messages.append(message)
      #if message.action in self.messages:
      #  (self.messages[message.action])(self, message.args)
      #elif self.player:
      #  self.player.do_command(message)
      #  self.output_messages.extend(self.player.output_queue)
      #  self.player.output_queue.clear()
  
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
    
  def do_logout(self, args):
    print('logging out', self.address)
    self.disconnect = True

  def save(self, args=[]):
    print('saving player and closing: {}'.format(self.address))
    with shelve.open('data/users') as users:
      users[self.player.username] = self.player
    #self.connection.close()

class Server:
  def __init__(self, address, timeout=3):
    self.timeout = timeout
    self.address = address
    self.selector = selectors.DefaultSelector()
    self.socket = None
    self.clients = {}
  
  def __login_client(self, address, args):
    if not len(args) == 3:
      print(args)
      print('Malformed login request from', address)
      # TODO reply with error
      return
    username = args[0]
    password = args[1]
    version = args[2]
    if not version == PROTOCOL_VERSION:
      print('login request with bad version from', address)
      # TODO reply with error
      return
    with shelve.open('data/users') as users:
      if not username in users:
        print('User not found:', username)
        # TODO reply with error
      else:
        player = users[username]
        if not player.check_password(password):
          print('Bad credentials for "', username, '"')
          # TODO reply with error
        else:
          print('Logging in "', username, '" from', address)
          client = Client(address)
          client.player = player
          self.clients.update({address: client})
          print('active connections: ', self.clients)
          message = Message(SERVER_COMMANDS.login, ['success'])
          client.output_messages.append(message)
  
  def __disconnect_client(self, client):
    print('disconnecting:', client.address)
    client.save()
    self.clients.pop(client.address)
    print('Total Clients:', len(self.clients))
  
  def __is_timed_out(self, time, client):
    return time - client.last_input > self.timeout

  def open(self):
    if self.socket:
      return

    self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    self.socket.bind(self.address)
    self.socket.setblocking(False)
    self.selector.register(self.socket, selectors.EVENT_READ, data=None)
    print('Listening on', self.address)

  def read(self):
    events = self.selector.select(0)
    for key, mask in events:
      socket = key.fileobj
      data, address = socket.recvfrom(2048)
      client = self.clients.get(address)
      if client is None:
        print('need to login the new address')
        command = Message()
        print('loginRequest: ', data)
        print('commandArgs pre parsing:', command.args)
        data = command.parse(data)
        if command.action == SERVER_COMMANDS.login:
          self.__login_client(address, command.args)
      while data:
        command = Message()
        data = command.parse(data)
        client.input_messages.append(command)
  
  def send(self):
    for client in self.clients.values():
      while len(client.output_messages):
        command = client.output_messages.pop(0)
        print('sending: ', client.address, command.action)
        self.socket.sendto(command.encode(), client.address)

  
  def step_clients(self):
    now = time()
    keys = list(self.clients.keys())
    for key in keys:
      client = self.clients[key]
      # check if should close
      if client.disconnect or self.__is_timed_out(now, client):
        self.__disconnect_client(client)
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
