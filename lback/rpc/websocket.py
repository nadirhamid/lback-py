from pyee import EventEmitter
from lback.rpc.api import RPCSuccessMessages, RPCErrorMessages, RPCResponse, RPCMessage
from lback.rpc.state import BackupState
from multiprocessing import Queue
from threading import Thread
from  lback.rpc.events import EventStatuses, EventObjects
from lback.rpc.auth import Auth

from gevent import monkey; monkey.patch_all()
import importlib
import argparse
import random
import os
import json
from gevent import monkey
monkey.patch_all()
import gevent
import gevent.pywsgi
from lback.utils import lback_output, lback_auth_user, lback_uuid, lback_rpc_serialize
from ws4py.server.geventserver import WebSocketWSGIApplication, WebSocketWSGIHandler, GEventWebSocketPool
from ws4py import configure_logger
from chaussette.backend._gevent import Server as GEventServer
from chaussette.backend import register
from chaussette.server import make_server
import lback
import time
import socket


from ws4py.websocket import EchoWebSocket, WebSocket




emitter = EventEmitter()
def  getRuntimeAndArgs():
     module = importlib.import_module("lback.runtime")
     return [module.Runtime,module.RuntimeArgs]

   

def getObject(msg):
	 
         if msg['obj'] ==  EventObjects.OBJECT_BACKUP:
		stateObj = BackupState( msg['backupId'] )
	 elif msg['obj'] == EventObjects.OBJECT_RESTORE:
		stateObj = RestoreState( msg['restoreId'] )
         return stateObj
   



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
class  BackupServerBackup(object):
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
	   self.restoreUuid = msg.backupId
           self.socket = socket
       def serveRestore( self ):
            module = importlib.import_module("lback.runtime")
	    args = module.RuntimeArgs(
		restore=True,
		local=True,
		id=self.restoreUuid
		)
	    runtime = module.Runtime( args )
	    runtime.perform()
		
            self.socket.send(RPCResponse(
			True,
			 message="Restore complete").serialize())
			
			
    
# event emitter for LBack RPC
	
# based on websockets
class  BackupServer( object ):
   def received_message(self, message):
	 msg = RPCMessage(message)
	 if not msg:
	 	return self.send(RPCResponse(
			False,
			message=RPCErrorMessages.ERR_MESSAGE).serialize())

         if msg['type'] == "auth":
		 user = lback_auth_user( msg['auth']['username'], msg['auth']['password'] )
		 if not user:
			 return self.send(RPCResponse(
				False,
				message=RPCErrorMessages.ERR_USER_AUTH).serialize())
		 auth = Auth()
		 username = msg['auth']['username']
		 password = msg['auth']['password']
		 token = auth.getAuthenticationToken( username, password )
		 try:
		         auth.setAuthenticationToken( username, password,  token )
			 return self.send(RPCResponse(	
				False,
				message=RPCSuccessMessages.AUTH_OK,
				data=json.dumps({"token": token})
				).serialize())
		 except Exception, ex:
			msg = RPCErrorMessages.ERR_USER_AUTH_TOKEN + " (ERROR: %s)"%( str(ex) )
			return self.send(RPCResponse(	
				True,
				message=msg).serialize())
	 else:
		auth = Auth()	
		if auth.isAuthenticated( msg['token'] ):
			 if msg['type'] == "poll":
				 stateObj = getObject(msg)
				 state = getBackupState(stateObj)
				 self.send(state.serialize())
			 elif msg['type'] == "stream":
				 stateObj = getObject(msg)
				 streamer = BackupServerStreamer(self, stateObj)
				 thread = Thread(target=streamer.startStreaming, args=())
				 thread.daemon = True
				 thread.run()
			 elif msg['type'] == "dobackup":
				 id = lback_uuid()
				 backup =  BackupServerBackup(self, msg)
				 thread = Thread(target=backup.serveBackup, args=())
				 thread.daemon = True
				 thread.run()
			 elif msg['type'] in ['adduser', 'deluser', 'getbackup', 'listbackups', 'getrestore']:
				runtime,runtimeargs=getRuntimeAndArgs()
				rargs =  runtimeargs(**dict(
					dict(type=msg['type']).items() +
					msg['args'].items()))
				setattr( rargs, msg['type'], True )
				runtimeobject = runtime( rargs )
				result = runtimeobject.perform()
				self.send(  lback_rpc_serialize( result ) ) 
				 
					 
			 elif msg['type'] =="dorestore":
				 restore = BackupServerRestore(self, msg)
				 thread = Thread(target=restore.serveRestore, args=())
				 thread.daemon =True
				 thread.run()
		else:
			return self.send(RPCResponse(
				True,
				message=RPCErrorMessages.ERR_USER_AUTH).serialize())
			  
			 
		 
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
		
		 
			
		


		



				
    

		 
