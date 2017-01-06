
from lback.utils import LBack_Protobuf_Message,recvall,lback_output
import socket
  


class Client(object):
  def __init__(self, ip, port, server=dict()):
    self.status = 0
    self.server = server
  
  def run(self, cmd='BACKUP', folder=None, id='', contents='',name='',version='1.0.0',size=0, jit=False):
    s = socket.socket()
    size = str(size)
    #s.setblocking(0)
    s.connect((self.server['ip'], int(self.server['port'])))
    #smessage = cmd + ', ' + 'UID: "' + id + '", ' + 'FOLDER: "' + os.path.abspath(folder) + '", '  + 'JIT: "' + str(jit) +  '", ' +  "SIZE: " + size + ', ' + "VERSION: " + version + ', ' + "NAME: " + name + "\nCONTENTS: " + contents
    smessage = LBack_Protobuf_Message()
    smessage.CMD = cmd
    smessage.UID = id
    smessage.FOLDER = folder
    smessage.JIT = jit 
    smessage.SIZE = str(size)
    smessage.VERSION  =version
    smessage.NAME = name
    smessage.CONTENTS = contents.encode("hex").encode("utf-8")
    lback_output("Message passing: (FOLDER: %s, SIZE: %s, UID: %s, JIT: %s, VERSION: %s)" % (folder, str(size), str(id), str(jit), str(version)))

    s.sendall(smessage.SerializeToString())
    out = False
    ###  shorter spurts for commands not
    ## needing heavy TCP/IP communication
    if cmd == 'BACKUP' or  cmd == 'DELETE':
      self.m = recvall(s)
    else:
      self.m = ""
      while True:
        if out:
          break
        try:
          m = s.recv(2048)
          if not m:
            break
          if m == "":
            out = True
            break
          if m != "" or m:
            self.m += m
          
        except socket.error, e:
          lback_output("??")
          if e.errno != errno.EAGAIN:
            raise e
            
          select.select([s], [], [])
          
    try:
      the_message = LBack_Protobuf_Message() 
      the_message.ParseFromString(self.m)
      s.close()
      self.status = 1
      return ClientReply(the_message.STATUS, the_message) 
      #if the_message.STATUS == "SUCCESS":
         
      #if len(re.findall("CONTENTS:\s+", self.m)) > 0:
      #  self.m = re.sub('SUCCESS.*\n', '', self.m)
      #  self.m = re.sub(".*CONTENTS:\s+", "", self.m)
    except:
      the_message  = LBack_Protobuf_Message()
      the_message.STATUS = "FAIL"
      s.close()  
      self.status = 0
      return ClientReply(the_message.STATUS, the_message)
  
  def get(self):
    return self.m
  
  def send(self, data):
    pass
    
  def receive(self, data):
    pass
 
class ClientReply(object):
  def __init__(self,status, lback_message):
    self.status = status
    self.msg = lback_message
 

