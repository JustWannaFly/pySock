from constants.general import Directions

next_id = 1

class Entity:
  id=0
  position=(0,0)

  def __init__(self):
    global next_id
    self.id = next_id
    next_id += 1
  
  def do_command(self, command):
    '''No-op stub so all entities have ability to do commands'''

  def serialize(self):
    return '' + self.position

  def move(self, direction):
    print('direction to move: {}'.format(direction))
    x = self.position[0]
    y = self.position[1]
    if direction == Directions.north.value:
      print('north')
      y -= 1
    if direction == Directions.south.value:
      y += 1
    if direction == Directions.east.value:
      x += 1
    if direction == Directions.west.value:
      x -= 1
    self.position = (x, y)
