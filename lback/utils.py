
import time,socket
import os
import  zipfile
import json
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
import base64
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random



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

def lback_temp_dir():
    return lback_dir()+"/temp/"

def lback_temp_path():
   return "{}/".format(lback_temp_dir(), str(uuid.uuid4()))
def lback_temp_file():
    tfile = tempfile.NamedTemporaryFile()
    tfile.write("")
    tfile.seek(0)
    tfile.close()
    return open(tfile.name,"wb")

def lback_settings():
   file = open("%s/settings.json"%(lback_dir()), "r+")
   import json
   return json.loads( file.read() ) 

def lback_backup_path( id, shard=None ):
   if shard is None:
      return "{}/{}{}".format(lback_backup_dir(), id, lback_backup_ext())
   return "{}/{}_{}{}".format(lback_backup_dir(), id, shard, lback_backup_ext())


def lback_backup( id ):
   from .backup import BackupObject
   db = lback_db()
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM backups WHERE id = %s LIMIT 1", ( id, ))
   db_backup = select_cursor.fetchone()
   return BackupObject(db_backup)

def lback_backup_shard_size( id, count ):
  return ( os.stat( lback_backup_path( id ) ).st_size / count )

def lback_backup_shard_start_end( shard_count, sharded_backup_size ):
  shard_start = ( shard_count * sharded_backup_size )
  shard_end = ( shard_start + sharded_backup_size )
  return [ shard_start, shard_end ]



def lback_backup_chunked_file( id, chunk_size= 1048576, chunk_start=0, chunk_end=None ):
   bytes_read = [0]
   def read_bytes():
      if not ( chunk_end is None ) and ( bytes_read[0] > chunk_end ):
         return ""
      content = file_handler.read( chunk_size )
      bytes_read[0] += chunk_size
      return content

   with open( lback_backup_path( id ), "rb" ) as file_handler:
       file_handler.seek( chunk_start )
       content = read_bytes()
       while content!="":
         lback_output("CHUNK CONTENT")
         lback_output(content)
         packed_content = content
         content = read_bytes()
         yield packed_content

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

def lback_agent_is_available(agent_object):
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.settimeout(2)
   result = sock.connect_ex((agent_object.host, int(agent_object.port)))
   if result == 0:
       return True
   return False

def lback_backups():
   from .backup import BackupObject
   db = lback_db()
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM backups")
   db_backup = select_cursor.fetchone()
   backups = []
   while db_agent:
	backups.append( BackupObject( db_backup ) )
	db_backups = select_cursor.fetchone()
   return backups


def lback_backup_remove( id ):
   os.remove( lback_backup_path( id ) )

def lback_id(id=None,shard=None,salt=""):
    result = ""
    if id is None:
      id = hashlib.sha1("{}_{}".format(salt, str( uuid.uuid4() ))).hexdigest()
    result = id
    if shard is None:
       return result
    result = "{}_{}".format(id, shard)
    return result
def lback_id_temp(existing_id):
    return "{}-TEMP-{}".format(existing_id, str(uuid.uuid4()))

def lback_validate_id(id):
   if not len( id ) > 6:
	raise Exception("ID should be more than 6 characters")

def lback_untitled():
   return "Untitled"

def derive_key_and_iv(password, salt, key_length, iv_length):
    d = d_i = ''
    while len(d) < key_length + iv_length:
        d_i = md5(d_i + password + salt).digest()
        d += d_i
    return d[:key_length], d[key_length:key_length+iv_length]

def lback_encrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = Random.new().read(bs - len('Salted__'))
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    out_file.write('Salted__' + salt)
    finished = False
    while not finished:
        chunk = in_file.read(1024 * bs)
        if len(chunk) == 0 or len(chunk) % bs != 0:
            padding_length = (bs - len(chunk) % bs) or bs
            chunk += padding_length * chr(padding_length)
            finished = True
        out_file.write(cipher.encrypt(chunk))

def lback_decrypt(in_file, out_file, password, key_length=32):
    bs = AES.block_size
    salt = in_file.read(bs)[len('Salted__'):]
    key, iv = derive_key_and_iv(password, salt, key_length, bs)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    next_chunk = ''
    finished = False
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(in_file.read(1024 * bs))
        if len(next_chunk) == 0:
            padding_length = ord(chunk[-1])
            chunk = chunk[:-padding_length]
            finished = True
        out_file.write(chunk)


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

