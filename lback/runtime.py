
from lback.utils import lback_untitled, lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_error, lback_print, lback_id, get_folder_size
from lback.restore import Restore, RestoreException
from lback.backup import Backup, BackupException
from lback.client import Client
from lback.server import Server
from os import getenv
from pydal import Field
import glob
import shutil
import argparse
import time
import os
import json


class Runtime(object):
  def __init__(self, args):
    untitled = lback_untitled()
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers()
   
     
    backup_parser = sub_parser.add_parser("backup", 
		help="Backup files and folders",
		)

    backup_parser.add_argument("folder", 
		help="Select a folder",
		nargs="*"
	)
    backup_parser.add_argument("--name", help="Name for backup", default=untitled)
    backup_parser.add_argument("--remove", action="store_true",
		help="Remove backup when done",
	default=False)
    backup_parser.add_argument("--local",default=True, action="store_true")
    backup_parser.set_defaults(backup=True)
    restore_parser = sub_parser.add_parser("restore", 
		help="Run a restore",
	)
    restore_parser.add_argument("id",
		help="Select the ID",
		nargs="*"
	)
    restore_parser.add_argument("--name",
		help="Filter to a specific name",
		default=False
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
    rm_parser.add_argument("--name",
		help="Filter to a specific name",
		default=False
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
    mv_parser.set_defaults(name=False)
    self.args = parser.parse_args()
    

  def run(self):
    args = self.args
    backup_dir = lback_backup_dir()
    ext = lback_backup_ext()
    db = lback_db()

    def get_all_globs(folders_or_ids):
	full_list = []
	for folder in folders_or_ids:
	   glob_entries = glob.glob( folder )
	   if len( glob_entries ) > 0:
		full_list = full_list + glob_entries
	   else:
	   	full_list.append( folder )
        return full_list
	 


    ## Either short ID (7 chars) OR long ID (40) chars OR folder
    def check_for_row(id, return_all_matches=False):
       ## folder and name
       if args.name:
		rows = db(db.backups.name == args.name)
	        if not rows.count()>0:
			raise Exception("Backup with name not found")
       else:
	        rows = db((db.backups.lback_id.like(id+"%") | \
		      (db.backups.name == id) ))
	        if not rows.count()>0:
		    try_folder = os.path.abspath( id )
		    rows = db(db.backups.folder == try_folder)
       		if not rows.count()>0:
  	  	    raise Exception("Backup with Folder/ID not found")
       if return_all_matches:
	   return rows
       return rows.select().last()
    def check_parser(name):
      if  name in dir( args ) and getattr( args, name ):
        return True
      return False

    def do_backup( rel_folder ): 
	try:
	  id =lback_id()
	  folder = os.path.abspath( rel_folder )
	  dirname = os.path.dirname( folder )
          bkp = Backup(id, folder)
       	  bkp.run()
	  size = get_folder_size(folder)
          db.backups.insert(lback_id=id,
		 time=time.time(), 
		 folder=folder,
		 dirname=dirname,
		 size=size, local=args.local,name=args.name)
          db.commit()
          lback_output("Backup OK. Now saving to disk")
          lback_output("Local Backup has been successfully stored")
          lback_output("Transaction ID: " + id)
	  if args.remove:
	    shutil.rmtree(folder)
	    lback_output("Directory successfully deleted..")
	except BackupException, ex:
	  lback_error(ex)	
 	except Exception, ex:
	  lback_error(ex)	
    def do_restore( short_or_long_id ):
	try:
	  row = check_for_row( short_or_long_id )
	  if args.clean \
	  and os.path.isdir(row.folder):
	    lback_output("Cleaning directory..")
	    shutil.rmtree(row.folder)
	        
	  lback_output("Backup Found. Now restoring compartment")
	  rst = Restore(row.lback_id,folder=row.folder)
	  rst.run(local=True)
	  lback_output("Restore has been successfully performed")
	except RestoreException, ex:
	  lback_error(ex)	
	except Exception, ex:
	  lback_error(ex)	
    def do_rm(short_or_long_id):
	try:
	  rows = check_for_row(short_or_long_id, return_all_matches=True)
	  folder = rows.select(db.backups.folder).first().folder
	  for backup in rows.select(db.backups.lback_id):
  	     os.remove(backup_dir + backup.lback_id +ext)
	  rows.delete()
	  db.commit()
	except Exception,ex:
	  lback_error(ex)	
    def do_ls():
      try:
        current_dir = os.getcwd()
	rows = db(db.backups.dirname==current_dir)
	lback_print("total %d"%(rows.count()), "white")
        for backup in rows.select():
	    splitted = backup.folder.split("/")
	    filename = splitted[ len( splitted ) - 1 ]
	    lback_print("%s\t%s"%(filename, backup.lback_id), "white")
      except Exception, ex:
	  lback_error(ex)	
    def do_mv(short_or_long_id):
	try:
	  row = check_for_row( short_or_long_id )
  	  folder = os.path.abspath( args.dst )
	  dirname = os.path.dirname( folder )
	
	  row = db( db.backups.lback_id == row.lback_id )
	  backup = row.select(db.backups.lback_id, db.backups.folder).first()
          archive = backup_dir + backup.lback_id + ext
	  row.update( 
		folder=folder,
		dirname=dirname )
	  db.commit()
	  lback_output("Moved compartment successfully")
	except Exception,ex:
	  lback_error(ex)	

    if check_parser("backup"):
	 map(do_backup, get_all_globs(args.folder))

    if check_parser("restore"):
	 ids = args.id
	 map(do_restore, get_all_globs(args.id))
    if check_parser("rm"):
	 ids = args.id
	 map(do_rm, get_all_globs(args.id))
            
    if check_parser("ls"):
	 do_ls()
    if check_parser("mv"):
	 do_mv(args.id)
