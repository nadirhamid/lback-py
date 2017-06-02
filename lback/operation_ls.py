
from .operation import Operation, OperationNoGlobs
from .utils import lback_print, lback_output, lback_error, lback_id
from .backup import BackupObject
import shutil
import os

class OperationLs(OperationNoGlobs):
    def _run( self ):
      try:
        db = self.db
        args = self.args
        current_dir = os.getcwd()
        select_cursor = db.cursor()
        select_cursor.execute("SELECT * FROM backups WHERE dirname = %s",( current_dir, ))
        db_backup = select_cursor.fetchone()
        while db_backup:
          backup = BackupObject( db_backup )
          filename = backup.get_filename()
          lback_print("%s\t%s\t%s"%(backup.id, filename, backup.distribution_strategy), "white")
          db_backup = select_cursor.fetchone()
      except Exception, ex:
        lback_error(ex)	

