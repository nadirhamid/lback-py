
import time,socket
import os
import sys
import  zipfile
import json
import uuid
import MySQLdb
import tempfile
import errno
import hashlib
import time
import tarfile
import sys
import base64
import shutil
from termcolor import colored
from hashlib import md5
from Crypto.Cipher import AES
from Crypto import Random
from . import log




def lback_init_if_needed():
  if not os.path.exists( lback_dir() ):
      os.makedirs(lback_dir())
      os.makedirs(lback_backup_path())
      if getattr(sys, 'frozen', False):
        # If the application is run as a bundle, the pyInstaller bootloader
        # extends the sys module by a flag frozen=True and sets the app 
        # path into variable _MEIPASS'.
        application_path = sys._MEIPASS
      else:
        application_path = os.path.dirname(os.path.abspath(__file__))
      lback_output("INITIALIZING FIRST USE OF LBACK AT PATH %s"%(application_path))

      initial_settings_file = os.path.abspath(os.path.join(application_path, "..", "conf", "settings.json"))
      user_settings_file = os.path.join("%s/settings.json"%(lback_dir()))
      lback_output("COPIYING PATH SETTINGS %s TO %s"%(initial_settings_file, user_settings_file))
      shutil.copy(
            initial_settings_file,
            user_settings_file
      )
      settings_file = lback_resolve_path("settings.json")
      with open(settings_file, "r+") as file:
           config = json.loads( file.read() )
      db = config['master']['database']
      connection = MySQLdb.connect(db['host'], db['user'], db['pass'], db['name'])
      cursor = connection.cursor()
      cursor.execute(r"""DROP TABLE IF EXISTS backups""")
      cursor.execute(r"""DROP TABLE IF EXISTS agents""")
      cursor.execute(r"""
         CREATE TABLE backups (
         id VARCHAR(255),
         name VARCHAR(50),
         time DOUBLE,
         folder VARCHAR(255),
         dirname VARCHAR(255),
         size VARCHAR(255),
         encryption_key VARCHAR(255) DEFAULT NULL,
         distribution_strategy VARCHAR(255) DEFAULT "shared",
         shards_total smallint(3)
        ); """)
      cursor.execute(r"""
         CREATE TABLE agents (
         id VARCHAR(255),
         host VARCHAR(50),
         port VARCHAR(5)
        ); """)
      ## add local agent by default
      localhost_agent_host = "127.0.0.1"
      localhost_agent_port = "5750"
      lback_output("ADDING LOCALHOST AGENT ON %s:%s"%( localhost_agent_host, localhost_agent_port ) )
      cursor.execute(r"""INSERT INTO agents(id, host, port) VALUES (%s, %s, %s)""", (lback_id(), localhost_agent_host, localhost_agent_port, ) )
      connection.commit()
      lback_output("INITIZATION DONE. FOR LBACK SUPPORT AND COMMENTS PLEASE GO TO http://lback.io/support/")

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
    return ""

def lback_temp_dir():
    return lback_dir()+"/temp/"

def lback_temp_path():
   return "{}/{}".format(lback_temp_dir(), str(uuid.uuid4()))
def lback_temp_file():
    tfile = tempfile.NamedTemporaryFile()
    tfile.write("")
    tfile.seek(0)
    tfile.close()
    return open(tfile.name,"wb")

def lback_resolve_path(file):
   local_path = "%s/%s"%(lback_dir(), file)
   if os.path.exists( local_path ):
       return local_path
   global_path =  "/etc/lback/%s"%( file )
   if not os.path.exists(global_path):
       return None
   return global_path



def lback_settings():
   import json
   file = open( lback_resolve_path("settings.json"), "r+" )
   return json.loads( file.read() ) 

def lback_backup_path( id="", shard=None, suffix="" ):
   text = "{}/{}{}".format(lback_backup_dir(), id, lback_backup_ext())
   if not shard is None:
       text = "{}/{}_{}{}".format(lback_backup_dir(), id, shard, lback_backup_ext())
   return "{}{}".format( text, suffix )


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



def lback_backup_chunked_file( id, chunk_size=128000, chunk_start=0, chunk_end=None ):
   bytes_read = [0]
   path = lback_backup_path( id )
   file_size = os.stat( path ).st_size
   if file_size < chunk_size:
      chunk_size = file_size
   if not chunk_end:
      chunk_end = file_size
   bytes_needed = ( chunk_end - chunk_start )
   def read_bytes():
      bytes_remaining = ( bytes_needed - bytes_read[ 0 ] )
      increment = chunk_size
      if bytes_remaining < chunk_size:
         increment = bytes_remaining

      if bytes_needed == bytes_read[ 0 ]:
         return ""
      content = file_handler.read( chunk_size )

      bytes_read[0] += increment
      lback_output("BYTES READ %s/%s"%( bytes_read[0], bytes_needed ) )
      return content

   with open( path, "rb" ) as file_handler:
       file_handler.seek( chunk_start )
       content = read_bytes()
       while content!="":
         packed_content = content
         content = read_bytes()
         yield packed_content

def lback_agents( transform_cls = None ):
   if transform_cls is None:
     from .agent import AgentObject
     transform_cls = AgentObject

   db = lback_db()
   select_cursor = db.cursor()
   select_cursor.execute("SELECT * FROM agents")
   db_agent = select_cursor.fetchone()
   agents = []
   while db_agent:
	agents.append( transform_cls( db_agent ) )
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
   while db_backup:
	backups.append( BackupObject( db_backup ) )
	db_backup = select_cursor.fetchone()
   return backups


def lback_backup_remove( id, shard=None ):
   os.remove( lback_backup_path( id=id, shard=shard ) )

def lback_backup_move( backup_path_1, backup_path_2 ):
   shutil.move( backup_path_1, backup_path_2 )

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
    return "{}_T".format(existing_id)

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

def lback_make_temp_backup(backup):
  temp_backup_id = lback_id_temp( backup.id )
  real_backup_path = lback_backup_path( backup.id )
  temp_backup_path = lback_backup_path( temp_backup_id )
  shutil.copy( real_backup_path, temp_backup_path )
  return temp_backup_id

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

