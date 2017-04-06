from .db import DBObject
class AgentObject(DBObject):
	FIELDS = [
		"id",
		"host",
		"port" ]
