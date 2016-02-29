""" Backup tool for linux.  This performs ehe needed functionality
behind this specifcation.

Implementors must deciede which 
version to run and on what port. This
file acts as 'both' a client and server
and can be started from the command line
via -c or -s respectively.
"""
"""
guide to commands

NEEDS to work on OpenSUSE with RPM
and compiled in py2exe and p2app

"""

from dal import DAL, Field
import errno
import subprocess
import threading
import datetime
import zipfile
import shutil
import socket
import select
import glob
import time
import json
import uuid
import sys
import os
import re

import zipfile,os.path
from datetime import timedelta

from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor, Descriptor
from google.protobuf.reflection import GeneratedProtocolMessageType



try:
  import boto
  from boto.s3.key import Key
  from boto.s3.connection import S3Connection
except:
  ## no boto
  pass

LOCAL_BACKUP_DIR = '/usr/local/lback/backups/'

def  make_lback_protobuf_field(name, type, type1, idx=0, tag=0, default_value=""):
   return FieldDescriptor(name, name,idx,tag, type, type1,default_value, name,None,None,None,False,None)
def make_lback_protobuf_descriptor(name, fields=[], enum_fields=[], containing_fields=[], nestable_fields=[]):
   return Descriptor(name, name, name, None, fields, nestable_fields, enum_fields, containing_fields)

## UID, NAME, SIZE, VERSION, JIT, FOLDER, CONTENTS, CMD, VERSION, STATUS
uid_field = make_lback_protobuf_field("UID", FieldDescriptor.TYPE_STRING, FieldDescriptor.CPPTYPE_STRING,1,1)
name_field = make_lback_protobuf_field("NAME", FieldDescriptor.TYPE_STRING, FieldDescriptor.CPPTYPE_STRING,2,2)
size_field = make_lback_protobuf_field("SIZE",  FieldDescriptor.TYPE_STRING, FieldDescriptor.CPPTYPE_STRING,3,3)
jit_field =  make_lback_protobuf_field("JIT", FieldDescriptor.TYPE_BOOL, FieldDescriptor.CPPTYPE_BOOL,4,4,False)
folder_field = make_lback_protobuf_field("FOLDER", FieldDescriptor.TYPE_STRING, FieldDescriptor.CPPTYPE_STRING,5,5)
contents_field = make_lback_protobuf_field("CONTENTS", FieldDescriptor.TYPE_STRING, FieldDescriptor.CPPTYPE_STRING,6,6)
cmd_field = make_lback_protobuf_field("CMD", FieldDescriptor.TYPE_STRING,FieldDescriptor.CPPTYPE_STRING,7,7)
version_field = make_lback_protobuf_field("VERSION",FieldDescriptor.TYPE_STRING,FieldDescriptor.CPPTYPE_STRING,8,8)
status_field = make_lback_protobuf_field("STATUS",FieldDescriptor.TYPE_STRING,FieldDescriptor.CPPTYPE_STRING,9,9)

lback_msg_descriptor = make_lback_protobuf_descriptor("LBack_Protobuf_Message", [
    uid_field,
    name_field,
    size_field,
    jit_field,
    folder_field,
    contents_field,
    cmd_field,
    version_field,
    status_field
])
      

class LBack_Protobuf_Message(Message):
  __metaclass__ = GeneratedProtocolMessageType 
  DESCRIPTOR  = lback_msg_descriptor




class Backup(object):
  def __init__(self, record_id, folder='./', client=True):
    global LOCAL_BACKUP_DIR
    if not folder[len(folder) - 1] == "/":
      folder += "/"

    self.things = []
    self.record_id = record_id
    if client:
      self.zip = zipfile.ZipFile(LOCAL_BACKUP_DIR + record_id + '.zip', 'w', zipfile.ZIP_DEFLATED)
    self.status = 0
    self.folder = folder

  def raw(self, content):
    global LOCAL_BACKUP_DIR
    
    try:
      from cStringIO import StringIO
    except:
      from StringIO import StringIO

    #fp = StringIO(content)
    #zfp = zipfile.ZipFile(fp, "w")
    #f = open("./backups/server.zip", "w+")
    f = open(self.get(), "w+")
    f.write(content)
    f.close()
    
    self.status = 1
    
  def run(self, pack=True):
    l = os.listdir(self.folder)
    #self.zip.write(self.folder)
    #self.things.append(self.folder)
    folders = [self._folder(i, self.folder) for i in l if os.path.isdir(self.folder + i)]
    files = [self._file(i, self.folder) for i in l if os.path.isfile(self.folder + i)]
    #self.things = glob.glob(self.folder + "*")
    if pack:
      self.pack()
    
  def get(self):
    return LOCAL_BACKUP_DIR + self.record_id + '.zip'
    
  def pack(self):
    print "Files have been gathered. Forming archive.."
    for i in self.things:
      self.zip.write(i, os.path.relpath(i, self.folder))
    print "Files found: "
    print self.things
    #Util().zip(self.folder, self.get())
    self.zip.close()
    self.status = 1
    

  def _folder(self, anchor, prefix=''):
    l = os.listdir(prefix + anchor)

    folders = [self._folder(i, prefix + anchor + "/") for i in l if os.path.isdir(prefix + anchor + "/" + i)]
    files = [self._file(i, prefix + anchor + "/") for i in l if os.path.isfile(prefix + anchor + "/" + i)]
    self.things.append(prefix + anchor)

    return prefix + anchor
    
  def _file(self, anchor, prefix=''):
    print "added => " + prefix + anchor
    self.things.append(prefix + anchor)
    
    return prefix + anchor
  
class Restore(object):
  def __init__(self, zip_file_loc, folder='./', clean=False):
    self.zip_file,self.status = zip_file_loc, 0
    self.clean = clean
    self.folder = folder
  def run(self, local=False, uid=''):
    global LOCAL_BACKUP_DIR
    if local:
      self.zip_file = LOCAL_BACKUP_DIR + uid + ".zip"

    if self.clean:
      shutil.rmtree(self.folder)
      Util().unzip(self.zip_file, self.folder)
    else:
      Util().unzip(self.zip_file, self.folder)    
    self.status = 1

import time,socket

def recvall(the_socket,timeout=''):
    #setup to use non-blocking sockets
    #if no data arrives it assumes transaction is done
    #recv() returns a string
    the_socket.setblocking(0)
    total_data=[];data=''
    begin=time.time()

    if not timeout:
        timeout=1
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        wait=0
        try:
            data=the_socket.recv(4096)
            if data:
                total_data.append(data)
                begin=time.time()
                data='';wait=0
            else:
                time.sleep(0.1)
        except:
            pass
        #When a recv returns 0 bytes, other side has closed
    result=''.join(total_data)
    return result
  
class Server(object):
  def __init__(self, port, ip, db, table):
    self.status = 0
    self.ip = ip
    self.db = db
    self.port = port
    self.db_table = table
  
  def cmd(self):
    pass
    
  def run(self):
    global LOCAL_BACKUP_DIR
    s = socket.socket()         # Create a socket object
    self.port = int(self.port)              # Reserve a port for your service.
    s.bind((self.ip, self.port))        # Bind to the port
    #s.setblocking(0)

    s.listen(1)                 # Now wait for client connection.
    while True:
       c, addr = s.accept()     # Establish connection with client.
       #print connections
       print 'Got connection from', addr
       
       message = recvall(c)

       protobufMessage = LBack_Protobuf_Message()
       protobufMessage.ParseFromString(message)
       """
       what command is this?
       """
       if protobufMessage.CMD == "RESTORE":
        print "Running 'RESTORE'"
        uid = False
        uid = protobufMessage.UID

        version = protobufMessage.VERSION
        if not uid:
          continue

        if version.lower() == 'latest':
          r = self.db(((self.db[self.db_table].uid == uid) | 
                 (self.db[self.db_table].name == uid) |  
                 (self.db[self.db_table].folder == uid))).select().last()

        elif version.lower() == 'oldest':
          r = self.db(((self.db[self.db_table].uid == uid) | 
                 (self.db[self.db_table].name == uid) |  
                 (self.db[self.db_table].folder == uid))).select().first()

        else:
          r = self.db(((self.db[self.db_table].uid == uid) | 
                 (self.db[self.db_table].name == uid) |  
                 (self.db[self.db_table].folder == uid)) &
                 (self.db[self.db_table].version == version)).select().first()
        if not r:
          print "SERVER couldn\'t find backup.."
          continue
        else:
          uid = row.uid


          
        fi = open(LOCAL_BACKUP_DIR + uid + '.zip', 'r+')
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
          
        print "Restore backup fetched."
        print "Sending to client.."
        print "Transaction ID: " + uid
        c.close()
    
       
       elif protobufMessage.CMD == "DELETE":
         print "Running 'DELETE'"
         uid = protobufMessage.UID
         
         status = os.remove(LOCAL_BACKUP_DIR +  uid + ".zip") 
         if not os.path.isfile(LOCAL_BACKUP_DIR + uid + ".zip"):
           print "Backup deleted successfull.."
           self.db(self.db[self.db_table].uid == uid).delete() 
         else:
           print "Could not delete the backup device or resource busy"
          
       elif protobufMessage.CMD == "BACKUP":
        print "Running 'BACKUP'"
        uid = protobufMessage.UID
        contents = protobufMessage.CONTENTS
        folder = protobufMessage.FOLDER
        name =protobufMessage.NAME
        size = protobufMessage.SIZE
        version = protobufMessage.VERSION
        jit =protobufMessage.JIT
        c.sendall("SUCCESS")
        if not contents:
          continue

        bkp = Backup(uid, folder, False)
        bkp.raw(contents)
        
        if bkp.status:
          """ backed up, send back message """
          self.db[self.db_table].insert(uid=uid, time=time.time(), folder=folder, size=size, local=False, name=name, jit=True, version=version)
          self.db.commit()
          c.sendall("SUCCESS")
          print "Backup complete."
          print "Transaction ID: " + uid
          
        c.close()
       #c.send('Thank you for connecting')
       
       
        
    pass
  
class Output(object):
  def __init__(self):
    pass
  def show(self,msg,times=0):
    if times == 0:
      print(msg)
    else:
      print(msg + "\n" * times)
  
class Client(object):
  def __init__(self, ip, port, server=dict()):
    self.status = 0
    self.server = server
  
  def run(self, cmd='BACKUP', folder=None, uid='', contents='',name='',version='1.0.0',size=0, jit=False):
    s = socket.socket()
    size = str(size)
    #s.setblocking(0)
    s.connect((self.server['ip'], int(self.server['port'])))
    #smessage = cmd + ', ' + 'UID: "' + uid + '", ' + 'FOLDER: "' + os.path.abspath(folder) + '", '  + 'JIT: "' + str(jit) +  '", ' +  "SIZE: " + size + ', ' + "VERSION: " + version + ', ' + "NAME: " + name + "\nCONTENTS: " + contents
    smessage = LBack_Protobuf_Message()
    smessage.CMD = cmd
    smessage.UID = uid
    smessage.FOLDER = os.path.abspath(folder)
    smessage.JIT = jit 
    smessage.SIZE = str(size)
    smessage.VERSION  =version
    smessage.NAME = name
    smessage.CONTENTS = contents.encode("hex").encode("utf-8")
    print "Message passing: (FOLDER: %s, SIZE: %s, UID: %s, JIT: %s, VERSION: %s)" % (folder, str(size), str(uid), str(jit), str(version))

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
          print "??"
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
 
class Record(object):
  def __init__(self):
    pass
  def generate(self):
    return uuid.uuid4().__str__()


"""
Just in time backups
"""
class JIT(object):
  def __init__(self, db, db_table):
    self.db = db
    self.db_table = db_table

  def check(self, record=''):
    while True:
      if record:
        backups = self.db(self.db[self.db_table].uid == record).select()
      else:
        backups = self.db(self.db[self.db_table].jit == True).select()

      for i in backups:
        initial_time = float(i.time)
        local = i.local
        uid = i.uid
        folder = i.folder
        cpath = os.getcwd()
        
        files = os.listdir(folder)

        b = Backup(None, folder, False)
        b.run(False) ## dont actually run.. yet
        
        for f in b.things:
          if os.path.getmtime(f) > initial_time:
            print "Running JIT Backup file was edited.."
            """ time for a backup """
            os.chdir(cpath)
            bkp = Backup(uid, folder)
            bkp.run()

            if bkp.status == 1:
              size = str(Util().getFolderSize(folder))
              self.db(self.db[self.db_table].uid == uid).update(time = time.time(), size=size)
              self.db.commit()

              break

"""
Profile based backups
"""
class Profiler(object):
  def __init__(self,profiles,server_ip,server_port,ip,port,db,db_table):
    self.profiles = profiles
    self.server_ip = server_ip
    self.server_port = server_port
    self.ip = ip
    self.port = port
    self.db = db
    self.db_table = db_table
    self.o = Output()
  def run(self):
    client = Client(self.port, self.ip, dict(ip=self.server_ip, port=self.server_port))
    
    while True:
      now = time.time()
      for i in self.profiles:
        if not os.path.isdir(i['folder']):
          continue
         
        print "Reading scheduled backup" 
        print i.__str__()
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
              self.db[self.db_table].insert(uid=uid, time=time.time(), folder=os.path.abspath(i['folder']), local=i['local'],name=name,size=size)
              self.db.commit()
              if i['local']:
                self.o.show("Backup Ok -- Now saving to disk")
                self.o.show("Local Backup has been successfully stored")
                
              else:
                fc = open(bkp.get(), "r+").read()
                client.run(cmd='BACKUP', folder=i['folder'], uid=uid, contents=fc,name=name,size=size)
                if client.status:
                  self.o.show("Backup Ok -- Now transferring to server")
                  
                  fp = client.get()
                  if len(re.findall("SUCCESS", fp)) > 0:
                    self.o.show("Remote Backup has been successfully transferred")
                    
                    os.remove(bkp.get())
                  else:
                    self.o.show("Something went wrong on the server.. couldnt back that folder. Reverting changes")
                else:
                  pass
            else:
              pass
          
  
    
class Util(object):
  def unzip(self, source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
      for member in zf.infolist():
        # Path traversal defense copied from
        # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
        words = member.filename.split('/')
        path = dest_dir
        for word in words[:-1]:
          drive, word = os.path.splitdrive(word)
          head, word = os.path.split(word)
          if word in (os.curdir, os.pardir, ''): continue
          path = os.path.join(path, word)
        zf.extract(member, os.path.relpath(path))
  def zip(self, source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
      for member in zf.infolist():
        # Path traversal defense copied from
        # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
        words = member.filename.split('/')
        path = dest_dir
        for word in words[:-1]:
          drive, word = os.path.splitdrive(word)
          head, word = os.path.split(word)
          if word in (os.curdir, os.pardir, ''): continue
          path = os.path.join(path, word)
        zf.write(member, path)
  def getFolderSize(self,p,parent=True):
    if not os.path.isfile(p) and not os.path.isdir(p):
      return 0
    #from functools import partial
    
    totalSize = 0 
    if os.path.isdir(p): 
      prepend = os.path.abspath(p)
      files = os.listdir(prepend)
      thisFolderSize = 0 
      for i in files:
        if os.path.isfile(prepend+"/"+i):
          thisFolderSize +=  float(os.path.getsize( prepend+"/"+i ))
        else:
          thisFolderSize += float(self.getFolderSize(prepend+"/"+i,parent=False))
      totalSize += thisFolderSize
     
    if not parent:   
      return float(thisFolderSize)
    else:
      return str(totalSize)
  
class Runtime(object):
  def __init__(self, a):
    global LEGAL_CMDS
    
    self.db_name = ''
    self.db_pass = ''
    self.db_host = ''
    self.db_table = ''
    self.db_user = ''
    self._settings()
    self._profiles()
    self.propagate()
    self.uid = Record().generate()
    self.o = Output()
    self.type = 'CLIENT'
    self.help = 0
    self.clean = 0
    self.name = "N/A"
    self.version = "1.0.0"
    self.is_jit = False
    self.s3 = False
    self.has_version = False

    if not len(a) > 1:
      self.help = True
      self.type = ''

    for _i in range(0, len(a)):
      i = a[_i]
      try:
        j = a[_i + 1]
      except:
        j = a[_i]
        
      if i in ['-c', '--client']:
        self.type = 'CLIENT'
      if i in ['-s', '--server']:
        self.type = 'SERVER'
      if i in ['-h', '--help']:
        self.help = True
      if i in ['-b', '--backup']:
        self.backup = True
      if i in ['-r', '--restore']:
        self.restore = True
      if i in ['-i', '--ip']:
        self.ip = j
      if i in ['-p', '--port']:
        self.port = j
      if i in ['-x', '--compress']:
        self.compress = True
      if i in ['-e', '--encrypt']:
        self.encrypt = True
      if i in ['-l', '--local']:
        self.local = True
      if i in ['-f', '--folder']:
        self.folder = j
      if i in ['-li', '--list']:
        self.list = True
      if i in ['-p', '--profiler']:
        self.profiler = True
        self.type = 'PROFILER'
      if i in ['-rm', '--remove']:
        self.remove = True
      if i in ['-del', '--delete']:
        self.delete = True
      if i in ['-n', '--name']:
        self.name = j
      if i in ['-cl', '--clean']:
        self.clean = True
      if i in ['-id', '--id']:
        self.id = j
      if i in ['-g', '--graceful']:
        self.graceful = True
      if i in ['-re', '--restart']:
        self.restart = True
      if i in ['-st', '--start']:
        self.start = True
      if i in ['-sp', '--stop']:
        self.stop = True
      if i in ['-sn', '--snapshot']:
        self.snapshot = True
      if i in ['-v', '--version']:
        self.version = j 
        self.has_version = True
      if i in ['-j', '--just-in-time', '-jit']:
        self.jit = True
        self.is_jit = True
      if i in ['--settings']:
        self.settings = True
      if i in ['--stop-profiler']:
        self.stop_profiler = True
      if i in ['-st', '--status']:
        self.status = True
      if i in ['-s3', '--s3']:
        self.s3 = True
  
    if self.help:
      self._help()
      return

    if not self.has_version and 'restore' in dir(self):
      self.version = "latest" 

    self.o.show("Running in {0} mode".format(self.type))
    self.perform()
  """
  try to set up the database
  """
  def propagate(self):
    self.db = DAL(self.db_family + '://' + self.db_user + ':' + self.db_pass + '@' + self.db_host + '/' + self.db_name, pool_size=1, migrate_enabled=False)
      
    self.db.define_table(
      self.db_table,
      Field('id'),
      Field('uid'),
      Field('name'),
      Field('time'),
      Field('folder'),
      Field('size'),
      Field('version'),
      Field('jit'),
      Field('local'),
    )

    
  def perform(self):
    is_success = False

    if 'settings' in dir(self):
      self.o.show('Opening settings') 
      os.system('vim /usr/local/lback/settings.json')

    if 'graceful' in dir(self):
      """ TODO add graceful shutdown """
      self.o.show("Stopping server..")
      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      exit()
      return

    if 'stop' in dir(self): 
      self.o.show("Stopping server..")

      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      quit()
      return

    if 'restart' in dir(self):
      self.o.show("Restarting server..")

      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      self.o.show("Started new instance..")

      time.sleep(1)
      os.system("lback-server --start")
      quit()
      return
    
    if 'status' in dir(self):
      self.o.show("Status of SERVER:")
      return

    if 'stop_profiler' in dir(self):
      self.o.show("Stopping profiler..")
      os.system("pkill -f 'python ./lback.py --profiler'")
      os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
      return
    
    if 'folder' in dir(self):
      self.size = Util().getFolderSize(self.folder)
    
    if 'profiler' in dir(self):
      profiler = Profiler(self.profiles,self.server_ip,self.server_port,self.ip,self.port,self.db,self.db_table).run()


    if 'stop-jit' in dir(self):
      self.o.show("Stopping JIT instance..")
      os.system("pkill -f 'python ./lback.py --jit'")
      os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
      return
      
    if not 'local' in dir(self):
      self.isLocal = False
      if self.type == 'CLIENT':
        client = Client(self.port, self.ip, dict(ip=self.server_ip, port=self.server_port))
        self.o.show("Running on port: {0}, ip: {1}".format(self.server_port, self.server_ip))
      else:
        server = Server(self.server_port, self.server_ip, self.db, self.db_table)
        self.o.show("Running on port: {0}, ip: {1}".format(self.server_port, self.server_ip))
        server.run()
        # exit now and loop
    else:
      self.isLocal = True
        
    if 'backup' in dir(self):
      if not 'folder' in dir(self):
        pass
      else:
        self.o.show("Gathering files.. this can take awhile")
        bkp = Backup(self.uid, self.folder)
        bkp.run()
        
        if bkp.status == 1:

          if self.version == '1.0.0':
            """ try to get previous version """
            """ and up the patch by one """
            r = self.db(self.db[self.db_table].folder == self.folder).select().last()

            if r:
              v = r['version'] 
              cv = re.findall("\d\.\d\.(\d)", v)[0]
              nv = int(cv) + 1
              self.version = re.sub('\d$', str(nv), v)
              

          self.db[self.db_table].insert(uid=self.uid, time=time.time(), folder=os.path.abspath(self.folder), size=self.size, local=self.isLocal,name=self.name, version=self.version, jit=True if self.is_jit else False)
          self.db.commit()
        
        
          is_success = True
          
          if self.isLocal:
            self.o.show("Backup Ok -- Now saving to disk")
            self.o.show("Local Backup has been successfully stored")
            self.o.show("Transaction ID: " + self.uid)
          else:
            fc = open(bkp.get(), 'r').read()
            client.run(cmd='BACKUP', folder=os.path.abspath(self.folder), uid=self.uid, contents=fc, name=self.name,version=self.version,size=self.size)
            if client.status:
              self.o.show("Backup Ok -- Now transferring to server")
              
              fp = client.get()
              if len(re.findall("SUCCESS", fp)) > 0:
                self.o.show("Remote Backup has been successfully transferred")
                self.o.show("Transaction ID: " + self.uid)
                os.remove(bkp.get())
              else:
                self.o.show("Something went wrong on the server.. couldnt back that folder. Reverting changes")
            else:
              pass
        else:
          pass
        
    if 'restore' in dir(self):
      if 'id' in dir(self):

        if not self.has_version:
          r = self.db((self.db[self.db_table].uid == self.id)  | \
                      (self.db[self.db_table].name == self.id) | \
                (self.db[self.db_table].folder == self.id)).select().last()

  
        else:

          if self.version == "latest":
            r = self.db((self.db[self.db_table].uid == self.id)  | \
                      (self.db[self.db_table].name == self.id) | \
                (self.db[self.db_table].folder == self.id)).select().last()


          elif self.version.lower() == "oldest":
            r = self.db((self.db[self.db_table].uid == self.id)  | \
                      (self.db[self.db_table].name == self.id) | \
                (self.db[self.db_table].folder == self.id)).select().first()

          else:
            r = self.db(((self.db[self.db_table].uid == self.id)  | \
                   (self.db[self.db_table].name == self.id) | \
                   (self.db[self.db_table].folder == self.id)) \
                 & (self.db[self.db_table].version == self.version)).select().first()

        if not r:
          self.o.show("ERROR: Backup not found.")
          return
          
        self.folder = r['folder']
        self.local = r['local']
        self.ruid = r['uid']

        ## restore an s3 instance
        if s3 in dir(self) and self.s3:
          pass
        
        if self.clean:
          self.o.show("Cleaning directory..")
          if not os.path.isdir(self.folder):
            os.makedirs(self.folder)
          
        if self.isLocal:
          self.o.show("Restore Ok -- Now restoring compartment")
          rst = Restore(False, self.folder, self.clean)
          rst.run(True, self.ruid)  
          
          if rst.status:
            self.o.show("Restore has been successfully performed")
        else:
          self.o.show("Pinging server for restore..")
          client.run(cmd='RESTORE', folder=os.path.abspath(self.folder), uid=self.ruid, version=self.version)
          self.o.show("Forming archive.. this can take some time")
          if client.status:
            self.o.show("Restore Retrieval Ok -- now attempting to restore")
            fp = open(LOCAL_BACKUP_DIR + self.ruid + '.zip', 'w+')
            fp.write(client.get().decode("utf-8").decode("hex"))
            fp.close()
            
            rst = Restore(LOCAL_BACKUP_DIR + self.ruid + '.zip', self.folder, self.clean)
            rst.run(True, self.ruid)
            
            if rst.status:
              self.o.show("Restore Successful")
              
      else:
        pass

    if 'jit' in dir(self):
      if 'id' in dir(self):
        jit = JIT(self.db, self.db_table).check(self.id)
      else:
        self.o.show("Starting a JIT instance on this backup")
        os.system("lback-jit --id '{0}' > /dev/null 2>&1".format(self.uid))


    ## important to check for success
    ## on this command
    
    if 'remove' in dir(self) and is_success:
      if 'folder' in dir(self):
        shutil.rmtree(self.folder)
        self.o.show("Directory successfully deleted..")
    if 'delete' in dir(self):
      client = Client(self.port, self.ip, dict(ip=self.ip,port=self.port))
      if 'id' in dir(self):
        row =self.db(self.db[self.db_table].uid == self.id).select().first()
        
        if row:
          print "Removing backup: " + row.name
     
          if not row.local: 
            client.run("DELETE",  uid=row.uid)
            print client.m
          else:
            os.remove(LOCAL_BACKUP_DIR + row.uid+".zip")
            if not os.path.isfile(LOCAL_BACKUP_DIR +  row.uid + ".zip"):
              print "Removed backup successfully"
            else:
              print "Could not delete backup device or resource busy"

          self.db(self.db[self.db_table].uid == self.id).delete()
        else:
          row = self.db(self.db[self.db_table].folder == self.folder).select()
          if len(row) > 0:
            print "There are multiple backups with: " + self.folder
            counter = 1
            counterOfBackups= dict()
            for i in row:
              print "Press " +counter +  " to delete: "  
              print i.as_dict()
              counterOfBackups[counter] =i.uid
              counter += 1
            numberSelected = ""
            while numberSelected != "QUIT":
              numberSelected = raw_input()
              if numberSelected >0  and numberSelected < len(counterOfBackups):
                thisBackup =counterOfBackups[numberSelected]
                theBackup = self.db(self.db[self.db_table].uid == thisBackup).select().first()
                print "removing: " + theBackup.name 
                if not theBackup.local:
                  client.run("DELETE",uid=theBackup.uid) 
                  print client.m
                else:
      
                  os.remove(LOCAL_BACKUP_DIR +theBackup.uid + ".zip")
                  if not os.path.isfile(LOCAL_BACKUP_DIR +   theBackup.uid + ".zip"):
                    print "Removed the backup successfully"
                  else:
                    print "Could not delete the backup device or resource is busy"
    
                self.db(self.db[self.db_table].uid == thisBackup).delete()
                print "removed this backup successfully"
              else:
                print "not a valid number please press one of: " + ",".join(counterOfBackups.keys())
              print "Press QUIT to exit or another number to delete more"

          elif len(row) == 1:
            row = row.first()   
            if not row.local:
              client.run("DELETE",uid=row.uid)
            else:
              os.remove(LOCAL_BACKUP_DIR + row.uid +".zip")
              if not os.path.isfile(LOCAL_BACKUP_DIR +  row.uid + ".zip"):
                print "Backup removed successfully"
              else:
                print "Could not remove the backup" 
            
            self.db(self.db[self.db_table].folder == self.folder).delete()
            print "removed this backup successfully "
          else: 
            print "Could not find this backup"
      
    if 'list' in dir(self):
      rows = self.db(self.db[self.db_table].time > 0).select().as_list()
      self.o.show("Full list of stored backups")
      for i in rows:
        print i
  
  def _help(self):
    print """
usage: lback [options] required_input required_input2
options:
-c, --client     Run a command as a client (required)
-s, --server     Initiate a server (required)
-b, --backup     Run a backup
-r, --restore    Run a restore
-f, --folder     Specify a folder (required *) for backups
-i, --id,        Specify an id (required *) for restores [ this can be a folder or name of backup ]
-n, --name       Name for backup (optional)
-rm, --remove    Remove a directory on backup
-x, --compress   Compress an archive (default)
-l, --list       Generate a full list of your backups
-i, --ip         Specify an ip (overridden by settings.json if found)
-p, --port       Specify a port (overridden by settings.json if found)
-h, --help       Print this text
-del, --delete   Delete a backup
-jit, --just-in-time  Just in time backups (read docs for more) [accepts singular file or document]
-v, --version specify a version to restore (for restores you can use: LATEST|OLDEST)
--settings       Opens settings in VIM

SERVER SPECIFIC
-g, --graceful  Perform a graceful shutdown
-re, --restart  Restart the server
-st, --start    Start the server
-sp, --stop     Force a shutdown
-st, --status   Is the server running or stopped

PROFILER SPECIFIC
-st, --start Start the profiler
--stop_profiler Stop the profiler

JIT SPECIFIC
--st, --start starts a JIT instance
--stop        Stop the JIT instance
    """
  
  def try_hard_to_find(self):
    pass
    
  def _settings(self):
    if os.path.isfile("/usr/local/lback/settings.json"):
      settings = json.loads(open("/usr/local/lback/settings.json").read())
    elif os.path.isfile("../settings.json"):
      settings = json.loads(open("../settings.json").read())
    for i in settings.keys():
      setattr(self, i, settings[i])
      
    self.ip = settings['client_ip']
    self.port = settings['client_port']
    self.server_ip = settings['server_ip']
    self.server_port = settings['server_port']
    
    if not 'db_family' in settings.keys():
      self.db_family = 'mysql'
    else:
      self.db_family = settings['db_family']
        
  def _profiles(self):
    if os.path.isfile("/usr/local/lback/profiles.json"):
      self.profiles = json.loads(open("/usr/local/lback/profiles.json").read())
    elif os.path.isfile("../profiles.json"):
      self.profiles = json.loads(open("../profiles.json").read()) 

  
if __name__ == '__main__':
  r = Runtime(sys.argv)
