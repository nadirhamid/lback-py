
from .operation import Operation
from .utils import lback_output, lback_id, lback_error, lback_backup, get_folder_size
from .backup import Backup, BackupException
import glob
import shutil
import os
import time

class OperationBackup(Operation):
    def _get_all_globs(self):
      folders_or_ids = self.args.folder
      db = self.db
      full_list = []
      for folder in folders_or_ids:
         glob_entries = glob.glob( folder )
         if len( glob_entries ) > 0:
           full_list = full_list + glob_entries
         else:
           full_list.append( folder )
      return full_list

    
    def _run( self, rel_folder ):   
      try:
        db = self.db
        args = self.args
        folder = os.path.abspath( rel_folder )
        id =lback_id(folder)
        dirname = os.path.dirname( folder )
        bkp = Backup(id, folder)
        bkp.run()
        size = get_folder_size(folder)
        insert_cursor = db.cursor().execute("INSERT INTO backups (id, time, folder, dirname, size, name) VALUES (%s, %s, %s, %s, %s, %s)", 
          (id, time.time(), folder, dirname, size, args.name,))
        db.commit()

        lback_output("Backup OK. Now saving to disk")
        lback_output("Local Backup has been successfully stored")
        lback_output("Transaction ID: " + id)
        if args.remove:
          shutil.rmtree(folder)
          lback_output("Directory successfully deleted..")
	backup_obj = lback_backup( id )
  	self.client._run( self, backup_obj )
      except BackupException, ex:
        lback_error(ex)	
      except Exception, ex:
        lback_error(ex)	
