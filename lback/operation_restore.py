
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
        lback_output("Trying to restore from backup..")
        backup = BackupObject.find_backup( short_or_long_id, by_name=args.name )
        if args.clean \
        and os.path.isdir(backup.folder):
          lback_output("Cleaning directory..")
          shutil.rmtree(backup.folder)
	self.client._run(self, backup )
        lback_output("Backup Found. Now restoring compartment")

        rst = Restore(backup.id,folder=backup.folder)
        rst.run(local=True)
        lback_output("Restore has been successfully performed")
      except RestoreException, ex:
        lback_error(ex)	
      except Exception, ex:
        lback_error(ex)	


