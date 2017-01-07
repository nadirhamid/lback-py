
from .operation import Operation, OperationNoArgs
from .utils import lback_print, lback_output, lback_error, lback_id
import shutil
import os

class OperationLs(OperationNoArgs):
    def _run( self ):
      try:
        db = self.db
        args = self.args
        current_dir = os.getcwd()
        select_cursor = db.cursor().execute("SELECT * FROM backups WHERE dirname = ?",( current_dir, ))
        backup = select_cursor.fetchone()
        while backup:
          filename = backup.get_filename()
          lback_print("%s\t%s"%(filename, backup.lback_id), "white")
          backup = select_cursor.fetchone()
      except Exception, ex:
        lback_error(ex)	

