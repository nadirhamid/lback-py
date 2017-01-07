
import glob
import fnmatch
import os
from .utils import lback_db, lback_output

class Operation( object ):
  def __init__( self, args, db ):
      self.args = args 
      self.db = db
      self.globs = self._get_all_globs()
  def _get_all_globs(self):
    db = self.db
    full_list = []
    for folder in self.args.id:
       current_dir = os.getcwd()
       glob_entries = []
       select_cursor = db.cursor().execute("SELECT * FROM  backups WHERE dirname = ?", (current_dir,))
       backup = select_cursor.fetchone()
       while backup:
         filename = backup.get_filename()
         if fnmatch.fnmatch(filename, folder):
           glob_entries = glob_entries + [filename]
         backup = select_cursor.fetchone()
       if len( glob_entries ) > 0:
         full_list = full_list + glob_entries
       else:
         full_list.append( folder )
    return full_list
  def run(self):
      map( lambda folder_or_id: self._run( folder_or_id ), self.globs )
class OperationNoArgs(object):
   def __init__( self, args, db ):
     self.args = args
     self.db = db
   def run(self):
     self._run()
