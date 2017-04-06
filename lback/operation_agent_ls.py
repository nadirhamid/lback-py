
from .operation import OperationNoGlobs
from .utils import lback_print, lback_output, lback_error, lback_id
from .agent import AgentObject
import shutil
import os

class OperationAgentLs(OperationNoGlobs):
    def _run( self ):
      try:
        db = self.db
        args = self.args
        select_cursor = db.cursor()
	select_cursor.execute("SELECT * FROM agents")
        db_agent = select_cursor.fetchone()
        while db_agent:
	  agent = AgentObject(db_agent)
          lback_print("%s\t%s\t%s"%(agent.id, agent.host, agent.port), "white")
          db_agent = select_cursor.fetchone()
      except Exception, ex:
        lback_error(ex)	

