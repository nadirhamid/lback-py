
from .operation import Operation
from .utils import lback_output, lback_error, lback_id
from .restore import Restore, RestoreException
from .backup import BackupObject
import shutil
import os

class OperationRestore(Operation):
    def _run( self, short_or_long_id ):   
      try:
        db = self.db
        args = self.args
        row = BackupObject.find_backup( short_or_long_id, by_name=args.name )
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


