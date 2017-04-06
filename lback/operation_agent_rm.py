
from .operation import OperationNoGlobs
from .utils import lback_print, lback_output, lback_error, lback_id
from .agent import AgentObject
import shutil
import os

class OperationAgentRm(OperationNoGlobs):
    def _run( self  ):
      try:
	AgentObject.delete_by_id( self.args.id )
      except Exception, ex:
        lback_error(ex)	

