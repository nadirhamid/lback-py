
import redis
from lback.utils import lback_output


class StateConnection(object):
	 def __init__(self,backupId, prefix=""):
		self.prefix="LBACK_"+prefix
		self.pool = redis.ConnectionPool(host="127.0.0.1",port=6379)
		self.client = redis.Redis(connection_pool= self.pool )
		self.backupId = backupId
	 def getState(self):
		lback_output("RPC - Getting state Backup: {0}".format( self.backupId ))
		data = self.client.get(self.prefix+self.backupId)
		lback_output("RPC - Got state: {0}".format( data ) )
	        return data
	 def setState(self,data):
		lback_output("RPC - Setting state Backup: {0}: {1}".format( self.backupId, data) )
		return self.client.set(self.prefix+self.backupId, data)
	


class BackupState(StateConnection):
	 def __init__(self, backupId):
		super(BackupState, self).__init__(backupId, prefix="backup_")
	
class RestoreState(StateConnection):
	 def __init__(self, backupId):
		super(RestoreState, self).__init__(backupId, prefix="restore_" )
