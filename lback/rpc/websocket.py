from pyee import EventEmitter
from lback.rpc.api import RPCSuccessMessages, RPCErrorMessages, RPCResponse, RPCMessage
from lback.rpc.state import BackupState
from multiprocessing import Queue
from threading import Thread
from  lback.rpc.events import EventStatuses, EventObjects

from SimpleWebSocketServer import SimpleWebSocketServer, WebSocket
from gevent import monkey; monkey.patch_all()
import argparse
import random
import os
from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pywsgi
from lback.utils import lback_output
from ws4py.server.geventserver import WebSocketWSGIApplication, WebSocketWSGIHandler, GEventWebSocketPool
from ws4py import configure_logger
from chaussette.backend._gevent import Server as GEventServer
from chaussette.backend import register
from chaussette.server import make_server
import time
import socket


from ws4py.websocket import EchoWebSocket, WebSocket




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
	
	 #message = self.stateObj.getState()
	 while not backupState.error and (
			backupState.data['status'] ==EventStatuses.STATUS_IN_PROGRESS
			or
			backupState.data['status']  == EventStatuses.STATUS_STARTED ):
		self.client.send( backupState.serialize() )
		time.sleep( 1 )
	 self.client.send( backupState.serialize() )
	 
# event emitter for LBack RPC
# based on websockets
class  BackupServer( object ):
   def received_message(self, message):
	 msg = RPCMessage(message)
	 if not msg:
	 	return self.send(RPCResponse(
			False,
			message=RPCErrorMessages.ERR_MESSAGE).serialize())
	 if msg['obj'] ==  EventObjects.OBJECT_BACKUP:
		stateObj = BackupState( msg['backupId'] )
	 elif msg['obj'] == EventObjects.OBJECT_RESTORE:
		stateObj = RestoreState( msg['restoreId'] )
	 
	 hasState = stateObj.getState()
	 if not hasState:
		 return self.send(RPCResponse(
		 	False,
			message=RPCErrorMessages.ERR_NOT_READY).serialize())
	 
	 if msg['type'] == "poll":
		 state = getBackupState(stateObj)
		 self.send(state.serialize())
    	 elif msg['type'] == "stream":
	 	 streamer = BackupServerStreamer(self, stateObj)
		 thread = Thread(target=streamer.startStreaming, args=())
	   	 thread.daemon = True
		 thread.run()
class WebSocketChaussette( GEventServer ):
   handler_class = WebSocketWSGIHandler
   def __init__(self,*args,**kwargs):
        self.server = GEventServer.__init__(self, *args, **kwargs)	
	self.pool = GEventWebSocketPool()
   def close(self):
	self.pool.close()
	

class WebSocketGevent( WebSocket, BackupServer ):
   def opened(self):
	lback_output("Received connection for Lback RPC ")
   def received_message(self, message):
   	lback_output("Received message: %s"%(str(message)))
        BackupServer.received_message(self, message.data) 
   def closed(self, code, reason=""):
	lback_output("Received disconnection")
   

   
class WebSocketServer( object ):
	 def __init__(self, host, port):
		register("ws4py", WebSocketChaussette)
		logger = configure_logger()
		self.server =  make_server(
			app=WebSocketWSGIApplication(handler_cls=WebSocketGevent),
			host=host,
			port=port,
		 	backend="ws4py",
			address_family=socket.AF_INET,
			logger=logger )
		self.server.serve_forever()
		
		 
			
		


		



				
    

		 
