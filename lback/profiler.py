from lback.client import Client
from lback.utils import Util
import re
import os

"""
Profile based backups
"""
class Profiler(object):
  def __init__(self,profiles,server_ip,server_port,ip,port,db,db_table='backups'):
    self.profiles = profiles
    self.server_ip = server_ip
    self.server_port = server_port
    self.ip = ip
    self.port = port
    self.db = db
    self.db_table = db_table
  def run(self):
    client = Client(self.port, self.ip, dict(ip=self.server_ip, port=self.server_port))
    
    while True:
      now = time.time()
      for i in self.profiles:
        if not os.path.isdir(i['folder']):
          continue
         
        lback_output("Reading scheduled backup")
        lback_output(i.__str__())
        size = str(Util().getFolderSize(i['folder']))
        name = "N/A"
        if 'name' in i.keys():
          name = i['name']
          
        c = self.db((self.db[self.db_table].name == name) & (self.db[self.db_table].folder == i['folder'])).count()
        if c > 0:
          continue

        if i['time'].isdigit():
          dst_time = int(i['time'])
        else:
          ## try parsing the time
          dst_time = datetime.datetime.strptime(i['time'], "%b %d, %Y %H:%M:%S")
          epoch  =datetime.datetime(1970, 1,1)
          delt =   dst_time - epoch
          dst_time =  float((delt.microseconds + (delt.seconds +delt.days *  86400) * 10**6) / 10**6)
   

        if dst_time: 
          if now >= dst_time:
            uid = Record().generate()
            bkp = Backup(uid, i['folder'])
            bkp.run()

            if bkp.status == 1:
              self.db[self.db_table].insert(uid=uid, time=time.time(), folder=i['folder'], local=i['local'],name=name,size=size)
              self.db.commit()
              if i['local']:
                lback_output("Backup Ok -- Now saving to disk")
                lback_output("Local Backup has been successfully stored")
                
              else:
                fc = open(bkp.get(), "r+").read()
                client.run(cmd='BACKUP', folder=i['folder'], uid=uid, contents=fc,name=name,size=size)
                if client.status:
                  lback_output("Backup Ok -- Now transferring to server")
                  
                  fp = client.get()
                  if len(re.findall("SUCCESS", fp)) > 0:
                    lback_output("Remote Backup has been successfully transferred")
                    
                    os.remove(bkp.get())
                  else:
                    lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes")
                else:
                  pass
            else:
              pass
          

