
from lback.utils import Util, lback_backup_dir, lback_backup_ext

class Restore(object):
  def __init__(self, backup_id, archive_loc, folder='./', clean=False, state=None):
    self.archive,self.status = archive_loc, 0

    self.backup_id = backup_id
    self.clean = clean
    self.folder = folder
    self.state = state
  def run(self, local=False):
    backup_dir = lback_backup_dir()
    ext = lback_backup_ext()
    if local:
      self.archive = backup_dir + self.backup_id + ext

    if self.clean:
      shutil.rmtree(self.folder)
      Util().untar(self.archive, self.folder)
    else:
      Util().untar(self.archive, self.folder)    
class RestoreException(Exception):
     pass

