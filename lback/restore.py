
from lback.utils import Util, lback_backup_dir, lback_backup_ext

class Restore(object):
  def __init__(self, archive_loc, folder='./', clean=False):
    self.archive,self.status = archive_loc, 0
    self.clean = clean
    self.folder = folder
  def run(self, local=False, uid=''):
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

