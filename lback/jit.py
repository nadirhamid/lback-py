import os
from lback.utils import Util
"""
Just in time backups
"""
class JIT(object):
  def __init__(self, db, db_table='backups'):
    self.db = db
    self.db_table = db_table

  def check(self, record=''):
    while True:
      if record:
        backups = self.db(self.db[self.db_table].uid == record).select()
      else:
        backups = self.db(self.db[self.db_table].jit == True).select()

      for i in backups:
        initial_time = float(i.time)
        local = i.local
        uid = i.uid
        folder = i.folder
        cpath = os.getcwd()
        
        files = os.listdir(folder)

        b = Backup(None, folder, False)
        b.run(False) ## dont actually run.. yet
        
        for f in b.things:
          if os.path.getmtime(f) > initial_time:
            Output.show("Running JIT Backup file was edited..")
            """ time for a backup """
            os.chdir(cpath)
            bkp = Backup(uid, folder)
            bkp.run()

            if bkp.status == 1:
              size = str(Util().getFolderSize(folder))
              self.db(self.db[self.db_table].uid == uid).update(time = time.time(), size=size)
              self.db.commit()

              break


