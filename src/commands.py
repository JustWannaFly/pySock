command_end = b'\n'
action_end = b'~'
arg_separator = b';'

class SERVER_COMMANDS:
  login = 'login'
  logout = 'logout'

class PLAYER_COMMANDS:
  move = 'move'

class Message:
  def __init__(self):
    self.action = ''
    self.args = []

  def build(self, action, args=[]):
    self.action = action
    for arg in args:
      self.args.append(str(arg))

  def parse(self, input_data=b''):
    # isolate the first command in the input string
    input_parts = input_data.partition(command_end)
    this_command = input_parts[0]
    
    # parse the command's function
    command_parts = this_command.partition(action_end)
    self.action = command_parts[0].decode()
    this_command = command_parts[2]

    # parse the command's args
    while len(this_command):
      arg_parts = this_command.partition(arg_separator)
      self.args.append(arg_parts[0].decode())
      this_command = arg_parts[2]

    # return any input after the command ended for future processing
    return input_parts[2]

  def encode(self): 
    output = self.action + action_end.decode()
    for arg in self.args:
      output += arg + arg_separator.decode()
    # remove the last separator as it's not needed
    output = output[:-1]
    return output + command_end.decode()
