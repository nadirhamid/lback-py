
import glob
import fnmatch
import os
from .utils import lback_db, lback_output

class Operation( object ):
  def __init__( self, args, client, db ):
      self.args = args 
      self.client= client
      self.db = db
      self.globs = self._get_all_globs()
  def _get_all_globs(self):
    db = self.db
    full_list = []
    for unregistered_folder in self.args.id:
       current_dir = os.getcwd()
       glob_entries = []
       select_cursor = db.cursor().execute("SELECT * FROM  backups WHERE dirname = ?", (current_dir,))
       backup = select_cursor.fetchone()
       while backup:
         filename = backup.get_filename()
	 id = backup.id
         if fnmatch.fnmatch(filename, unregistered_folder):
           glob_entries = glob_entries + [id]
         backup = select_cursor.fetchone()
       if len( glob_entries ) > 0:
         full_list = full_list + glob_entries
       else:
         full_list.append( unregistered_folder )
    return full_list
  def _run(self):
     self.client._run( self )
  def run(self):
      map( lambda folder_or_id: self._run( folder_or_id ), self.globs )

class OperationNoGlobs(object):
   def __init__( self, args, client, db ):
     self.args = args
     self.client = client
     self.db = db
   def run(self):
     self._run()
