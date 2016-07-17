
import time,socket
import os
import  zipfile
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor, Descriptor
from google.protobuf.reflection import GeneratedProtocolMessageType
from dal import DAL, Field

import hashlib
import time
import tarfile


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

## Either short ID (7 char
def check_for_id(id_initial, db):
   id = -1
   if  len(id_initial) == 7:
	chunks=db(db.backups.uid.like(id_initial+"%")).select().first()
	if chunks:
	    id=chunks.uid
	else:
	    id=0
   elif len(id_initial) == 40:
	 chunks = db(db.backusp.uid==id_initial).select().first()
	 if chunks:
	      id=chunks.uid
	 else:
	      id=0
   return throw_id_error_if_needed( id )

def throw_id_error_if_needed( id ):
   if id == 0:
      raise Exception("Error record was not found")
   elif id == -1:
      raise Exception("Please provide a short hash (5 characters) or long (40 characters)")
   return id


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
def lback_output(*args,**kwargs):
  show_tag=False if 'tag'in kwargs.keys() and not kwargs['tag'] else True
  if show_tag:
    for i in args:
      print "LBACK: {0}".format( i )
  else:
    for i in args:
      print i
def lback_backup_dir():
    return "/usr/local/lback"
def lback_backup_ext():
    return ".tar.gz"
def lback_uuid():
    return hashlib.sha1(str(time.time())).hexdigest()
def lback_db( ):
  db = DAL('sqlite://db.sql', folder='/usr/local/lback/')
  db.define_table(
      "backups",
      Field('id'),
      Field('uid'),
      Field('name'),
      Field('time'),
      Field('folder'),
      Field('size'),
      Field('version'),
      Field('jit'),
      Field('local'),
      migrate=True
    )
  db.define_table(
	 "users",
	 Field('id'),
	 Field('username'),
	 Field('password'),
	migrate=True
   )


  return db
def lback_auth_user( username, password ):
    db = lback_db()
    user =  db((db.users.username==username) & (db.users.password==password)).select().first()
    return user
   

  

class Util(object):
  def unzip(self, source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
      for member in zf.infolist():
        # Path traversal defense copied from
        # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
        try:
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
              drive, word = os.path.splitdrive(word)
              head, word = os.path.split(word)
              if word in (os.curdir, os.pardir, ''): continue
              path = os.path.join(path, word)
            zf.extract(member, os.path.relpath(path))
        except Exception, e:
            lback_output("Unable to extract {}".format(member.filename))
  def untar(self, source_filename, dest_dir):
	try:
 	  tarfile.TarFile( source_filename ).extractall( dest_dir )
	except Exception, e:
	   lback_output("Unable to extract {}".format(source_filename))
	
	
          
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
      return float(totalSize)
  def getFileSize(self,path):
	 return float(os.path.getsize( path ))
 
