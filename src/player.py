from hashlib import sha256
import world
from commands import PLAYER_COMMANDS, Message

class Player(world.Entity):
  password = ''
  output_queue = []

  def __init__(self, username):
    self.username = username

  def set_password(self, password):
    self.password = sha256(password.encode()).hexdigest()

  def check_password(self, password=''):
    attempt_hash = sha256(password.encode()).hexdigest()
    return attempt_hash == self.password

  def do_command(self, command):
    if command.action == PLAYER_COMMANDS.move:
      self.move(command.args[0])
      message = Message()
      message('position', ['self', self.position])
      self.output_queue.append(message)