
from lback.utils import Util, lback_backup_dir, lback_backup_ext
from lback.rpc.events import Events, EventStatuses, EventObjects, EventMessages
from lback.rpc.meta import RestoreMeta

class Restore(object):
  def __init__(self, archive_loc, folder='./', clean=False, state=None):
    self.archive,self.status = archive_loc, 0
    self.clean = clean
    self.folder = folder
    self.state = state
  def run(self, local=False, uid='', rid=''):
    backupDir = lback_backup_dir()
    ext = lback_backup_ext()
    if local:
      self.archive = backupDir + uid + ext

    if self.clean:
      shutil.rmtree(self.folder)
      Util().untar(self.archive, self.folder)
    else:
      Util().untar(self.archive, self.folder)    
    self.status = 1

