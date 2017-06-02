
from .operation import Operation
from .operation_restore import OperationRestore
from .operation_args import OperationArgs
from .parser_distribution_strategy import ParserDistributionStrategy
from .utils import lback_output, lback_id, lback_error, lback_temp_path, lback_backup, get_folder_size
from .backup import BackupObject
import glob
import shutil
import os
import time

class OperationModify(Operation):
    PARSERS = [
       ParserDistributionStrategy
    ]
    def _run( self, id ):
      try:
        backup = BackupObject.find_backup( id )
        lback_output("MODIFY BACKUP %s"%( backup.id, ) )
        db = self.db    
        args = self.args
        db.cursor().execute("UPDATE backups SET distribution_strategy = %s WHERE ID = %s", ( args.distribution_strategy, backup.id, ) )
        db.commit()
      except Exception, ex:
        lback_error(ex)	
