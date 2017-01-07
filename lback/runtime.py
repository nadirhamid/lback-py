
from lback.utils import lback_untitled, lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_error, lback_print, lback_id, get_folder_size
from lback.restore import Restore, RestoreException
from lback.backup import Backup, BackupException
from lback.client import Client
from lback.server import Server
from os import getenv
import glob
import shutil
import argparse
import time
import os
import json
import fnmatch


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
    cursor = db.cursor()

    def get_backup_filename( backup ):
            splitted = backup.folder.split("/")
	    filename = splitted[ len( splitted ) - 1 ]
	    return  filename

    def get_all_globs(folders_or_ids, as_restore=False):
	full_list = []
	for folder in folders_or_ids:
	   if as_restore:
		## fnmatch is used by glob under the hood
		## we need to make sure
		## even non existant files get detected
	 	current_dir = os.getcwd()
	 	glob_entries = []
		select_cursor = db.cursor().execute("SELECT * FROM  backups WHERE dirname = ?", (current_dir,))
	  	backup = select_cursor.fetchone()
		while backup:
		    if fnmatch.fnmatch(get_backup_filename( backup ), folder):
		  	glob_entries = glob_entries + [backup.folder]
		    backup = select_cursor.fetchone()
	   else:
	   	glob_entries = glob.glob( folder )
	   if len( glob_entries ) > 0:
		full_list = full_list + glob_entries
	   else:
		full_list.append( folder )
        return full_list
	 


    ## Either short ID (7 chars) OR long ID (40) chars OR folder
    def check_for_row(id):
       ## folder and name
       if args.name:
		select_cursor = db.cursor().execute("SELECT * FROM backups WHERE name = ?", (args.name,))
		row = select_cursor.fetchone()
	        if not row:
			raise Exception("Backup with name not found")
       else:
		select_cursor = db.cursor().execute("SELECT * FROM backups WHERE lback_id LIKE ?",("%"+id+"%",))
		row =select_cursor.fetchone()
	        if not row:
		   select_cursor = db.cursor().execute("SELECT * FROM backups WHERE folder = ?", (id,))
		 
		row =select_cursor.fetchone()
       		if not row:
  	  	    raise Exception("Backup with Folder/ID not found")
       return row
    def check_parser(name):
      if  name in dir( args ) and getattr( args, name ):
        return True
      return False

    def do_backup( rel_folder ): 
	try:
	  folder = os.path.abspath( rel_folder )
	  id =lback_id(folder)
	  dirname = os.path.dirname( folder )
          bkp = Backup(id, folder)
       	  bkp.run()
	  size = get_folder_size(folder)
	  insert_cursor = db.cursor().execute("INSERT INTO backups (lback_id, time, folder, dirname, size, name) VALUES (?, ?, ?, ?, ?, ?)", 
			(id, time.time(), folder, dirname, size, args.name,))


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
	  row = check_for_row(short_or_long_id)
	  archive_loc = backup_dir + row.lback_id +ext
	  lback_output("Removing %s" % (archive_loc))
	  folder = row.folder
  	  os.remove(backup_dir + row.lback_id +ext)
	  delete_cursor =db.cursor().execute("DELETE FROM backups WHERE lback_id = ?", ( row.lback_id, ) )
	except Exception,ex:
	  lback_error(ex)	
    def do_ls():
      try:
        current_dir = os.getcwd()
	select_cursor = db.cursor().execute("SELECT * FROM backups WHERE dirname = ?",( current_dir, ))
        backup = select_cursor.fetchone()
	while backup:
	    filename = get_backup_filename( backup )
	    lback_print("%s\t%s"%(filename, backup.lback_id), "white")
	    backup = select_cursor.fetchone()
      except Exception, ex:
	  lback_error(ex)	
    def do_mv(short_or_long_id):
	try:
	  row = check_for_row( short_or_long_id )
  	  folder = os.path.abspath( args.dst )
	  dirname = os.path.dirname( folder )
          archive = backup_dir + row.lback_id + ext
	  update_cursor = db.cursor().execute("UPDATE backups SET folder = ?, dirname = ? WHERE lback_id = ?",
			(folder, dirname, row.lback_id))
	  lback_output("Moved compartment successfully")
	except Exception,ex:
	  lback_error(ex)	

    if check_parser("backup"):
	 map(do_backup, get_all_globs(args.folder))

    if check_parser("restore"):
	 ids = args.id
	 map(do_restore, get_all_globs(args.id, True))
    if check_parser("rm"):
	 ids = args.id
	 map(do_rm, get_all_globs(args.id, True))
            
    if check_parser("ls"):
	 do_ls()
    if check_parser("mv"):
	 do_mv(args.id)
    db.commit()
    db.close()

