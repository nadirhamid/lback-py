

import tarfile 
import os
from lback.utils import lback_backup_dir,lback_backup_ext,lback_output, Util, is_writable
from lback.archive import Archive

class Backup(object):
  def __init__(self, backup_id, folder='./', client=True, state=None):
    backup_dir = lback_backup_dir()
    if not folder[len(folder) - 1] == "/":
      folder += "/"

    self.things = []
    self.backup_id = backup_id
    if client:
      self.archive = Archive(backup_dir + backup_id+lback_backup_ext(), "w")
    self.folder = folder
    self.progress= 0
    self.state = state

  def raw(self, content):
    
    try:
      from cStringIO import StringIO
    except:
      from StringIO import StringIO

    #fp = StringIO(content)
    #zfp = archivefile.ZipFile(fp, "w")
    #f = open("./backups/server.archive", "w+")
    f = open(self.get(), "w+")
    f.write(content)
    f.close()
    
    
  def run(self, pack=True):
    l = os.listdir(self.folder)
    #self.archive.write(self.folder)
    #self.things.append(self.folder)
    folders = [self._folder(i, self.folder) for i in l if os.path.isdir(self.folder + i)]
    files = [self._file(i, self.folder) for i in l if os.path.isfile(self.folder + i)]
    #self.things = glob.glob(self.folder + "*")
    if pack:
      self.pack()
    
  def get(self):
    return backup_dir + self.backup_id + '.archive'
    
  def pack(self):
    lback_output( "Files have been gathered. Forming archive.." )
    for i in self.things:
      as_file = os.path.relpath(i, self.folder)
      if not is_writable( i ):
	  lback_output("Permissions not set for %s"%( i ), type="ERROR" )
      else:
          self.archive.obj.add(i, arcname=as_file ) 

    #Util().archive(self.folder, self.get())
    self.archive.obj.close()

  def _folder(self, anchor, prefix=''):
    l = os.listdir(prefix + anchor)

    folders = [self._folder(i, prefix + anchor + "/") for i in l if os.path.isdir(prefix + anchor + "/" + i)]
    files = [self._file(i, prefix + anchor + "/") for i in l if os.path.isfile(prefix + anchor + "/" + i)]
    self.things.append(prefix + anchor)

    return prefix + anchor
    
  def _file(self, anchor, prefix=''):
    lback_output("Added \"" + prefix + anchor + "\"")
    self.things.append(prefix + anchor)

    return prefix + anchor
class BackupException( Exception ):
     pass

