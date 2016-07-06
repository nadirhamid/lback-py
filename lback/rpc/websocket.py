from pyee import EventEmitter
from lback.rpc.api import RPCSuccessMessages, RPCErrorMessages, RPCResponse, RPCMessage
from lback.rpc.state import BackupState
from multiprocessing import Queue
from threading import Thread
from  lback.rpc.events import EventStatuses

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket



emitter = EventEmitter()


## all connections

def getBackupState(state):
		 state = state.getState()
		 if state:
			msg = RPCResponse(
				True,
				message=RPCSuccessMessages.POLL_OK,
				data=state
				 )
		 else:
			msg = RPCResponse(
				False,
				message=RPCErrormessages.POLL_ERROR
			 )
		 return msg
 	 	 
class BackupServerStreamer(object):
   def __init__(self, client, stateObj):
	 self.client = client
	 self.stateObj = stateObj
   def startStreaming(self):
	 backupState= getBackupState(self.stateObj)
	
	 message = self.stateObj.getState()
	 while not backupState.error and (
			message['status'] ==EventStatuses.STATUS_IN_PROGRESS
			or
			message['status'] == EventStatuses.STATUS_STARTED ):
		self.client.send( backupState.serialize() )
		time.sleep( 1 )
	 self.client.send( backupState.serialize() )
	 

# event emitter for LBack RPC
# based on websockets
class  BackupServer( WebSocket ):
   def handleConnection(self, connection):
	
	 self.sthread = False
	 msg = RPCResponse(
		True,
		message=RPCSuccessMessages.CONNECTION_OK )
	 self.send( msg.serialize() )
   def handleMessage(self):
	 msg = RPCMessage(self.data)
	 if not msg:
	 	return self.send(RPCResponse(
			False,
			message=RPCErrorMessages.ERR_MESSAGE).serialize())
	 if msg['obj'] ==  EventObjects.OBJECT_BACKUP:
		stateObj = BackupState( msg['backupId'] )
	 elif msg['obj'] == EventObjects.OBJECT_RESTORE:
		stateObj = RestoreState( msg['backupId'] )


	 hasState = state.getState()
	 if not hasState:
		 return self.send(RPCResponse(
		 	False,
			message=RPCErrorMessages.ERR_NOT_READY).serialize())
	 
	 if msg['type'] == "poll":
		 state = getBackupState(stateObj)
		 self.send(state.serialize())
    	 elif msg['type'] == "stream":
	 	 streamer = BackupServerStreamer(self, stateObj)
		 if not self.sthread:
			 self.sthread = Thread(target=streamer.startStreaming, args=(streamer))
			 self.sthread.run()
		 else:
			 self.send( RPCResponse(
				False,
				message=RPCErrorMessages.ERR_STREAMING_IN_PROGRESS))
   def handleClose(self):
	  self.close(self)
				
    

		 
