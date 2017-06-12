
from .operation import OperationNoGlobs
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext, lback_backup_path
from .backup import BackupObject
import shutil
import os

class OperationFocus(OperationNoGlobs):
    def _run( self, short_or_long_id ):   
      try:
        pass
      except Exception,ex:
        lback_error(ex)	
    def run( self ):
        self._run( self.args.id )

