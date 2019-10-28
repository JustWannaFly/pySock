

class Command:

  def __init__(self):
    self.endOfCommand = '\n'
    self.command = ''
    self.args = []

  def decode(self, input_string=[]):
    self.command = input_string[:4]
    return input_string[4:]

  def encode(self): 
    output = self.command
    return output + self.endOfCommand
