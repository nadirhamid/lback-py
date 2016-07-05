
import redis



class StateConnection(object):
	 def __init__(self,backupId, prefix=""):
		self.prefix=prefix
		self.pool = redis.ConnectionPool(host="127.0.0.1",port=6379)
		self.client = redis.Client(connection_pool= self.pool )
		self.backupId = backupid
	 def getState(self):
		return self.client.get(self.prefix+self.backupId)
	 def setState(self,data):
		return self.client.set(self.prefix+self.backupId, data)
	


class BackupState(StateConnection):
	 def __init__(self, backupId):
		super(StateConnection, self).__init__(backupId, "backup")
	
class RestoreState(object):
	 def __init__(self, backupId):
		super( StateConnection, self).__init__(backupId, "restore" )
