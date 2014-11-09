import os, os.path
from glob import iglob
import sys

try:
	from setuptools import setup
except ImportError:
	from distutils.lback import setup

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

fpath = '/usr/bin/'
lpath = '/usr/local/lback/'
ffpath = '/usr/'
path = os.getcwd()
bin_path = path + '/bin/'
os.chdir(fpath)
""" remove all previous files """
os.system('sudo rm ' + path + "/storage.db > /dev/null 2>&1 &")
os.system('sudo rm ' + path + "/lback.py > /dev/null 2>&1 &")
os.system('sudo rm ' + path + "/odict.py > /dev/null 2>&1 &")
os.system('sudo rm ' + path + "/dal.py > /dev/null 2>&1 &")
os.system('sudo rm ' + path + "/lback* > /dev/null 2>&1 &")
os.system('sudo rm /etc/init.d/lback > /dev/null 2>&1 &')
os.system('sudo rm ' + ffpath + "settings.json > /dev/null 2>&1 &")
os.system('sudo rm ' + ffpath + "profiler.json > /dev/null 2>&1 &")
os.system('sudo rm ' + ffpath + "profiler.json > /dev/null 2>&1 &")
if os.path.isdir(lpath):
	os.system('sudo rm ' + lpath + "/* > /dev/null 2>&1 &")
	os.system('sudo rm -rf ' + lpath + "/ > /dev/null 2>&1 &")
os.system('sudo rm ' + lpath + "settings.json > /dev/null 2>&1 &")
os.system('sudo rm ' + lpath + "profiler.json > /dev/null 2>&1 &")

os.system('sudo ln -s ' + path + "/storage.db > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "dal.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "odict.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-client > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-client > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-server > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-profiler > /dev/null 2>&1 &")


if not os.path.isdir(lpath):
	os.mkdir(lpath)

os.chdir(lpath)
os.system('sudo ln -s ' + path + "backups > /dev/null 2>&1 &")
os.system('sudo ln -s ' + path + "settings.json > /dev/null 2>&1 &")
os.system('sudo ln -s ' + path + "profiles.json > /dev/null 2>&1 &")
os.chdir(path)
os.system('sudo cp ' + path + '/service /etc/init.d/lback > /dev/null 2>&1 &')
os.system('sudo chkconfig --add lback')
os.system('sudo chkconfig lback on')
os.chdir(path)
print """
Installed the following commands:
lback (same as lback-client)
lback-client
lback-server
lback-profiler
"""
