

import tarfile 
import os
from lback.utils import lback_backup_dir,lback_backup_ext,lback_output, is_writable, lback_db
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

  def get_filename( self ):
    splitted = self.folder.split("/")
    filename = splitted[ len( splitted ) - 1 ]
    return  filename

  @staticmethod
  def find_by_name( name ):
       db = lback_db()
       return db.cursor().execute("SELECT * FROM backups WHERE name = ?", (args.name,)).fetchone()
  @staticmethod
  def find_by_id( id ):
       db = lback_db()
       return db.cursor().execute("SELECT * FROM backups WHERE lback_id LIKE ?",("%"+id+"%",)).fetchone()
  @staticmethod
  def find_by_folder( folder ):
       db = lback_db()
       return db.cursor().execute("SELECT * FROM backups WHERE folder = ?", (os.path.abspath(folder),)).fetchone()
  @staticmethod
  def find_backup( id, by_name=False ):
    if by_name:
      backup = BackupObject.find_by_name( by_name )
      if not backup:
        raise Exception("Backup with name not found")
    else:
      backup = BackupObject.find_by_id(id)
      if not backup:
        backup = BackupObject.find_by_folder(id)
      if not backup:
        raise Exception("Backup with Folder/ID not found")
    return backup


