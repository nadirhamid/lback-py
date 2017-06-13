
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
        id =lback_id()
        folder =os.path.abspath( rel_folder )

        bkp = Backup(id, folder)
        backup_res = self.client._run(self, bkp)
        lback_output("Backup OK. Now saving to disk")
        lback_output("Local Backup has been successfully stored")
        lback_output("Transaction ID: " + id)
      except Exception, ex:
        lback_error(ex)	
