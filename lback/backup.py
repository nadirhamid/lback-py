

import tarfile 
import os
from lback.utils import lback_backup_dir,lback_backup_ext,lback_output, is_writable
from lback.archive import Archive

class Backup(object):
  def __init__(self, backup_id, folder):
    backup_dir = lback_backup_dir()
    self.things = []
    self.backup_id = backup_id
    self.archive = Archive(backup_dir + backup_id+lback_backup_ext(), "w")
    self.folder = folder
  def run(self):
    self._folder( self.folder )
    self._pack()
      
  def _pack(self):
    lback_output( "Files have been gathered. Forming archive.." )
    for i in self.things:
      as_file = os.path.relpath(i, self.folder)
      if not is_writable( i ):
	  lback_output("Permissions not set for %s"%( i ), type="ERROR" )
      else:
          self.archive.obj.add(i, arcname=as_file ) 
    self.archive.obj.close()
  def _folder(self, pathname, prefix=''):
    l = os.listdir(prefix + pathname)
    lback_output("Added \"" + prefix + pathname + "\"")
    folders = [self._folder(i, prefix + pathname + "/") for i in l if os.path.isdir(prefix + pathname + "/" + i)]
    files = [self._file(i, prefix + pathname + "/") for i in l if os.path.isfile(prefix + pathname + "/" + i)]
    self.things.append(prefix + pathname)

    return prefix + pathname
  def _file(self, pathname, prefix=''):
    lback_output("Added \"" + prefix + pathname + "\"")
    self.things.append(prefix + pathname)

    return prefix + pathname

class BackupException(Exception):
    pass

class BackupObject(object):
    def __init__(self):
	 pass

