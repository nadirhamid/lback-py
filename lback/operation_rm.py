
from .operation import Operation
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext
from .backup import BackupObject
import shutil
import os

class OperationRm(Operation):
    def _run( self, short_or_long_id ):   
      try:
        db= self.db
        args = self.args
        ext = lback_backup_ext()
        backup_dir = lback_backup_dir()
        backup =  BackupObject.find_backup( short_or_long_id )
        archive_loc = backup_dir + backup.lback_id + ext
        lback_output("removing %s"%(backup.lback_id))
        folder = backup.folder
        os.remove(archive_loc)
        delete_cursor =db.cursor().execute("DELETE FROM backups WHERE lback_id = ?", ( backup.lback_id, ) )
        db.commit()
      except Exception,ex:
        ## silent for rm
        lback_error( ex,True)
