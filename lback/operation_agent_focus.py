
from .operation import OperationNoGlobs
from .utils import lback_output, lback_error, lback_id, lback_backup_dir, lback_backup_ext, lback_backup_path, lback_dir
from .backup import BackupObject
from .agent import AgentObject
import shutil
import os

class OperationAgentFocus(OperationNoGlobs):
    def _run( self, short_or_long_id ):   
      try:
        agent_object = AgentObject.find_by_id( short_or_long_id )
        if not agent_object:
           raise("No agent found with ID %s"%( short_or_long_id, ))
        file_name = os.path.join(lback_dir(), ".lbackfocus")
        with open( file_name, "w+" ) as focus_file:
           focus_file.write( agent_object.id )
      except Exception,ex:
        lback_error(ex)	
    def run( self ):
        self._run( self.args.id )

