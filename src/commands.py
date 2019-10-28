
command_end = '\n'
function_end = ':'
arg_separator = ','


def find_char(string='', char=''):
  """ Returns the index of the first occurence of a character in a string or len(string) if character is not found """
  index = string.find(char)
  if index < 0:
    index = len(string)
  return index
class Command:
  # TODO verify the special parsing characters cannot be in the command parts
  def __init__(self):
    self.command = ''
    self.args = []

  def decode(self, input_string=''):
    # isolate the first command in the input string
    end_index = find_char(input_string, command_end)
    command_string = input_string[:end_index]
    
    # parse the command's function
    function_end_index = find_char(command_string, function_end)
    self.command = command_string[:function_end_index]
    command_string = command_string[function_end_index + 1:]

    # parse the command's args
    while len(command_string):
      separator_index = find_char(command_string, arg_separator)
      self.args.append(command_string[:separator_index])
      command_string = command_string[separator_index + 1:]

    # return any input after the command ended for future processing
    return input_string[end_index + 1:]

  def encode(self): 
    output = self.command + function_end
    for arg in self.args:
      output += arg + arg_separator
    # remove the last separator as it's not needed
    output = output[:-1]
    return output + command_end
