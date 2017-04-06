
from .operation import OperationNoGlobs
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext, lback_backup_path
from .backup import BackupObject
import shutil
import os

class OperationMv(OperationNoGlobs):
    def _run( self, short_or_long_id ):   
      try:
        db = self.db
        args = self.args
        backup = BackupObject.find_backup( short_or_long_id )
        ext = lback_backup_ext()
        backup_dir = lback_backup_dir()
        folder = os.path.abspath( args.dst )
        dirname = os.path.dirname( folder )
        archive = lback_backup_path( backup.id )
        update_cursor = db.cursor().execute("UPDATE backups SET folder = %s, dirname = %s WHERE lback_id = %s",
          (folder, dirname, backup.id))
        db.commit()
        lback_output("Moved compartment successfully")
      except Exception,ex:
        lback_error(ex)	
    def run( self ):
        self._run( self.args.id )

