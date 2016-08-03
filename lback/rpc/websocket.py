from pyee import EventEmitter
from lback.rpc.api import RPCSuccessMessages, RPCErrorMessages, RPCResponse, RPCMessage
from lback.rpc.state import BackupState
from multiprocessing import Queue
from threading import Thread
from  lback.rpc.events import EventStatuses, EventObjects
from lback.rpc.auth import Auth
from  lback.rpc.websocket_threads import BackupServerStreamer, BackupServerBackup, RestoreServerStreamer, BackupServerRestore, getObject, getObjState
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

   
# event emitter for LBack RPC
	
# based on websockets
class  BackupServer( object ):
   def received_message(self, message):
	 msg = RPCMessage(message)
	 if not msg:
	 	return self.send(RPCResponse(
			False,
			message=RPCErrorMessages.ERR_MESSAGE,
			msgtype="error",
			).serialize())

         if msg['type'] == "auth":
		 user = lback_auth_user( msg['auth']['username'], msg['auth']['password'] )
		 if not user:
			 return self.send(RPCResponse(
				False,
				msgtype="auth",
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
			 	msgtype="auth",
				data=json.dumps({"token": token})
				).serialize())
		 except Exception, ex:
			msg = RPCErrorMessages.ERR_USER_AUTH_TOKEN + " (ERROR: %s)"%( str(ex) )
			return self.send(RPCResponse(	
				True,
				msgtype="auth",
				message=msg).serialize())
	 else:
		auth = Auth()	
		if auth.isAuthenticated( msg['token'] ):
			 if msg['type'] == "pollbackup":
				 stateObj = getObject(msg['args'])
				 state = getObjState("pollbackup", stateObj)
				 self.send(state.serialize())
			 elif msg['type'] == "pollrestore":
				 stateObj = getObject(msg['args'])
				 state = getObjState("pollrestore",stateObj)
				 self.send(state.serialize())
			 elif msg['type'] == "streambackup":
				 stateObj = getObject(msg['args'])
				 streamer = BackupServerStreamer(self, stateObj)
				 thread = Thread(target=streamer.startStreaming, args=())
				 thread.daemon = True
				 thread.run()
			 elif msg['type'] == "streamrestore":
				 stateObj = getObject(msg['args'])
				 streamer = RestoreServerStreamer(self, stateObj)
				 thread = Thread(target=streamer.startStreaming, args=())
				 thread.daemon = True
				 thread.run()
			 elif msg['type'] == "dobackup":
				 id = lback_uuid()
				 backup =  BackupServerBackup(self, msg['args'])
				 thread = Thread(target=backup.serveBackup, args=())
				 thread.daemon = True
				 thread.run()
			 elif msg['type'] in ['adduser', 'deluser', 'getbackup', 'listbackups', 'listrestores', 'getrestore']:
				runtime,runtimeargs=getRuntimeAndArgs()
				rargs =  runtimeargs(**dict(
					dict(type=msg['type']).items() +
					msg['args'].items()))
				setattr( rargs, msg['type'], True )
				runtimeobject = runtime( rargs )
				result = runtimeobject.perform()
				self.send(  lback_rpc_serialize( result ) ) 
				 
					 
			 elif msg['type'] =="dorestore":
				 restore = BackupServerRestore(self, msg['args'])
				 thread = Thread(target=restore.serveRestore, args=())
				 thread.daemon =True
				 thread.run()
		else:
			return self.send(RPCResponse(
				True,
				message=RPCErrorMessages.ERR_USER_AUTH,
				msgtype=msg['type']
				).serialize())
			  
			 
		 
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
		
		 
			
		


		



				
    

		 
