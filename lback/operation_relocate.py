
from .operation import OperationNoGlobs
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext
from .backup import BackupObject
import shutil
import os

class OperationRelocate(OperationNoGlobs):
    def _run( self, short_or_long_id ):   
      try:
	client = self.client
	backup = BackupObject.find_backup( short_or_long_id )
	client._run( self, backup )
      except Exception,ex:
        lback_error(ex)	
    def run( self ):
        self._run( self.args.id )

