
from lback.utils import lback_uuid
from lback.rpc.api import RPCResponse
import importlib
import json

def getObject(msg):
	 
         if msg['obj'] ==  EventObjects.OBJECT_BACKUP:
		stateObj = BackupState( msg['backupId'] )
	 elif msg['obj'] == EventObjects.OBJECT_RESTORE:
		stateObj = RestoreState( msg['restoreId'] )
         return stateObj
   

## all connections

def getObjState(objtype, state):
		 state = state.getState()
		 if state:
			msg = RPCResponse(
				True,
				message=RPCSuccessMessages.POLL_OK,
				data=state,
				msgtype=objtype,
				 )
		 else:
			msg = RPCResponse(
				False,
				message=RPCErrormessages.POLL_ERROR,
				msgtype=objtype
			 )
		 return msg


class ServerStreamer(object):
   def __init__(self, client, type, stateObj):
	 self.client = client
	 self.stateObj = stateObj
	 self.type = type
   def startStreaming(self):
	 backupState= getObjState(self.type, self.stateObj)
	
	 #message = self.stateObj.getState()
	 while not backupState.error and (
			backupState.data['status'] ==EventStatuses.STATUS_IN_PROGRESS
			or
			backupState.data['status']  == EventStatuses.STATUS_STARTED ):
		self.client.send( backupState.serialize() )
		time.sleep( 1 )
	 self.client.send( backupState.serialize() )

class BackupServerStreamer(ServerStreamer):
   def __init__(self,client,stateObj):
	 super(BackupServerStreamer,self).__init__(self,client,"streambackup",stateobj)
class RestoreServerStreamer(ServerStreamer):
   def __init__(self,client,stateObj):
	 super(RestoreServerStreamer,self).__init__(self,client,"streamrestore",stateobj)



class BackupServerBackup(object):
	 def __init__(self, socket, msg):
		  self.backupUuid = lback_uuid()
	    	  self.socket = socket
		  self.msg = msg
	 def serveBackup(self):
		  module = importlib.import_module("lback.runtime")
		  msg = json.dumps({"backupId": self.backupUuid})
		  self.socket.send(RPCResponse(
			  True,
			   message="",
			   msgtype="dobackup",
			  data=msg).serialize()
			)
		   
		  args =  module.RuntimeArgs(backup=True, id=self.backupUuid,
				local=True, 
				name=self.msg['name'],
				version=self.msg['version'],
				folder=self.msg['folder'])
		  runtime = module.Runtime(args)
		  runtime.perform()

class BackupServerRestore(object):
       def __init__(self, socket, msg):
	   self.restoreUuid = lback_uuid()
           self.socket = socket
	   self.msg =msg
       def serveRestore( self ):
            module = importlib.import_module("lback.runtime")
	    msg = json.dumps({"restoreId": self.restoreUuid})
	    args = module.RuntimeArgs(
		restore=True,
		local=True,
		id=self.msg['backupId'],
		rid=self.restoreUuid
		)
	    runtime = module.Runtime( args )
	    runtime.perform()
		
            self.socket.send(RPCResponse(
			True,
			 message="Restore complete",
			msgtype="dorestore",
			data=msg
			).serialize())
			
			
    

