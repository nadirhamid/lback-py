
import time,socket
import os
import  zipfile
import json
from google.protobuf.message import Message
from google.protobuf.descriptor import FieldDescriptor, Descriptor
from google.protobuf.reflection import GeneratedProtocolMessageType
from . import log
from termcolor import colored
import uuid
import MySQLdb
import tempfile
import errno
import hashlib
import time
import tarfile
import sys



def lback_output(*args,**kwargs):
  type = kwargs['type'] if "type" in kwargs.keys() else "INFO"
  tag = kwargs['tag'] if "tag" in  kwargs.keys() else True
  fn = getattr(log, type.lower())
  for i in args:
	fn( i )

def lback_error(exception, silent=False):
   from traceback import print_exc
   print_exc( exception )
   if silent:
     return
   try:
     sys.stderr.write( "%s\n"%(str( exception )) ) 
     sys.exit(1) # Or something that calls sys.exit()
   except SystemExit as e:
     sys.exit(e)
   except:
    # Cleanup and reraise. This will print a backtrace.
    # (Insert your cleanup code here.)
    raise

def lback_print(text,color):
   print colored( text, color )

def lback_exception( ex ) :
   return ex
def lback_dir():
    from os import getenv
    return "{}/.lback".format(getenv("HOME"))
def lback_backup_dir():
    return lback_dir()+"/backups/"

def lback_backup_ext():
    return ".tar.gz"

def lback_settings():
   file = open("%s/settings.json"%(lback_dir()), "r+")
   import json
   return json.loads( file.read() ) 

def lback_backup_path( id ):
   return "{}/{}{}".format(lback_backup_dir(), id, lback_backup_ext())

def lback_backup( id ):
   from .backup import BackupObject
   db = lback_db()
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM backups WHERE id = %s LIMIT 1", ( id, ))
   db_backup = select_cursor.fetchone()
   return BackupObject(db_backup)

def lback_backup_chunked_file( id, chunk_size= 1024 ):
   file_handler = open( lback_backup_path( id ), "rb" )
   content = file_handler.read( chunk_size )
   while content:
	yield content
	content = file_handler.read( chunk_size )

def lback_agents():
   from .agent import AgentObject
   db = lback_db()
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM agents")
   db_agent = select_cursor.fetchone()
   agents = []
   while db_agent:
	agents.append( AgentObject( db_agent ) )
	db_agent = select_cursor.fetchone()
   return agents

def lback_backup_remove( id ):
   os.remove( lback_backup_path( id ) )

def lback_id(salt=""):
    return hashlib.sha1("{}_{}".format(salt, uuid.uuid4())).hexdigest()
def lback_id_temp(existing_id):
    return "{}-TEMP".format(existing_id)

def lback_validate_id(id):
   if not len( id ) > 6:
	raise Exception("ID should be more than 6 characters")

def lback_untitled():
   return "Untitled"

def lback_db( ):
  from os import getenv
  config = lback_settings()
  db = config['master']['database']
  connection = MySQLdb.connect(db['host'], db['user'], db['pass'], db['name'])
  return connection
def untar(source_filename, dest_dir):
    try:
       tarfile.TarFile( source_filename ).extractall( dest_dir )
    except Exception, e:
       lback_output("Unable to extract {}".format(source_filename), type="ERROR")
def get_folder_size(p,parent=True):
  if not os.path.isfile(p) and not os.path.isdir(p):
      return 0
  total_size = 0 
  if os.path.isdir(p): 
    prepend = os.path.abspath(p)
    files = os.listdir(prepend)
    this_folder_size = 0 
    for i in files:
      if os.path.isfile(prepend+"/"+i):
        this_folder_size +=  float(os.path.getsize( prepend+"/"+i ))
      else:
        this_folder_size += float(get_folder_size(prepend+"/"+i,parent=False))
    total_size += this_folder_size
    if not parent:   
      return float(this_folder_size)
    else:
      return float(total_size)
def get_file_size(path):
  return float(os.path.getsize( path ))

def is_writable( path ):
    try:
	if os.path.isdir( path ):
	  testfile = tempfile.TemporaryFile(dir = path)
	  testfile.close()
	else:
	  file = open( path, "a" )
	  file.close()
    except OSError as e:
        if e.errno == errno.EACCES:  # 13
           return False
        e.filename = path
        raise
    return True

