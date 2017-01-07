
from lback.utils import lback_untitled, lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_error, lback_print, lback_id, get_folder_size
from lback.restore import Restore, RestoreException
from lback.backup import Backup, BackupException
from lback.client import Client
from lback.server import Server
from lback.operation_backup import OperationBackup
from lback.operation_restore import OperationRestore
from lback.operation_ls import OperationLs
from lback.operation_rm import OperationRm
from lback.operation_mv import OperationMv
from os import getenv
import glob
import shutil
import argparse
import time
import os
import json
import fnmatch


class Runtime(object):
  def __init__(self, args):
    untitled = lback_untitled()
    parser = argparse.ArgumentParser()
    sub_parser = parser.add_subparsers()
   
     
    backup_parser = sub_parser.add_parser("backup", help="Backup files and folders") 
    backup_parser.add_argument("folder", help="Select a folder", nargs="*")
    backup_parser.add_argument("--name", help="Name for backup", default=untitled)
    backup_parser.add_argument("--remove", action="store_true", help="Remove backup when done", default=False)
    backup_parser.add_argument("--local",default=True, action="store_true") 
    backup_parser.set_defaults(backup=True)


    restore_parser = sub_parser.add_parser("restore", help="Run a restore")
    restore_parser.add_argument("id", help="Select the ID", nargs="*")
    restore_parser.add_argument("--name", help="Filter to a specific name", default=False)
    restore_parser.add_argument("--clean", action="store_true", help="Clean backup on completion", default=False)
    restore_parser.set_defaults(restore=True)

    rm_parser = sub_parser.add_parser("rm", help="Delete existing backup")
    rm_parser.add_argument("id", help="Select the ID", nargs="*")
    rm_parser.add_argument("--name", help="Filter to a specific name", default=False)
    rm_parser.set_defaults(rm=True)

    ls_parser = sub_parser.add_parser("ls", help="List backups")
    ls_parser.set_defaults(ls=True)

    mv_parser = sub_parser.add_parser("mv", help="Move mounted backup")
    mv_parser.add_argument("id", help="Select the ID")
    mv_parser.add_argument("dst", help="Select the Destination")
    mv_parser.set_defaults(mv=True)
    mv_parser.set_defaults(name=False)

    self.args = parser.parse_args()
  def run(self):
    args = self.args
    backup_dir = lback_backup_dir()
    db = lback_db()
    def check_parser(name):
      if  name in dir( args ) and getattr( args, name ):
        return True
      return False
    if check_parser("backup"):
      operation = OperationBackup(args, db)
    if check_parser("restore"):
      operation = OperationRestore(args, db)
    if check_parser("rm"):
      operation = OperationRm(args, db)
    if check_parser("ls"):
      operation = OperationLs(args, db)
    if check_parser("mv"):
      operation = OperationMv(args, db)
    operation.run()
    db.close()

