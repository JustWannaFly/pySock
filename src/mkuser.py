import sys
import shelve

from player import Player

def main(args):
  print('arg length', len(args))
  if not len(args) == 3:
    print('Bad arguments, must supply username and password')
    return
  
  username = args[1]
  password = args[2]

  player = Player(username)
  player.set_password(password)

  with shelve.open('data/users') as users:
    users[username] = player

  print('Successfully created user', username)

if __name__ == "__main__":
    main(sys.argv)
    sys.exit(0)
