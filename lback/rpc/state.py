
import redis
from lback.utils import lback_output


class StateConnection(object):
	 def __init__(self,objectId, prefix="", obj="Backup"):
		self.prefix="LBACK_"+prefix
		self.pool = redis.ConnectionPool(host="127.0.0.1",port=6379)
		self.client = redis.Redis(connection_pool= self.pool )
		self.objectId = objectId
	 	self.obj = obj 
	 def getState(self):
		lback_output("RPC - Getting state {}: {}".format( self.obj, self.objectId ) )
		data = self.client.get(self.prefix+self.objectId)
		lback_output("RPC - Got state: {0}".format( data ) )
	        return data
	 def setState(self,data):
		lback_output("RPC - Setting state {}: {}: {}".format( self.obj, self.objectId, data) )
		return self.client.set(self.prefix+self.objectId, data)
	


class BackupState(StateConnection):
	 def __init__(self, backupId):
		super(BackupState, self).__init__(backupId, prefix="backup_")
	
class RestoreState(StateConnection):
	 def __init__(self, restoreId):
		super(RestoreState, self).__init__(restoreId, prefix="restore_" , obj="Restore")
