
from .operation import OperationNoArgs
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext
from .backup import BackupObject
import shutil
import os

class OperationMv(OperationNoArgs):
    def _run( self, short_or_long_id ):   
      try:
        db = self.db
        args = self.args
        backup = BackupObject.find_backup( short_or_long_id )
        ext = lback_backup_ext()
        backup_dir = lback_backup_dir()
        folder = os.path.abspath( args.dst )
        dirname = os.path.dirname( folder )
        archive = backup_dir + backup.lback_id + ext
        update_cursor = db.cursor().execute("UPDATE backups SET folder = ?, dirname = ? WHERE lback_id = ?",
          (folder, dirname, backup.lback_id))
        db.commit()
        lback_output("Moved compartment successfully")
      except Exception,ex:
        lback_error(ex)	
    def run( self ):
        self._run( self.args.id )

