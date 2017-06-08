import os, os.path
import sys
import shutil
import json
import subprocess
import hashlib
import uuid
from setuptools import setup
from setuptools.command.build_py import build_py
from setuptools.command.install import install


def lback_id(salt=""):
    return hashlib.sha1("{}_{}".format(salt, uuid.uuid4())).hexdigest()



def create_db():
  import MySQLdb
  with open(os.path.join(os.getcwd(), "settings.json"), "r+") as settings_file:
       config = json.loads( settings_file.read() )
  db = config['master']['database']
  connection = MySQLdb.connect(db['host'], db['user'], db['pass'], db['name'])
  cursor = connection.cursor()
  cursor.execute(r"""DROP TABLE IF EXISTS backups""")
  cursor.execute(r"""DROP TABLE IF EXISTS agents""")
  cursor.execute(r"""
     CREATE TABLE backups (
     id VARCHAR(255),
     name VARCHAR(50),
     time DOUBLE,
     folder VARCHAR(255),
     dirname VARCHAR(255),
     size VARCHAR(255),
     encryption_key VARCHAR(255) DEFAULT NULL,
     distribution_strategy VARCHAR(255) DEFAULT "shared",
     shards_total smallint(3)
    ); """)
  cursor.execute(r"""
     CREATE TABLE agents (
     id VARCHAR(255),
     host VARCHAR(50),
     port VARCHAR(5)
    ); """)
  ## add local agent by default
  cursor.execute(r"""INSERT INTO agents(id, host, port) VALUES (%s, %s, %s)""", (lback_id(), "127.0.0.1", "5750",))
  connection.commit()

class installsetup(install):
    def run(self):
      create_db()
      base_dir = "%s/.lback"%(os.getenv("HOME"))
      shutil.rmtree( base_dir )
      os.makedirs( base_dir )
      shutil.copy( "./settings.json", "%s/%s"%( base_dir, "settings.json" ) )
      install.run(self)

def get_version():
  import pkg_resources
  try:
    version = pkg_resources.get_distribution("LinuxOpenSuseBackupTool").version
  except:
    return None
  return version
deps = [
    "mysqlclient==1.3.10",
    "termcolor==1.1.0",
    "pycrypto==2.6.1",
    "enum34==1.1.6",
    "six==1.10.0",
    "protobuf==3.3.0",
    "pyinstaller==3.0"
]


setup(name="LinuxOpenSuseBackupTool",
      version="0.1.0",
      description="Quick and simple backups for linux",
      maintainer="Nadir Hamid",
      maintainer_email="matrix.nad@gmail.com",
      url="https://",
      download_url = "https://pypi.python.org/pypi/",
      license="MIT",
      long_description="",
      packages=["lback", "lback_grpc/lback_grpc"],
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
      setup_requires=deps,
      install_requires=deps,
      cmdclass=dict(install=installsetup))



