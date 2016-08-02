
class BaseMeta( object ):
   def __init__(self,id=None,size=None,progressPct=None, progressSz=None,message=None):
	 self.id = id
	 self.size = size
	 self.progressSz = progressSz
	 self.progressPct = progressPct
	 self.message = message
   def serialize(self):
	 return dict(
		id=self.id,
		progressPct=self.progressPct,
		progressSz=self.progressSz,
		message=self.message,
		size=self.size)



class BackupMeta( BaseMeta ):
    pass

class RestoreMeta( BaseMeta ):
    pass
