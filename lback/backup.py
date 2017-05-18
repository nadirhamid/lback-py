

import tarfile 
import os
from .db import DBObject
from .utils import lback_backup_dir,lback_backup_ext,lback_output,lback_backup_path, is_writable, lback_db,  lback_backup_path, lback_id_temp
from .archive import Archive

class Backup(object):
  def __init__(self, backup_id, folder, temp=False, diff=False):
    backup_dir = lback_backup_dir()
    self.archive_list = []
    self.backup_id = backup_id
    self.folder = folder
    self.diff = diff
  def run(self):
    self.archive = Archive(lback_backup_path(self.backup_id), "w")
    self._folder( "" )
    self._pack()
  def run_diff(self, diff_backup):
    self.diff_backup = diff_backup 
    self.run()
  def write_chunked(self, gen):
    path = lback_backup_path(self.backup_id ) 
    with open( path, "w+" ) as backup_archive_file:
        for chunk in gen:
           lback_output("BACKUP WRITING CHUNK")
           backup_archive_file.write( chunk )

  def _add_to_archive_list(self,path):
     self.archive_list.append(path)
     lback_output("ADDED " + path + " TO ARCHIVE")
  def _pack(self):
    lback_output( "Files have been gathered. Forming archive.." )
    for archive_file in self.archive_list:
      full_path = os.path.join( self.folder, archive_file )
      if not is_writable( full_path ):
	      lback_output("Permissions not set for %s"%( full_path ), type="ERROR" )
      else:
          self.archive.obj.add(full_path, arcname=archive_file ) 
    self.archive.obj.close()
  def _can_add(self, file_path):
       if not self.diff:
           return True
       diff_file = os.path.join( self.diff_backup, file_path)
       lback_output("DIFF CHECKING FILE {}".format(diff_file))
       ## new file added
       if not os.path.exists(diff_file):
           lback_output("DIFF NEW FILE FOUND {}".format(file_path))
           return True
       diff_file_st = os.stat(diff_file)
       backup_file = os.path.join( self.folder, file_path )
       backup_file_st = os.stat(backup_file)
       ## file modified since last backup
       if int(diff_file_st.st_mtime) != int(backup_file_st.st_mtime):
           lback_output("DIFF FILE MODIFIED {}".format(file_path))
           return True
       ## no changes
       return False
  def _folder(self, folder_path):
    folder_list = os.listdir(os.path.join(self.folder, folder_path))
    ##self._add_to_archive_list(folder_path)
    for file_or_folder in folder_list:
        target_path = os.path.join(folder_path, file_or_folder)
        real_path = os.path.join(self.folder, target_path)
        if os.path.isdir( real_path ):
            self._folder( target_path )
        elif os.path.isfile( real_path ):
            self._file( target_path )
  def _file(self, file_path):
    if self._can_add( file_path ):
        self._add_to_archive_list(file_path)

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
       select_cursor.execute("SELECT * FROM backups WHERE name = %s", (name,))
       db_backup = select_cursor.fetchone()
       return BackupObject(db_backup)
  @staticmethod
  def find_by_id( partial_or_full_id ):
       db = lback_db()
       select_cursor =db.cursor()
       select_cursor.execute("SELECT * FROM backups WHERE ID LIKE %s", (partial_or_full_id,))
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


