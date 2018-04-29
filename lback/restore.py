import shutil
import tempfile
import os
from .utils import untar, lback_backup_dir, lback_backup_ext, lback_backup_path, lback_backup_chunked_file, lback_decrypt, lback_id_temp, lback_backup, lback_temp_file, lback_error
from .basic_wrapper import BasicWrapper

class Restore(BasicWrapper):
  SUFFIX = "R"
  def __init__(self, backup_id, folder='./', run=True, encryption_key=None, compression=None):
    self.id = backup_id
    self.archive = self.get_file()
    self.folder = folder
    self.encryption_key = encryption_key
    self.compression= compression
    self.do_run = run

  def run(self, local=False):
    if not self.do_run:
       return

    backup_dir = lback_backup_dir()
    temp_file = lback_temp_file()
    def run_decryptor():
        with open(self.archive, "rb") as in_file, open(temp_file.name, "wb") as out_file:
           lback_decrypt(in_file, out_file, self.encryption_key)
        shutil.move(temp_file.name, self.archive)
    def run_decompression():

        with open(self.archive, "rb") as in_file, open(temp_file.name, "wb") as out_file:
               lback_decompress(in_file, out_file)
        shutil.move(temp_file.name, self.archive)

    if self.encryption_key:
        run_decryptor()
    if self.compression:
        run_decompression()

    untar(self.archive, self.folder)
    os.remove( self.archive )
  def run_chunked(self, iterator):
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

