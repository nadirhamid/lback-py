
from lback.record import Record
from lback.utils import lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_uuid,lback_backups,  lback_backup, lback_restores, lback_restore,check_for_id, Util
from lback.profiler import Profiler
from lback.restore import Restore, RestoreException
from lback.backup import Backup, BackupException
from lback.client import Client
from lback.server import Server
from os import getenv
from pydal import Field

import shutil
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
  def __init__(self, args):
    self._settings()
    self.args = args

  def init(self):
    parser = argparse.ArgumentParser()
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
    parser.add_argument("--version", default=False,
		help="Select a version tag"
		)
    parser.add_argument("--local",default=True, action="store_true")
    parser.add_argument("--encrypt", action="store_true",
		help="Make an encrypted backup"	
	)
    parsed = parser.parse_args()
 
    parsed.type ='CLIENT'
    if parsed.server:
	parsed.type == 'SERVER'
    self.args = parsed
    self.perform()
    
  def perform(self):
    args = self.args
    is_success = False
    backupDir = lback_backup_dir()
    ext = lback_backup_ext()
    if check_arg(args, "folder" ):
      self.size = str(Util().getFolderSize(args.folder))
    
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
        return lback_output("You must provide argument folder", type="ERROR")
      else:
        lback_output("Gathering files.. this can take awhile")
        bkp = Backup(args.id, args.folder)
	try:
       	  bkp.run()
       
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
            lback_output("Backup OK. Now saving to disk")
            lback_output("Local Backup has been successfully stored")
            lback_output("Transaction ID: " + args.id)
          else:
            fc = open(bkp.get(), 'r').read()
            client.run(cmd='BACKUP', folder=args.folder, uid=args.id, contents=fc, name=args.name,version=args.version,size=self.size)
            if client.status:
              lback_output("Backup OK. Now transferring to server")
              
              fp = client.get()
              if len(re.findall("SUCCESS", fp)) > 0:
                lback_output("Remote Backup has been successfully transferred")
                lback_output("Transaction ID: " + args.id)
                os.remove(bkp.get())
              else:
                return lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes", type="ERROR")
            else:
                return lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes", type="ERROR")
	except BackupException, ex:
	  return lback_output( repr( ex ), type="ERROR" )
 	except Exception, ex:
	  return lback_output( repr( ex ), type="ERROR" )
    if check_arg(args, "restore"):

      if args.id:
	id = check_for_id( args.id, self.db)
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
	  return lback_output("Backup not found.", type="ERROR")
	args.folder = r['folder']
	args.local = r['local']
	args.clean= check_arg(args,"clean")
	ruid = r['uid']
	archive_loc = backupDir+ruid+ext
	  
	if check_arg(args,"clean"):
	  lback_output("Cleaning directory..")
	 
	  if not os.path.isdir(args.folder):
	    os.makedirs(args.folder)
	  
	if args.local:
	  lback_output("Restore OK. Now restoring compartment")
	   
	  rst = Restore(id, archive_loc, folder=args.folder, clean=args.clean)
	  try:
	    rst.run(local=True)
	    lback_output("Restore has been successfully performed")
	  except RestoreException, ex:
	    return lback_output( repr(ex), type="ERROR" )
	  except Exception, ex:
	    return lback_output( repr(ex), type="ERROR" )
	else:
	  lback_output("Pinging server for restore..")
	  client.run(cmd='RESTORE', folder=args.folder, uid=ruid, version=args.version)
	  lback_output("Forming archive.. this can take some time")
	  if client.status:
	    lback_output("Restore Retrieval OK. Now attempting to restore")
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

  def _settings(self):
    path = "{}/.lback/settings.json".format(getenv("HOME")) 
    self._settings_gen(json.loads(open(path).read()))

  def _settings_gen(self, settings):
    for i in settings.keys():
      setattr(self, i, settings[i])
      
    self.ip = settings['client_ip']
    self.port = settings['client_port']
    self.server_ip = settings['server_ip']
    self.server_port = settings['server_port']
    self.db_family = 'sqlite'
