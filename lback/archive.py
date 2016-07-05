
import tarfile

class ArchiveTar(object):
   
   def __init__(self,name=""):
	 self.obj = tarfile.TarFile.open(name+".tar.gz", "w")
   def write(self,file, path):
	 self.obj.add(file, arcname=path)
   def close(self):
	 self.obj.close()

	  

class Archive(object):
  def __init__( self, name, mode ):
	 self.obj = ArchiveTar( name=name )

