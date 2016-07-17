
import json

class RPCErrorMessages(object):
   ERR_STREAMING_IN_PROGRESS="Streaming already in progress"
   ERR_MESSAGE = "Message could not be deserialized"
   ERR_NOT_READY = "Backup not ready for action specified"
   ERR_NOT_FOUND = "The object was not found"
   ERR_USER_AUTH = "The user could not be authenticated"
class RPCSuccessMessages(object):
   CONNECTION_OK = "Connected to server"
   POLL_OK  = "Got poll progress"
   POLL_ERROR = "Got poll progress"
def RPCMessage(message):
	try:
		return json.loads( message )
	except Exception, ex:
		return False


class RPCResponse(object):
	 def __init__(self, error, message="", data=[] ):
		self.error=error
		self.message = message
		self.data = json.loads(data)
	 def serialize(self):
		if self.error:
			return json.dumps(dict(
					error=self.error,
					message=self.message,
					data=self.data))
		return json.dumps(dict(
			error=self.error,
			message=self.message,
			data=self.data))
			
		

   
   
   

