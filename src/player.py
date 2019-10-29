from hashlib import sha256

class Player:
  password = ''

  def __init__(self, username):
    self.username = username

  def set_password(self, password):
    self.password = sha256(password.encode()).hexdigest()

  def check_password(self, password=''):
    attempt_hash = sha256(password.encode()).hexdigest()
    return attempt_hash == self.password