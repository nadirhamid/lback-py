from lback.utils import lback_backup_path,lback_id
class BasicWrapper(object):
  def get_id(self):
     return self.id
  def get_full_id(self):
     return lback_id(self.get_id(),suffix=self.SUFFIX)
  def get_file(self):
     return lback_backup_path(self.get_full_id())

