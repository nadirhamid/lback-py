
from .operation import OperationNoGlobs
from .utils import lback_print, lback_output, lback_error, lback_id
import shutil
import os

class OperationAgentRm(OperationNoGlobs):
    def _run( self  ):
      try:
        db = self.db
        db.cursor().execute("DELETE FROM agents WHERE agent_id = %s", (self.args.id,))
      except Exception, ex:
        lback_error(ex)	

