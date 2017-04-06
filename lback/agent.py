from .db import DBObject
class AgentObject(DBObject):
  	TABLE = "agents"
	FIELDS = [
		"id",
		"host",
		"port" ]
