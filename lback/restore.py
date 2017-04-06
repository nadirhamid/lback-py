
from .utils import untar, lback_backup_dir, lback_backup_ext, lback_backup_path

class Restore(object):
  def __init__(self, backup_id, folder='./'):
    self.archive = lback_backup_path( backup_id )
    self.backup_id = backup_id
    self.folder = folder
  def run(self, local=False):
    backup_dir = lback_backup_dir()
    ext = lback_backup_ext()
    untar(self.archive, self.folder)

class RestoreException(Exception):
     pass

