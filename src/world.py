
next_id = 1

class Entity:
  id=0
  position=(0,0)
  output_queue=[]

  def __init__(self):
    global next_id
    self.id = next_id
    next_id += 1
  
  def do_command(self, command):
    self.output_queue.append(command)

  def serialize(self):
    return '' + self.position
