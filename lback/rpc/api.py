
import json

class RPCErrorMessages(object):
   ERR_STREAMING_IN_PROGRESS=""
   ERR_MESSAGE = "Message could not be deserialized"
class RPCSuccessMessages(object):
   CONNECTION_OK = "Connected to server"
   POLL_OK  = "Got poll progress"
   POLL_ERROR = "Got poll progress"

class RPCResponse(object):
	 def __init__(self, error, message="", data=[] ):
		self.error=error
		self.message = message
		self.data = data
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
			
		

   
   
   

