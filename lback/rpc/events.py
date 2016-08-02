

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
	 MSG_BACKUP_FINISHED = ""
	 MSG_RESTORE_IN_PROGRESS= ""
	 MSG_RESTORE_STARTED = ""
	 MSG_RESTORE_STOPPED = ""

class EventObjects(object):
	 OBJECT_BACKUP= "Backup"
	 OBJECT_RESTORE = "Restore"
class EventTypes(object):
 	 TYPE_PROGRESS="PROGRESS"
	 TYPE_STARTED="STARTED"
	 TYPE_FINISHED ="FINISHED"
	 TYPE_ENDED="ENDED"
class EventStatuses(object):
	 STATUS_IN_PROGRESS="IN-PROGRESS"
	 STATUS_FINISHED = "FINISHED"
	 STATUS_STARTED = "STARTED"
	 STATUS_STOPPED = "STOPPED"
	 STATUS_ERR = "ERRORED"



def getStartStopped(status="", data=[],eventType="",obj="", message=""):
	 	return dict(
			data=data,
			eventType=eventType,
			obj=obj,
			message=message,
			status=status)


class Events(object):
	@staticmethod 
	def getProgressEvent(progress=0, message="", status="", obj="", data=[]):
		return json.dumps(dict(
			progress=progress,
			status=status,
			message=message,
			obj=obj,
			data=data,
			eventType=EventTypes.TYPE_PROGRESS
			))
	@staticmethod
	def getStartEvent(*args,**kwargs):
	    kwargs['eventType']=EventTypes.TYPE_STARTED
	    return  json.dumps(getStartStopped(**kwargs))
    	@staticmethod
	def getFinishedEvent(*args,**kwargs):
	    kwargs['eventType'] =EventTypes.TYPE_FINISHED
	    return json.dumps(getStartStopped(**kwargs))
	@staticmethod
	def getStopEvent( *args, **kwargs ):
	    kwargs['eventType'] = EventTypes.TYPE_ENDED
	    return json.dumps(getStartStopped(**kwargs))
		
		
		


