
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
   DELETED_BACKUP = "Backup was deleted"
   DELETE_BACKUP_ERROR = "Error in backup delete"
   DELETED_RESTORE = "Restore was deleted"
   DELETE_RESTORE_ERROR = "Error in restore delete"
   LISTED_USERS = "Listed users"
   LISTED_USER = "Listed user"
   DELETED_USER = "User was deleted"
   DELETE_USER_ERROR = "User could not be deleted"
   EXISTS_USER = "User with this name already exists"
   CREATED_USER = "User was created"
   CREATE_USER_ERROR = "User could not be created"

def RPCMessage(message):
	try:
		return json.loads( message )
	except Exception, ex:
		return False


class RPCResponse(object):
	 def __init__(self, error, message="", data="{}", msgtype="", request_id=""):
		self.error=error
		self.type =msgtype
		self.message = message
		if type( data ) is str:
			self.data = json.loads(data)
		self.request_id=request_id
	 def serialize(self):
		if self.error:
			return json.dumps(dict(
					type=self.type,
					error=self.error,
					message=self.message,
					request_id=self.request_id,
					data=self.data))
		return json.dumps(dict(
			error=self.error,
			message=self.message,
			request_id=self.request_id,
			data=self.data))
			
		

   
   
   

