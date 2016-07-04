
from lback.utils import Util

class Restore(object):
  def __init__(self, zip_file_loc, folder='./', clean=False):
    self.zip_file,self.status = zip_file_loc, 0
    self.clean = clean
    self.folder = folder
  def run(self, local=False, uid=''):
    backupDir = lback_backup_dir()
    if local:
      self.zip_file = backupDir + uid + ".zip"

    if self.clean:
      shutil.rmtree(self.folder)
      Util().unzip(self.zip_file, self.folder)
    else:
      Util().unzip(self.zip_file, self.folder)    
    self.status = 1

