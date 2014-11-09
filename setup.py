import os, os.path
from glob import iglob
import sys

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

def finalizesetup():
	pass
 

setup(name="LinuxOpenSuseBackupTool",
      version="0.1.0",
      description="",
      maintainer="",
      maintainer_email="",
      url="https://",
      download_url = "https://pypi.python.org/pypi/",
      license="MIT",
      long_description="",
      packages=["lback"],
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Framework :: CherryPy',
          'Intended Audience :: Developers',
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
ffpath = '/usr/'
path = os.getcwd()
bin_path = path + '/bin/'
os.chdir(fpath)
os.system('sudo ln -s ' + path + "/storage.db > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "core.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "dal.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "odict.py > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-client > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-client > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-server > /dev/null 2>&1 &")
os.system('sudo ln -s ' + bin_path + "lback-profiler > /dev/null 2>&1 &")
os.system('sudo ln -s ' + path + "/backups > /dev/null 2>&1 &")
os.chdir(ffpath)
os.system('sudo ln -s ' + path + "/settings.json > /dev/null 2>&1 &")
os.system('sudo ln -s ' + path + "/profiles.json > /dev/null 2>&1 &")
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
