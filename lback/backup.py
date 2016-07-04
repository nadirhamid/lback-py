
import zipfile
import os
from lback.utils import lback_backup_dir,lback_output

class Backup(object):
  def __init__(self, record_id, folder='./', client=True):
    backupDir = lback_backup_dir()
    if not folder[len(folder) - 1] == "/":
      folder += "/"

    self.things = []
    self.record_id = record_id
    if client:
      self.zip = zipfile.ZipFile(backupDir + record_id + '.zip', 'w', zipfile.ZIP_DEFLATED)
    self.status = 0
    self.folder = folder

  def raw(self, content):
    
    try:
      from cStringIO import StringIO
    except:
      from StringIO import StringIO

    #fp = StringIO(content)
    #zfp = zipfile.ZipFile(fp, "w")
    #f = open("./backups/server.zip", "w+")
    f = open(self.get(), "w+")
    f.write(content)
    f.close()
    
    self.status = 1
    
  def run(self, pack=True):
    l = os.listdir(self.folder)
    #self.zip.write(self.folder)
    #self.things.append(self.folder)
    folders = [self._folder(i, self.folder) for i in l if os.path.isdir(self.folder + i)]
    files = [self._file(i, self.folder) for i in l if os.path.isfile(self.folder + i)]
    #self.things = glob.glob(self.folder + "*")
    if pack:
      self.pack()
    
  def get(self):
    return backupDir + self.record_id + '.zip'
    
  def pack(self):
    lback_output( "Files have been gathered. Forming archive.." )
    for i in self.things:
      self.zip.write(i, os.path.relpath(i, self.folder))
    lback_output( "Files found: ")
    lback_output(self.things)
    #Util().zip(self.folder, self.get())
    self.zip.close()
    self.status = 1
    

  def _folder(self, anchor, prefix=''):
    l = os.listdir(prefix + anchor)

    folders = [self._folder(i, prefix + anchor + "/") for i in l if os.path.isdir(prefix + anchor + "/" + i)]
    files = [self._file(i, prefix + anchor + "/") for i in l if os.path.isfile(prefix + anchor + "/" + i)]
    self.things.append(prefix + anchor)

    return prefix + anchor
    
  def _file(self, anchor, prefix=''):
    lback_output("added => " + prefix + anchor)
    self.things.append(prefix + anchor)
    
    return prefix + anchor
  

