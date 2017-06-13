from .db import DBObject
from .utils import lback_db, lback_output
class AgentObject(DBObject):
    TABLE = "agents"
    FIELDS = [
  	    "id",
  	    "host",
  	    "port" ]

    @staticmethod
    def find_by_id( partial_or_full_id ):
       lback_output("FINDING AGENT BY ID %s"%(partial_or_full_id))
       db = lback_db()
       select_cursor =db.cursor()
       select_cursor.execute("SELECT * FROM agents WHERE ID LIKE %s", ('%' + partial_or_full_id + '%',))
       db_backup = select_cursor.fetchone()
       return AgentObject.eval_and_return(db_backup)
    @staticmethod
    def find_by_name( name ):
       lback_output("FINDING AGENT BY NAME %s"%(name))
       db = lback_db()
       select_cursor =db.cursor()
       select_cursor.execute("SELECT * FROM agents WHERE name = %s", (name,))
       db_backup = select_cursor.fetchone()
       return AgentObject.eval_and_return(db_backup)


