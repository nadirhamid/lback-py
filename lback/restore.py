
from .utils import untar, lback_backup_dir, lback_backup_ext, lback_backup_path, lback_backup_chunked_file

class Restore(object):
  def __init__(self, backup_id, folder='./'):
    self.archive = lback_backup_path( backup_id )
    self.backup_id = backup_id
    self.folder = folder
  def run(self, local=False):
    backup_dir = lback_backup_dir()
    untar(self.archive, self.folder)
  def read_chunked(self):
    for chunk in lback_backup_chunked_file(self.backup_id):
	    yield chunk
  def run_chunked(self, iterator):
     def rollback():
         os.remove( self.archive )
     def verify_chunk(chunk):
        if not chunk:
           raise RestoreException("Unable to restore. Receiving from stream failed")
     try:
         with open( self.archive, "a+" ) as restore_backup_file:
             for chunk in iterator:
                 verify_chunk( chunk )
                 restore_backup_file.write( chunk )
             self.run()
     except Exception,ex:
         rollback()
         raise ex

class RestoreException(Exception):
     pass

