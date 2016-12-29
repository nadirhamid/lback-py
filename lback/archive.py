
import tarfile


class Archive(object):
  def __init__( self, name, mode ):
	 self.obj = tarfile.TarFile.open( name, mode )

