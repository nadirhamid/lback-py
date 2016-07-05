

from pyee import EventEmitter
from lback.rpc.api import RPCSuccessMessages, RPCErrorMessages, RPCResponse
from lback.rpc.state import BackupState
from multiprocessing import Queue
from threading import Thread
import json


class EventMessages(object):
	 MSG_BACKUP_IN_PROGRESS = ""
	 MSG_BACKUP_STARTED = ""
	 MSG_BACKUP_STOPPED = ""
	 MSG_RESTORE_IN_PROGRESS= ""
	 MSG_RESTORE_STARTED = ""
	 MSG_RESTORE_STOPPED = ""

class EventObjects(object):
	 OBJECT_BACKUP= "Backup"
	 OBJECT_RESTORE = "Restore"
class EventTypes(object):
 	 TYPE_PROGRESS="PROGRESS"
	 TYPE_STARTED="STARTED"
	 TYPE_ENDED="ENDED"
class EventStatuses(object):
	 STATUS_IN_PROGRESS="IN-PROGRESS"
	 STATUS_STARTED = "STARTED"
	 STATUS_STOPPED = "STOPPED"
	 STATUS_ERR = "ERRORED"



def getStartStopped(status="", data=[],eventType="",obj=""):
	 	return dict(
			data=data,
			eventType=eventType,
			obj=obj,
			status=status)


class Events(object):
	@staticmethod 
	def getProgressEvent(progress=0, status="",data=[]):
		return json.dumps(dict(
			progress=progress,
			status=status,
			data=data,
			eventType=EventTypes.TYPE_PROGRESS
			))
	@staticmethod
	def getStartEvent(status="", data=[], eventType=EventTypes.TYPE_STARTED,obj=""):
	    return  json.dumps(getStartStopped(**kwargs))
	@staticmethod
	def getStopEvent( status="", data=[], eventType=EventTypes.TYPE_STOPPED,obj=""):
	    return json.dumps(getStartStopped(**kwargs))
		
		
		


