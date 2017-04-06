
from .operation import OperationNoGlobs
from .utils import lback_print, lback_output, lback_error, lback_id
import shutil
import os

class OperationAgentAdd(OperationNoGlobs):
    def _run( self ):
      try:
        db = self.db
	id = lback_id()
	lback_output("ADDING agent")
        insert_cursor = db.cursor()
	insert_cursor.execute("INSERT INTO agents (id, host, port) VALUES (%s, %s, %s)", (id, self.args.host, self.args.port,))
	db.commit()
      except Exception, ex:
        lback_error(ex)	
