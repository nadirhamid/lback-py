
from .utils import LBack_Protobuf_Message,recvall,lback_backup_dir,lback_output
import socket
import time
class Server(object):
  def __init__(self, port, ip, db, table='backups'):
    self.status = 0
    self.ip = ip
    self.db = db
    self.port = port
    self.db_table = table
  
  def cmd(self):
    pass
    
  def run(self):
    backupDir = lback_backup_dir()
    s = socket.socket()         # Create a socket object
    self.port = int(self.port)              # Reserve a port for your service.
    s.bind((self.ip, self.port))        # Bind to the port
    #s.setblocking(0)

    s.listen(1)                 # Now wait for client connection.
    while True:
       c, addr = s.accept()     # Establish connection with client.
       #lback_output(connections
       lback_output('Got connection from', addr)
       
       message = recvall(c)

       protobufMessage = LBack_Protobuf_Message()
       protobufMessage.ParseFromString(message)
       """
       what command is this?
       """
       if protobufMessage.CMD == "RESTORE":
        lback_output("Running 'RESTORE'")
        id = protobufMessage.ID

        version = protobufMessage.VERSION

        if version.lower() == 'latest':
          r = self.db(((self.db[self.db_table].id == id) | 
                 (self.db[self.db_table].name == id) |  
                 (self.db[self.db_table].folder == id))).select().last()

        elif version.lower() == 'oldest':
          r = self.db(((self.db[self.db_table].id == id) | 
                 (self.db[self.db_table].name == id) |  
                 (self.db[self.db_table].folder == id))).select().first()

        else:
          r = self.db(((self.db[self.db_table].id == id) | 
                 (self.db[self.db_table].name == id) |  
                 (self.db[self.db_table].folder == id)) &
                 (self.db[self.db_table].version == version)).select().first()
        if not r:
          lback_output("SERVER couldn\'t find backup..")
          continue
        else:
          id = row.id


          
        fi = open(backupDir + id + '.zip', 'r+')
        contents = fi.read()
        fi.close()
        #fullmsg = "SUCCESS" + "\n" + "CONTENTS: " + contents
        fullmsg = LBack_Protobuf_Message()
        fullmsg.STATUS = "SUCCESS"
        fullmsg.CONTENTS = contents
        rawcontents = fullmsg.SerializeToString()
        it = 0
        while True:
          try:
            tmsg = rawcontents[it:it+2048]
            if tmsg != "":
              c.send(tmsg)
            else:
              break
            it += 2048
          except socket.error, e:
            if e.errno != errno.EAGAIN:
              raise e
              
            select.select([], [c], [])
          
        lback_output("Restore backup fetched.")
        lback_output("Sending to client..")
        lback_output("Transaction ID: " + id)
        c.close()
    
       
       elif protobufMessage.CMD == "DELETE":
         lback_output("Running 'DELETE'")
         id = protobufMessage.ID
         
         status = os.remove(backupDir +  id + ".zip") 
         if not os.path.isfile(backupDir + id + ".zip"):
           lback_output("Backup deleted successfull..")
           self.db(self.db[self.db_table].id == id).delete() 
         else:
           lback_output("Could not delete the backup device or resource busy")
          
       elif protobufMessage.CMD == "BACKUP":
        lback_output("Running 'BACKUP'")
        id = protobufMessage.ID
        contents = protobufMessage.CONTENTS
        folder = protobufMessage.FOLDER
        name =protobufMessage.NAME
        size = protobufMessage.SIZE
        version = protobufMessage.VERSION
        jit =protobufMessage.JIT
        c.sendall("SUCCESS")
        if not contents:
          continue

        bkp = Backup(id, folder, False)
        bkp.raw(contents)
        
        if bkp.status:
          """ backed up, send back message """
          self.db[self.db_table].insert(id=id, time=time.time(), folder=folder, size=size, local=False, name=name, jit=True, version=version)
          self.db.commit()
          c.sendall("SUCCESS")
          lback_output("Backup complete.") 
          lback_output("Transaction ID: " + id)
          
        c.close()
       #c.send('Thank you for connecting')
       
       
        
    pass
  

