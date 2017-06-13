
from .operation import Operation
from .operation_restore import OperationRestore
from .operation_args import OperationArgs
from .parser_distribution_strategy import ParserDistributionStrategy
from .utils import lback_output, lback_id, lback_error, lback_temp_path, lback_backup, get_folder_size
from .backup import Backup, BackupException, BackupObject
import glob
import shutil
import os
import time

class OperationBackup(Operation):
    PARSERS = [
        ParserDistributionStrategy
    ]
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
        folder = os.path.abspath(rel_folder)
        id =lback_id(salt=folder)
        dirname = os.path.dirname( folder )

        bkp = Backup(id, folder, diff=args.diff, encryption_key=args.encryption_key)
        def complete_backup():
            size = backup_res.backup_size
            bkp_type = "full"
            if args.diff:
                bkp_type = "diff"
            insert_cursor = db.cursor().execute("INSERT INTO backups (id, time, folder, dirname, size, backup_type, name, encryption_key, distribution_strategy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
              (id, time.time(), folder, dirname, size, bkp_type, args.name, args.encryption_key, args.distribution_strategy, ))
            db.commit()

            lback_output("Backup OK. Now saving to disk")
            lback_output("Local Backup has been successfully stored")
            lback_output("Transaction ID: " + id)
            backup =lback_backup( id )
        backup_res = self.client._run(self, bkp)
        complete_backup()
      except Exception, ex:
        lback_error(ex)	
