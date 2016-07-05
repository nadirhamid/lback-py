

class BackupMeta( object ):
    def __init__(self,id=None,size=None,progress=None,message=None):
	 self.id = id
	 self.size = size
	 self.progress = progress
	 self.message = message
    def serialize(self):
	 return dict(
		id=self.id,
		progress=self.progress,
		message=self.message,
		size=self.size)

class RestoreMeta( object ):
    pass
