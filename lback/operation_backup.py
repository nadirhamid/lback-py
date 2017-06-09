
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
        folder = os.path.abspath( rel_folder )
        id =lback_id(salt=folder)
        dirname = os.path.dirname( folder )
        bkp = Backup(id, folder, diff=args.diff, encryption_key=args.encryption_key)
        bkp_type = [ "" ]


        def complete_backup():
            size = get_folder_size(folder)
            insert_cursor = db.cursor().execute("INSERT INTO backups (id, time, folder, dirname, size, backup_type, name, encryption_key, distribution_strategy) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", 
              (id, time.time(), folder, dirname, size, bkp_type[ 0 ], args.name, args.encryption_key, args.distribution_strategy, ))
            db.commit()

            lback_output("Backup OK. Now saving to disk")
            lback_output("Local Backup has been successfully stored")
            lback_output("Transaction ID: " + id)
            backup =lback_backup( id )
            self.client._run(self, backup)

        def new_backup():
            lback_output("RUNNING FULL BACKUP")
            bkp_type[ 0 ] = "full"
            bkp.run()
            complete_backup()
            if args.remove:
              shutil.rmtree(folder)
              lback_output("Directory successfully deleted..")

        def diff_backup():
             lback_output("RUNNING DIFFERENTIAL BACKUP")
             bkp_type[ 0 ] = "diff"
             bkp_object = BackupObject.find_by_id( args.diff )
             if not bkp_object:
                lback_error("No such backup exists..")
             restore_path = lback_temp_path()
             os.makedirs(restore_path)
             restore_args = OperationArgs(
                id=[args.diff], 
                folder=restore_path,
                name=False,
                clean=False)
             restore_op = OperationRestore(restore_args,self.client,db)
             restore_op.run()
             bkp.run_diff( restore_path )
             complete_backup()
             ##shutil.rmtree(restore_path)
             lback_output("Restore snapshot removed successfully")
        if args.diff:
            diff_backup()
        else:
            new_backup()
      except BackupException, ex:
        lback_error(ex)	
      except Exception, ex:
        lback_error(ex)	
