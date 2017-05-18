

import tarfile 
import os
from .db import DBObject
from .utils import lback_backup_dir,lback_backup_ext,lback_output,lback_backup_path, is_writable, lback_db,  lback_backup_path, lback_id_temp
from .archive import Archive

class Backup(object):
  def __init__(self, backup_id, folder, temp=False):
    backup_dir = lback_backup_dir()
    self.things = []
    self.backup_id = backup_id
    self.archive = Archive(lback_backup_path(backup_id), "w")
    self.folder = folder
  def run(self):
    self._folder( self.folder )
    self._pack()
  def write_chunked(self, gen):
    def rollback():
        os.remove( path )
    def verify_chunk( chunk ):
        if not chunk:
           raise BackupException("Unable to write backup. Stream failed")

    path = lback_backup_path(self.backup_id ) 
    try:
        with open( path, "w+" ) as backup_archive_file:
            for chunk in gen:
               verify_chunk( chunk )
               backup_archive_file.write( chunk )
    except Exception,ex:
        rollback()
        raise ex
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

class BackupObject(DBObject):
  TABLE = "backups"
  FIELDS = [
	"id",
	"name",
	"time",
	"folder",
	"dirname",
	"size" ]
  def get_filename( self ):
    splitted = self.folder.split("/")
    filename = splitted[ len( splitted ) - 1 ]
    return  filename
  @staticmethod
  def find_by_name( name ):
       db = lback_db()
       select_cursor =db.cursor()
       select_cursor.execute("SELECT * FROM backups WHERE name = %s", (args.name,))
       db_backup = select_cursor.fetchone()
       return BackupObject(db_backup)
  @staticmethod
  def find_by_folder( folder ):
       db = lback_db()
       select_cursor = db.cursor()
       select_cursor.execute("SELECT * FROM backups WHERE folder = %s", (os.path.abspath(folder),))
       db_backup = select_cursor.fetchone()
       return BackupObject(db_backup)
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


