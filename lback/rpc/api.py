
import json

class RPCErrorMessages(object):
   ERR_STREAMING_IN_PROGRESS="Streaming already in progress"
   ERR_MESSAGE = "Message could not be deserialized"
   ERR_NOT_READY = "Backup not ready for action specified"
   ERR_NOT_FOUND = "The object was not found"
   ERR_USER_AUTH = "The user could not be authenticated"
   ERR_USER_AUTH_TOKEN = "The user token could not be validated"
class RPCSuccessMessages(object):
   CONNECTION_OK = "Connected to server"
   RESULT_OK = "Result was retrieved"
   POLL_OK  = "Got poll progress"
   POLL_ERROR = "Got poll progress"
   AUTH_OK = "Authentication was successful"
class RPCMessages(object):
   LISTED_BACKUPS = "Listed backups"
   LISTED_BACKUP = "Listed backup"
   LISTED_RESTORES = "Listed restores"
   LISTED_RESTORE = "Listed restore"
def RPCMessage(message):
	try:
		return json.loads( message )
	except Exception, ex:
		return False


class RPCResponse(object):
	 def __init__(self, error, message="", data="{}", msgtype=""):
		self.error=error
		self.type =msgtype
		self.message = message
		self.data = json.loads(data)
	 def serialize(self):
		if self.error:
			return json.dumps(dict(
					type=self.type,
					error=self.error,
					message=self.message,
					data=self.data))
		return json.dumps(dict(
			error=self.error,
			message=self.message,
			data=self.data))
			
		

   
   
   

