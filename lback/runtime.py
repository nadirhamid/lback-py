
from lback.record import Record
from lback.utils import lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_uuid,lback_backups,  lback_backup, lback_restores, lback_restore,check_for_id, Util
from lback.profiler import Profiler
from lback.jit import JIT
from lback.restore import Restore
from lback.backup import Backup
from lback.client import Client
from lback.server import Server
from lback.rpc.events import Events,EventMessages,EventTypes,EventObjects,EventStatuses
from lback.rpc.api import RPCMessages
from lback.rpc.meta import BackupMeta,RestoreMeta
from lback.rpc.state import BackupState,RestoreState
from lback.rpc.websocket import BackupServer, WebSocketServer
from os import getenv
from dal import Field

import argparse
import time
import os
import json
def check_arg(args, arg):
   if  arg in dir( args ) and getattr( args, arg ):
      return True
   return False
   
class RuntimeArgs(object):
   def __init__(self,*args,**kwargs):
     self.id= lback_uuid
     for i in kwargs.keys():
	  setattr( self,  i, kwargs[i] )
class Runtime(object):
  db = lback_db()
  db_host= ''
  db_table ='backups'
  db_user_table='users'
  db_user = ''
  def __init__(self, a):
    self._settings()
    self._profiles()
    ##self.propagate()
    ##self.uid = Record().generate()
    ##self.state = BackupState( self.uid )
    self.args = a

    ##self.initv2(a)


  def initv2(self):
    parser = argparse.ArgumentParser()
    parser.add_argument("--adduser", action="store_true",
	 help="Add a  new user to Lback",
	default=False)
    parser.add_argument("--deluser", action="store_true",
	 help="Delete a user from Lback",
	default=False)
    parser.add_argument("--backup", action="store_true",
		help="Backup files and folders"
		)
    parser.add_argument("--client", action="store_true",
		help="Run LBack in client mode",
		default=True	
		)
    parser.add_argument("--restore", action="store_true",
		help="Run a restore"
	)
    parser.add_argument("--server", action="store_true",
		help="Run Lback in server mode"
	)
    parser.add_argument("--folder", 
		help="Select a folder",
		default=""
	)
    parser.add_argument("--id", 
		help="An ID for Lback",
		default=Record().generate()
	)
    parser.add_argument("--rid",
		help="A restore ID for Lback",
		default=Record().generate()
	)
    parser.add_argument("--rpc",
		help="Run the RPC server for Lback",
		action="store_true",
		default=False)
    parser.add_argument("--rpcapi",
		 help="Run LBack in RPC Mode",
		action="store_true",
		default=False)


    parser.add_argument("--name", help="Name for backup", default="Untitled Backup")
    parser.add_argument("--clean", action="store_true",
		help="Clean backup on completion"
	)
    parser.add_argument("--delete", action="store_true",
		help="Delete existing backup"
		)
    parser.add_argument("--remove", action="store_true",
		help="Remove backup when done",
	default=False)
    parser.add_argument("--listall", action="store_true",
		help="List backups",
		default=False)
    parser.add_argument("--listusers", action="store_true",
		default=False)	
    parser.add_argument("--version", default=False,
		help="Select a version tag"
		)
    parser.add_argument("--local",default=True, action="store_true")
    parser.add_argument("--remote", default=False, action="store_true")
    parser.add_argument("--stop", default=False, action="store_true")
    parser.add_argument("--start", default=False, action="store_true")
    parser.add_argument("--restart", default=False, action="store_true")
    parser.add_argument("--graceful", default=False, action="store_true")
    parser.add_argument("--status", default=False, action="store_true")
    parser.add_argument("--settings", default=False, action="store_true")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
 
    parser.add_argument("--snapshot", action="store_true",
		help="Make a snapshot"
		)
    parser.add_argument("--profiler", default=False, action="store_true")
    parser.add_argument("--jit", default=False, action="store_true")
    parser.add_argument("--port", default="8050")
    parser.add_argument("--host", default="0.0.0.0")
    
  
    parser.add_argument("--encrypt", action="store_true",
		help="Make an encrypted backup"	
	)
    parsed = parser.parse_args()
 
    parsed.type ='CLIENT'
    if parsed.server:
	parsed.type == 'SERVER'
    self.args = parsed
    self.perform()
    
 
     


    

  def initv1(self):
    a = self.args
    backupDir = lback_backup_dir()
    ext = lback_backup_ext()
    
    self.uid = Record().generate()
    self.type = 'CLIENT'
    self.help = 0
    args.clean = 0
    args.name = "N/A"
    self.version = "1.0.0"
    self.is_jit = False
    self.s3 = False
    self.version = False
    

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
        self.folder = os.path.abspath(j)+"/"
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
        args.name = j
      if i in ['-cl', '--clean']:
        args.clean = True
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
        self.version = True
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

    if not self.version and 'restore' in dir(self):
      self.version = "latest" 

    lback_output("Running in {0} mode".format(self.type))
    self.args = self
    self.perform()
  """
  try to set up the database
  """
  def propagate(self):
     pass

        
  def perform(self):
    args = self.args
    is_success = False
    backupDir = lback_backup_dir()
    ext = lback_backup_ext()
    

    if check_arg(args,"id"):
        state=BackupState( args.id )
    if check_arg(args,"rid"):
        rstate = RestoreState( args.rid )

    if check_arg(args, "settings"):
      lback_output('Opening settings') 
      os.system('vim /usr/local/lback/settings.json')

    if check_arg(args, "graceful"):
      """ TODO add graceful shutdown """
      lback_output("Stopping server..")
      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      exit()
      return

    if check_arg(args, "stop"):
      lback_output("Stopping server..")

      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      quit()
      return

    if check_arg(args,"start"):
      lback_output("Restarting server..")

      os.system("pkill -f 'python ./lback.py --server'")
      os.system("pkill -f 'python /usr/bin/lback.py --server'")
      lback_output("Started new instance..")

      time.sleep(1)
      os.system("lback-server --start")
      quit()
      return
    
    if check_arg( args, "status" ):
      lback_output("Status of SERVER:")
      return

    if check_arg(args, "profiler" ) and check_arg(args, "stop" ):
      lback_output("Stopping profiler..")
      os.system("pkill -f 'python ./lback.py --profiler'")
      os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
      return
    
    if check_arg(args, "folder" ):
      self.size = str(Util().getFolderSize(args.folder))
    
    if check_arg(args, "jit" ) and check_arg(args, "stop" ):
      lback_output("Stopping JIT instance..")
      os.system("pkill -f 'python ./lback.py --jit'")
      os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
      return

    if check_arg(args, "rpc" ):
	 lback_output("RPC - Starting WebSocket server on {0}:{1}".format( "0.0.0.0", "9000"))
	 #server = SimpleWebSocketServer("0.0.0.0",9000,BackupServer)
	 #server.serveforever()
	 server = WebSocketServer("0.0.0.0", 9000)

	 
	 
      
    if check_arg( args, "server" ):
      args.local = False
      if self.type == 'CLIENT':
        client = Client(self.port, args.host, dict(ip=args.host, port=args.port))
        lback_output("Running on port: {0}, ip: {1}".format(args.port, args.host))
      else:
        server = Server(args.port, args.host, self.db, self.db_table)
        lback_output("Running on port: {0}, ip: {1}".format(args.port, args.host))
        server.run()
        # exit now and loop
    else:
      args.local = True
        
    if check_arg(args, "backup" ):
      if not args.folder:
        pass
      else:
        lback_output("Gathering files.. this can take awhile")
        bkp = Backup(args.id, args.folder, state=state)
	meta= BackupMeta(id=args.id)
        bkp.run()
        
        if bkp.status == 1:

          if check_arg(args, "version") and args.version == '1.0.0':
            """ try to get previous version """
            """ and up the patch by one """
            r = self.db(self.db[self.db_table].folder == args.folder).select().last()

            if r:
              v = r['version'] 
              cv = re.findall("\d\.\d\.(\d)", v)[0]
              nv = int(cv) + 1
              args.version = re.sub('\d$', str(nv), v)
              

          self.db[self.db_table].insert(uid=args.id, time=time.time(), folder=args.folder, size=self.size, local=args.local,name=args.name, version=args.version)
          self.db.commit()
        
        
          is_success = True
          
          if check_arg(args,"local"):

            lback_output("Transaction ID: " + args.id)
            lback_output("Backup Ok -- Now saving to disk")
            lback_output("Local Backup has been successfully stored")
            lback_output("Transaction ID: " + args.id)
          else:
            fc = open(bkp.get(), 'r').read()
            client.run(cmd='BACKUP', folder=args.folder, uid=args.id, contents=fc, name=args.name,version=args.version,size=self.size)
            if client.status:
              lback_output("Backup Ok -- Now transferring to server")
              
              fp = client.get()
              if len(re.findall("SUCCESS", fp)) > 0:
                lback_output("Remote Backup has been successfully transferred")
                lback_output("Transaction ID: " + args.id)
                os.remove(bkp.get())
              else:
                lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes", type="ERROR")
            else:
              pass
        else:
          pass
        
    if check_arg(args, "restore"):

      if args.id:
	id = check_for_id( args.id, self.db)

 	record = self.db.restores.insert(
		backupId=id,
		uid=args.rid,
		time=time.time() ) 

	meta = RestoreMeta(id=args.rid)

	if not check_arg(args,"version"):
	  r = self.db((self.db[self.db_table].uid == id)  | \
		      (self.db[self.db_table].name == id) | \
		(self.db[self.db_table].folder == id)).select().last()

  
	else:

	  if args.version == "latest":
	    r = self.db((self.db[self.db_table].uid == id)  | \
		      (self.db[self.db_table].name == id) | \
		(self.db[self.db_table].folder == id)).select().last()


	  elif args.version.lower() == "oldest":
	    r = self.db((self.db[self.db_table].uid == id)  | \
		      (self.db[self.db_table].name == id) | \
		(self.db[self.db_table].folder == id)).select().first()

	  else:
	    r = self.db(((self.db[self.db_table].uid == id)  | \
		   (self.db[self.db_table].name == id) | \
		   (self.db[self.db_table].folder == id)) \
		 & (self.db[self.db_table].version == args.version)).select().first()

	
	if not r:
	  lback_output("Backup not found.", type="ERROR")
	  return
	  
	args.folder = r['folder']
	args.local = r['local']
	args.clean= check_arg(args,"clean")
	ruid = r['uid']
	archive_loc = backupDir+ruid+ext
	  


	## restore an s3 instance
	#if s3 in dir(self) and self.s3:
	#  pass

        okargs = dict(
		status=EventStatuses.STATUS_STOPPED,
		message=EventMessages.MSG_RESTORE_FINISHED,
		obj=EventObjects.OBJECT_RESTORE,
		data=meta.serialize() )
	errargs = dict(
		status=EventStatuses.STATUS_ERR,
		message=EventMessages.MSG_RESTORE_STOPPED,
		obj=EventObjects.OBJECT_RESTORE,
		data=meta.serialize() )
	
	if check_arg(args,"clean"):
	  lback_output("Cleaning directory..")
	 
	  if not os.path.isdir(args.folder):
	    os.makedirs(args.folder)
	  
	if args.local:
	  lback_output("Restore Ok -- Now restoring compartment")
	   
	  rst = Restore(archive_loc, folder=args.folder, clean=args.clean, state=rstate)
	  rst.run(local=True, uid=ruid, rid=record.uid)  
	  
	  if rst.status:
	    lback_output("Restore has been successfully performed")
 	  else:
	    lback_output("Backup was unsuccessfull", type="ERROR")
		
	else:
	  lback_output("Pinging server for restore..")
	  client.run(cmd='RESTORE', folder=args.folder, uid=ruid, version=args.version)
	  lback_output("Forming archive.. this can take some time")
	  if client.status:
	    lback_output("Restore Retrieval Ok -- now attempting to restore")
	    fp = open(backupDir + ruid + ext, 'w+')
	    fp.write(client.get().decode("utf-8").decode("hex"))
	    fp.close()
	   
	      
	    rst = Restore(archive_loc, folder=args.folder,clean=args.clean,state=rstate)
	    rst.run(local=False, uid=ruid, rid=record.uid)
	    
	    if rst.status:
	      lback_output("Restore Successful")
	    else:
	      lback_output("Backup was unsuccessfull", type="ERROR")


      else:
	  lback_output("Please provide an ID")

    if check_arg(args, "jit"):
      if args.id:
	id = check_for_id(args.id,self.db)
        jit = JIT(self.db, self.db_table).check(id)
      else:
        lback_output("Starting a JIT instance on this backup")
        os.system("lback-jit --id '{0}' > /dev/null 2>&1".format(args.id))


    ## important to check for success
    ## on this command
    
    if check_arg(args,"remove") and is_success:
      if args.folder:
        shutil.rmtree(args.folder)
        lback_output("Directory successfully deleted..")
    if check_arg(args, "delete"):
      client = Client(self.port, args.host, dict(ip=args.host,port=self.port))
      if args.id:
	id = check_for_id(args.id,self.db)
        row =self.db(self.db[self.db_table].uid == id).select().first()
        
        if row:
          lback_output("Removing backup: " + row.name)
     
          if not row.local: 
            client.run("DELETE",  uid=row.uid)
            lback_output(client.m)
          else:
            os.remove(backupDir + row.uid+ext)
            if not os.path.isfile(backupDir +  row.uid + ext):
              lback_output("Removed backup successfully")
            else:
              lback_output("Could not delete backup device or resource busy", type="ERROR")

          self.db(self.db[self.db_table].uid == id).delete()
        else:
          row = self.db(self.db[self.db_table].folder == args.folder).select()
          if len(row) > 0:
            lback_output("There are multiple backups with: " + args.folder)
            counter = 1
            counterOfBackups= dict()
            for i in row:
              lback_output("Press " +counter +  " to delete: " )
              lback_output(i.as_dict())
              counterOfBackups[counter] =i.uid
              counter += 1
            numberSelected = ""
            while numberSelected != "QUIT":
              numberSelected = raw_input()
              if numberSelected >0  and numberSelected < len(counterOfBackups):
                thisBackup =counterOfBackups[numberSelected]
                theBackup = self.db(self.db[self.db_table].uid == thisBackup).select().first()
                lback_output("removing: " + theBackup.name)
                if not theBackup.local:
                  client.run("DELETE",uid=theBackup.uid) 
                  lback_output(client.m)
                else:
      
                  os.remove(backupDir +theBackup.uid + ext)
                  if not os.path.isfile(backupDir +   theBackup.uid + ext):
                    lback_output("Removed the backup successfully")
                  else:
                    lback_output("Could not delete the backup device or resource is busy", type="ERROR")
    
                self.db(self.db[self.db_table].uid == thisBackup).delete()
                lback_output("removed this backup successfully")
              else:
                lback_output("not a valid number please press one of: " + ",".join(counterOfBackups.keys()))
              lback_output("Press QUIT to exit or another number to delete more")

          elif len(row) == 1:
            row = row.first()   
            if not row.local:
              client.run("DELETE",uid=row.uid)
            else:
              os.remove(backupDir + row.uid + ext)
              if not os.path.isfile(backupDir +  row.uid + ext):
                lback_output("Backup removed successfully" )
              else:
                lback_output("Could not remove the backup" , type="ERROR")
            
            self.db(self.db[self.db_table].folder == args.folder).delete()
            lback_output("removed this backup successfully ")
          else: 
            lback_output("Could not find this backup")
      
    if check_arg(args,"listall"):
      rows = self.db(self.db[self.db_table].time > 0).select().as_list()
      lback_output("Full list of stored backups")
      for i in rows:
        lback_output("Backup", i)
    if check_arg(args, "listusers"):
      rows = self.db( self.db[self.db_user_table].id > 0 ).select().as_list()
      lback_output("Full list of users")
      for i in rows:
	 lback_output( "User", i )
    if check_arg(args, "listbackups"):
	    backups = lback_backups(page=args.page, amount=args.amount)
	    result =  backups.as_list()
	    return {"message": RPCMessages.LISTED_BACKUPS, "data": result, "error": False }
    if  check_arg(args, "listrestores"):
	 restores = lback_restores(args.page, amount=args.amount)
	 result = restores.as_list()
	 return {"message": RPCMessages.LISTED_RESTORES, "data": result, "error": False }
    elif check_arg(args, "getbackup"):
	    backup = lback_backup( id=args.id )
	    result = backup.as_dict()
	    return {"message": RPCMessages.LISTED_BACKUP, "data": result, "error": False }
    elif check_arg(args, "delbackup"):
	  backup = lback_backup(id=args.id)
	  try:
		backup.delete()
		return {"message": RPCMessages.DELETED_BACKUP,  "error": False }
	  except Exception,ex:
		return {"message": RPCMessages.DELETE_BACKUP_ERROR, "error": true }
   
    elif check_arg(args, "getrestore"): ##
	  restore = lback_restore( id=args.rid )
	  result =restore.as_dict()
	  return {"message": RPCMessages.LISTED_RESTORe, "data": result, "error": False }
    elif check_arg(args, "delrestore"):
	  restore = lback_restore( id = args.rid )
	  try:
		restore.delete()
		return {"message": RPCMessages.DELETED_RESTORE, "error": False }
	  except Exception,ex:
		return {"messages": RPCMessages.DELETE_RESTORE_ERROR, "error": True }
	 

    if check_arg(args, "adduser"):
       currentUser = self.db( self.db[self.db_user_table].username == args.username ).select().first()
       if currentUser:
	 return  {
			"error": True,
			"message":RPCMessages.EXISTS_USER
			}
       else:
	  try:
		  newRecord = self.db[self.db_user_table].insert(
				username=args.username,
				password=args.password)
	          self.db.commit()
	 	  return {
				"error": False,
				"data": newRecord.as_dict(),
				"message": RPCMessages.CREATED_USER
			}
	  except Exception, ex:
		  return {
				"error": True,
				"data": [],
				"message": RPCMessages.CREATE_USER_ERROR
			}
    if  check_arg(args, "deluser"):
	  try:
		 self.db(self.db[self.db_user_table].username==args.username).delete()
		 self.db.commit()
		 return {
				"error": False,
				"message": RPCMessages.USER_DELETED
			}

  	  except Exception, ex:
		 return {
					"message": RPCMessages.DELETE_USER_ERROR,
					"error": True
			}
    if check_arg(args, "getuser"):
	 user = lback_user(id=args.id)
	 result = user.as_dict()
	 return {"message": RPCMessages.LISTED_USER,"data":user}
    elif check_arg(args,"listusers"):
	 users = lback_users(page=args.page,amount=args.amount)
	 result = users.as_list()
	 return {"message": RPCMessages.LISTED_USERS, "data": result}
         
	
  
  def _help(self):
    lback_output("""
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
    """, tag=False)
  
 
  def try_hard_to_find(self):
    pass
    
  def _settings_v1(self):
    if os.path.isfile("/usr/local/lback/settings.json"):
      settings = json.loads(open("/usr/local/lback/settings.json").read())
    elif os.path.isfile("../settings.json"):
      settings = json.loads(open("../settings.json").read())
    self._settings_gen(settings)
  def _settings_v2(self):
    path = "{}/.lback/settings.json".format(getenv("HOME")) 
    self._settings_gen(json.loads(open(path).read()))
  def _settings(self):
    self._settings_v2()

  def _settings_gen(self, settings):
    for i in settings.keys():
      setattr(self, i, settings[i])
      
    self.ip = settings['client_ip']
    self.port = settings['client_port']
    self.server_ip = settings['server_ip']
    self.server_port = settings['server_port']
    
    self.db_family = 'sqlite'
        
  def _profiles(self):
    if os.path.isfile("/usr/local/lback/profiles.json"):
      self.profiles = json.loads(open("/usr/local/lback/profiles.json").read())
    elif os.path.isfile("../profiles.json"):
      self.profiles = json.loads(open("../profiles.json").read()) 
  @staticmethod
  def get_db( self ):
     db = DAL('sqlite://db.sql', folder='/usr/local/lback/')
     return db

 
