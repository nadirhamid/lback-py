
from .operation import Operation
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext, lback_backup_remove, lback_backup_path
from .backup import BackupObject
import shutil
import os

class OperationRm(Operation):
    def _run( self, short_or_long_id ):   
      try:
        db= self.db
        args = self.args
	client = self.client
        ext = lback_backup_ext()
        backup_dir = lback_backup_dir()
        backup =  BackupObject.find_backup( short_or_long_id )
        archive_loc = lback_backup_path( backup.id )
        lback_output("removing %s"%(backup.id))
        folder = backup.folder
  	client._run( self, backup )
        lback_backup_remove(backup.id)
        delete_cursor =db.cursor().execute("DELETE FROM backups WHERE lback_id = %s", ( backup.id, ) )
        db.commit()
      except Exception,ex:
        ## silent for rm
        lback_error( ex,True)
