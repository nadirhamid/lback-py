
from lback.record import Record
from lback.utils import lback_backup_dir, lback_backup_ext, lback_db, lback_output,lback_print, lback_id,lback_backups,  lback_backup, lback_restores, lback_restore,Util
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
     self.id= lback_id()
     for i in kwargs.keys():
	  setattr( self,  i, kwargs[i] )

class Runtime(object):
  def __init__(self, args):
    self._settings()
    self.args = args
    self.parser = argparse.ArgumentParser()
    self.db = lback_db()
    self.db_host= ''
    self.db_table ='backups'

  def init(self):
    parser = self.parser
    sub_parser = parser.add_subparsers()
     
    backup_parser = sub_parser.add_parser("backup", 
		help="Backup files and folders",
		)

    backup_parser.add_argument("folder", 
		help="Select a folder",
		nargs="*"
	)
    backup_parser.add_argument("--version", default=False,
		help="Select a version tag",
		)

    backup_parser.add_argument("--name", help="Name for backup", default="Untitled Backup")
    backup_parser.add_argument("--remove", action="store_true",
		help="Remove backup when done",
	default=False)
    backup_parser.add_argument("--local",default=True, action="store_true")
    backup_parser.add_argument("--encrypt", action="store_true",
		help="Make an encrypted backup"	
	)



    backup_parser.set_defaults(backup=True)
    restore_parser = sub_parser.add_parser("restore", 
		help="Run a restore",
	)
    restore_parser.add_argument("id",
		help="Select the ID",
		nargs="*"
	)
    restore_parser.add_argument("--clean", action="store_true",
		help="Clean backup on completion",
		default=False
	)



    restore_parser.set_defaults(restore=True)
    rm_parser = sub_parser.add_parser("rm", 
		help="Delete existing backup",
		)
    rm_parser.add_argument("id",
		help="Select the ID",
		nargs="*"
	)


    rm_parser.set_defaults(rm=True)
    ls_parser = sub_parser.add_parser("ls", 
		help="List backups",
		)

    ls_parser.set_defaults(ls=True)


    mv_parser = sub_parser.add_parser("mv", 
		help="Move mounted backup"
		)
    mv_parser.add_argument("id",
		help="Select the ID",
	)
    mv_parser.add_argument("dst",
		help="Select the Destination",
	)
    mv_parser.set_defaults(mv=True)

    parsed = parser.parse_args()
    self.args = parsed
    self.perform()
    
  def perform(self):
    args = self.args
    backup_dir = lback_backup_dir()
    ext = lback_backup_ext()
    db_table = self.db_table 
    host =""
    port =""
    db = self.db
    def get_an_id () :
	 return  Record().generate()
    ## Either short ID (7 chars) OR long ID (40) chars OR folder
    def check_for_id(id):
       row = db((db[db_table].lback_id.like(id+"%") | \
		      (db[db_table].name == id) )).select().last()

       if not row:
          try_folder = os.path.abspath( id )
          row = db(db[db_table].folder == try_folder).select().last()
       if not row:
         row = db((db[db_table].lback_id.like(id+"%") | \
		      (db[db_table].name == id) )).select().last()
       if not row:
          raise Exception("Please provide a short hash (7 characters) or long (40 characters) or folder")
       if not row:
          raise Exception("Error record was not found")
       return row.lback_id

    def do_backup( rel_folder ): 
        lback_output("Gathering files.. this can take awhile")
	id = get_an_id()
	folder = os.path.abspath( rel_folder )
        bkp = Backup(id, folder)
	try:
       	  bkp.run()
	  size = Util().get_folder_size(folder)
          db[db_table].insert(lback_id=id, time=time.time(), folder=folder, size=size, local=args.local,name=args.name, version=args.version)
          db.commit()
	  if check_arg(args,"local"):
            lback_output("Backup OK. Now saving to disk")
            lback_output("Local Backup has been successfully stored")
            lback_output("Transaction ID: " + id)
          else:
            fc = open(bkp.get(), 'r').read()
            client.run(cmd='BACKUP', folder=folder, id=id, contents=fc, name=args.name,version=args.version,size=size)
            if client.status:
              lback_output("Backup OK. Now transferring to server")
              
              fp = client.get()
              if len(re.findall("SUCCESS", fp)) > 0:
                lback_output("Remote Backup has been successfully transferred")
                lback_output("Transaction ID: " + id)
                os.remove(bkp.get())
              else:
                return lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes", type="ERROR")
            else:
                return lback_output("Something went wrong on the server.. couldnt back that folder. Reverting changes", type="ERROR")

	  if check_arg(args,"remove"):
	    shutil.rmtree(folder)
	    lback_output("Directory successfully deleted..")
	except BackupException, ex:
	  return lback_output( repr( ex ), type="ERROR" )
 	except Exception, ex:
	  return lback_output( repr( ex ), type="ERROR" )
    def do_restore( short_or_long_id ):
	id = check_for_id( short_or_long_id )
	if not check_arg(args,"version"):
	  row = db((db[db_table].lback_id == id)  | \
		      (db[db_table].name == id) | \
		(db[db_table].folder == id)).select().last()
	else:

	  if args.version == "latest":
	    row = db((db[db_table].lback_id == id)  | \
		      (db[db_table].name == id) | \
		(db[db_table].folder == id)).select().last()
	  elif args.version.lower() == "oldest":
	    row = db((db[db_table].lback_id == id)  | \
		      (db[db_table].name == id) | \
		(db[db_table].folder == id)).select().first()
	  else:
	    row = db(((db[db_table].lback_id == id)  | \
		   (db[db_table].name == id) | \
		   (db[db_table].folder == id)) \
		 & (db[db_table].version == args.version)).select().first()
	if not row:
	  return lback_output("Backup not found.", type="ERROR")
	archive_loc = backup_dir+row.lback_id+ext
	  
	if check_arg(args,"clean"):
	  lback_output("Cleaning directory..")
	 
	  if not os.path.isdir(row.folder):
	    os.makedirs(row.folder)
	  
	if row.local:
	  lback_output("Restore OK. Now restoring compartment")
	   
	  rst = Restore(row.lback_id, archive_loc, folder=row.folder, clean=args.clean)
	  try:
	    rst.run(local=True)
	    lback_output("Restore has been successfully performed")
	  except RestoreException, ex:
	    return lback_output( repr(ex), type="ERROR" )
	  except Exception, ex:
	    return lback_output( repr(ex), type="ERROR" )
	else:
	  lback_output("Pinging server for restore..")
	  client.run(cmd='RESTORE', folder=row.folder, id=row.lback_id, version=args.version)
	  lback_output("Forming archive.. this can take some time")
	  if client.status:
	    lback_output("Restore Retrieval OK. Now attempting to restore")
	    fp = open(backup_dir + rid + ext, 'w+')
	    fp.write(client.get().decode("utf-8").decode("hex"))
	    fp.close()
	      
	    rst = Restore(row.lback_id, archive_loc, folder=row.folder, clean=args.clean)
	    rst.run(local=False)
	    
	    if rst.status:
	      lback_output("Restore Successful")
	    else:
	      lback_output("Backup was unsuccessfull", type="ERROR")
    def do_rm(short_or_long_id):
        client = Client(port, host, dict(ip=host,port=port))
	id = check_for_id(short_or_long_id)
	row =db(db[db_table].lback_id == id)

	if row:
	  backup = row.select().first()
	  lback_id = backup.lback_id
	  name = backup.name
	  lback_output("Removing backup: " + name)
	  if not backup.local: 
	    client.run("DELETE",  id=lback_id)
	    lback_output(client.m)
	  else:
	    os.remove(backup_dir + lback_id+ext)
	    if not os.path.isfile(backup_dir +  lback_id + ext):
	      lback_output("Removed backup successfully")
	    else:
	      lback_output("Could not delete backup device or resource busy", type="ERROR")

	  row.delete()
	  db.commit()
	else:
	  row = db(db[db_table].folder == id).select()
	  if len(row) > 0:
	    lback_output("There are multiple backups with: " + id)
	    counter = 1
	    counter_of_backups= dict()
	    for i in row:
	      lback_output("Press " +counter +  " to delete: " )
	      lback_output(i.as_dict())
	      counter_of_backups[counter] =i.lback_id
	      counter += 1
	    number_selected = ""
	    while number_selected != "QUIT":
	      number_selected = raw_input()
	      if number_selected >0  and number_selected < len(counter_of_backups):
		id =counter_of_backups[number_selected]
		row = db(db[db_table].lback_id == id).select().first()
		lback_output("removing: " + row.name)
		if not row.local:
		  client.run("DELETE",id=row.id) 
		  lback_output(client.m)
		else:

		  os.remove(backup_dir +row.id + ext)
		  if not os.path.isfile(backup_dir +   row.id + ext):
		    lback_output("Removed the backup successfully")
		  else:
		    lback_output("Could not delete the backup device or resource is busy", type="ERROR")

		db( db[db_table].lback_id == id ).delete()
		db.commit()
		lback_output("removed this backup successfully")
	      else:
		lback_output("not a valid number please press one of: " + ",".join(counter_of_backups.keys()))
	      lback_output("Press QUIT to exit or another number to delete more")

	  elif len(row) == 1:
	    row = row.first()   
	    if not row.local:
	      client.run("DELETE",id=row.id)
	    else:
	      os.remove(backup_dir + row.id + ext)
	      if not os.path.isfile(backup_dir +  row.id + ext):
		lback_output("Backup removed successfully" )
	      else:
		lback_output("Could not remove the backup" , type="ERROR")
	    
	    db(db[db_table].folder == args.folder).delete()
	    db.commit()
	    lback_output("removed this backup successfully ")
	  else: 
	    lback_output("Could not find this backup")
    def do_ls():
      rows = db(db[db_table].time > 0).select()
      for backup in rows:
	  lback_print("\n", "white")
	  lback_print("id %s"%(backup.lback_id), "yellow")
	  lback_print("name: %s"%(backup.name), "white")
	  lback_print("version: %s"%(backup.version), "white")
	  lback_print("size: %s"%(backup.size), "white")
	  lback_print("folder: %s"%(backup.folder), "white")
	  lback_print("local: %s"%(backup.local), "white")
    def do_mv(short_or_long_id):
	id = check_for_id( short_or_long_id )
  	folder = os.path.abspath( args.dst )
	
	row = db( db[db_table].lback_id == id )
	backup = row.select().first()
        archive = backup_dir + backup.lback_id + ext
        Util().untar(archive, backup.folder)
	shutil.move( backup.folder, folder )
	row.update( 
		folder=folder )

	db.commit()
	lback_output("Moved compartment successfully")

    if check_arg(args, "backup" ):
	 folders = args.folder
	 map(do_backup, folders)

    if check_arg(args, "restore"):
	 ids = args.id
	 map(do_restore, ids)
    if check_arg(args, "rm"):
	 ids = args.id
	 map(do_rm, ids)
            
    if check_arg(args,"ls"):
	 do_ls()
    if check_arg(args,"mv"):
	 do_mv(args.id)


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
    db_family = 'sqlite'
