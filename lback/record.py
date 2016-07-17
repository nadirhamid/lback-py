import hashlib
import time
from  lback.utils  import lback_uuid

class Record(object):
  def __init__(self):
    pass
  def generate(self):
     return lback_uuid()

