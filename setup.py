import os, os.path
import sys
import shutil
from lback.lib.dal import DAL,Field
import json
import subprocess



try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

from distutils.command.build_py import build_py
from distutils.command.install import install

class installsetup(install):
    def run(self):
      version = get_version()
      cwd = os.getcwd()
      os.remove(cwd+"/db.sql")
      db = open(cwd+"/db.sql","w+")
      db.close()
     
      if os.path.isdir("/usr/local/lback"):
          shutil.rmtree("/usr/local/lback")

      os.makedirs("/usr/local/lback")
      os.makedirs("/usr/local/lback/backups/")
      links = [
            (cwd+"/lback/main.py", "/usr/bin/lback.py"),
            (cwd+"/lback/dal.py", "/usr/bin/dal.py"),
            (cwd+"/lback/odict.py", "/usr/bin/odict.py"),
            (cwd+"/bin/lback", "/usr/bin/lback"),
            (cwd+"/bin/lback-client", "/usr/bin/lback-client"),
            (cwd+"/bin/lback-server", "/usr/bin/lback-server"),
            (cwd+"/settings.json", "/usr/local/lback/settings.json"),
            (cwd+"/profiles.json", "/usr/local/lback/profiles.json"),
            (cwd+"/db.sql", "/usr/local/lback/db.sql")
        ]
      for i in links:
         subprocess.Popen(['ln', '-s', i[0], i[1]])
      install.run(self)

def get_version():
  import pkg_resources
  try:
    version = pkg_resources.get_distribution("LinuxOpenSuseBackupTool").version
  except:
    return None
  return version

def get_settings():
  file = open("/usr/local/lback/settings.json", "r")
  jsonobj = json.loads(file.read())
  file.close()
  return jsonobj
   

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
      packages=["lback", "lback/lib/", "lback/rpc/"],
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
      cmdclass=dict(install=installsetup))



