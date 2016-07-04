import hashlib
import time

class Record(object):
  def __init__(self):
    pass
  def generate(self):
    return hashlib.sha1(str(time.time())).hexdigest()

