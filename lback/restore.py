import shutil
import tempfile
import os
from .utils import untar, lback_backup_dir, lback_backup_ext, lback_backup_path, lback_backup_chunked_file, lback_decrypt, lback_id_temp, lback_backup, lback_temp_file, lback_error

class Restore(object):
  def __init__(self, backup_id, folder='./', run=True):
    self.archive = lback_backup_path( backup_id,suffix="R" )
    self.backup_id = backup_id
    self.folder = folder
    self.do_run = run
  def run(self, local=False):
    if not self.do_run:
       return

    backup_dir = lback_backup_dir()
    db_backup = lback_backup(self.backup_id)
    temp_file = lback_temp_file()
    def run_decryptor():
        with open(self.archive, "rb") as in_file, temp_file as out_file:
           lback_decrypt(in_file, out_file, db_backup.encryption_key)
        shutil.move(temp_file.name, self.archive)

    if db_backup.encryption_key:
        run_decryptor()

    untar(self.archive, self.folder)
    os.remove( self.archive )
  def run_chunked(self, iterator):
     db_backup = lback_backup(self.backup_id)
     def rollback():
         ##os.remove( self.archive )
         pass
     def verify_chunk():
        if not chunk:
           raise RestoreException("Unable to restore. Receiving from stream failed")
     try:
         with open( self.archive, "a+" ) as restore_backup_file:
             for chunk in iterator:
                 verify_chunk()
                 restore_backup_file.write( chunk )
             self.run()
     except Exception,ex:
         rollback()
         lback_error( ex )
         raise ex

class RestoreException(Exception):
     pass

