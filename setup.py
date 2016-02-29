import os, os.path
import sys
import shutil

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

from distutils.command.build_py import build_py

class buildsetup(build_py):
    def find_package_modules(self, package, package_dir):
        """
        Lookup modules to be built before install. Because we
        only use a single source distribution for Python 2 and 3,
        we want to avoid specific modules to be built and deployed
        on Python 2.x. By overriding this method, we filter out
        those modules before distutils process them.
        This is in reference to issue #123.
        """
        modules = build_py.find_package_modules(self, package, package_dir)
        amended_modules = []
        for (package_, module, module_file) in modules:
            if sys.version_info < (3,):
                if module in ['async_websocket', 'tulipserver']:
                    continue
            amended_modules.append((package_, module, module_file))

        return amended_modules
def get_version():
  import pkg_resources
  try:
    version = pkg_resources.get_distribution("LinuxOpenSuseBackupTool").version
  except:
    return None
  return version

def finalizesetup():
	pass
 

setup(name="LinuxOpenSuseBackupTool",
      version="0.1.0",
      description="Quick and simple backups for linux",
      maintainer="Nadir Hamid",
      maintainer_email="matrix.nad@gmail.com",
      url="https://",
      download_url = "https://pypi.python.org/pypi/",
      license="MIT",
      long_description="",
      packages=["lback"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
          'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      cmdclass=dict(build_py=buildsetup))


if sys.argv [1]=="install":
  fpath = '/usr/bin/'
  lpath = '/usr/local/lback/'
  ffpath = '/usr/'
  path = os.getcwd()
  bin_path = path + '/bin/'
  os.chdir(fpath)
  version = get_version()
  current_version_check = "{0}-{1}".format("/usr/local/lback", version)
  if not os.path.isdir( current_version_check ):
      if os.path.isdir("/usr/local/lback/") and version:
       
        ##found current
        print "Found current LBack moving to {0}-{1}".format("/usr/local/lback", version)
        os.mkdir("{0}-{1}/".format("/usr/local/lback",version))
        os.system("mv {0} {1}-{2}/".format("/usr/local/lback", "/usr/local/lback", version))
        #files_in_current = os.listdir("/usr/local/lback")
        #for i in files_in_current:
        #  os.remove("/usr/local/lback/"+i)
        #os.removedirs("/usr/local/lback/")



  """ remove all previous files """
  rem_files = [ 
      fpath+'/lback.py',
      fpath+'/dal.py',
      fpath+'/odict.py',
      fpath+'/lbackd',
      fpath+'/lback-client',
      fpath+'/lback-server',
      ffpath+'/settings.json',
      ffpath+'/profiler.json',
      lpath+'/settings.json',
      ffpath+'/profiler.json'
     '/etc/init.d/lback'
   ]
  known_files = [
       fpath+'/'+'lback.py',
        fpath+'/'+'dal.py',
        fpath+'/lback',
        fpath+'/lback-server',
        fpath+'/lback-client',
        fpath+'/lback-jit',
        fpath+'/lback-profiler'
  ]
  for i in known_files + rem_files:
    if os.path.isfile(i) or os.path.islink(i):
      os.remove(  i )

  os.system('sudo ln -s ' + bin_path + "lback.py")
  os.system('sudo ln -s ' + bin_path + "dal.py")
  os.system('sudo ln -s ' + bin_path + "odict.py")
  os.system('sudo ln -s ' + bin_path + "lback")
  os.system('sudo ln -s ' + bin_path + "lback-client")
  os.system('sudo ln -s ' + bin_path + "lback-server")
  os.system('sudo ln -s ' + bin_path + "lback-profiler")
  os.system('sudo ln -s ' + bin_path + "lback-jit")
  if os.path.isdir(lpath):
    shutil.rmtree(lpath)
    os.mkdir(lpath)
  else:
    os.mkdir(lpath)

  os.chdir(lpath)
  os.system('sudo ln -s ' + path + "/backups")
  os.system('sudo ln -s ' + path + "/settings.json")
  os.system('sudo ln -s ' + path + "/profiles.json")
  os.chdir(path)
  os.system('sudo cp ' + path + '/service /etc/init.d/lback')
  os.system('sudo chkconfig --add lback')
  os.system('sudo chkconfig lback on')
  os.chdir(path)
  print """
  Installed the following commands:
  lback (same as lback-client)
  lback-client
  lback-server
  lback-profiler
  lback-jit
  """
