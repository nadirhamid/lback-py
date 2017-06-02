from .utils import lback_untitled, lback_backup_dir, lback_backup_ext, lback_db, lback_output, lback_error, lback_print, lback_id,lback_settings, get_folder_size
from .restore import Restore, RestoreException
from .backup import Backup, BackupException
from .operation_backup import OperationBackup
from .operation_modify import OperationModify
from .operation_restore import OperationRestore
from .operation_ls import OperationLs
from .operation_rm import OperationRm
from .operation_mv import OperationMv
from .operation_relocate import OperationRelocate
from .operation_agent_add import OperationAgentAdd
from .operation_agent_rm import OperationAgentRm
from .operation_agent_ls import OperationAgentLs


from lback_grpc.client import Client
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
    backup_parser.add_argument("--diff", help="Runs a differential backup")
    backup_parser.add_argument("--remove", action="store_true", help="Remove backup when done", default=False)
    backup_parser.add_argument("--distribution-strategy", help="Defines the distribution strategy for the backup", default="shared")
    backup_parser.add_argument("--local",default=True, action="store_true") 
    backup_parser.add_argument("--encryption-key", help="Set an encryption key for the backup")
    backup_parser.set_defaults(backup=True)

    modify_parser = sub_parser.add_parser("modify", help="Make modifications to a backup")
    modify_parser.add_argument("id", help="Select the ID", nargs="*")
    modify_parser.add_argument("--distribution-strategy", help="Defines the distribution strategy for the backup", default="shared")
    modify_parser.set_defaults(modify=True)

    restore_parser = sub_parser.add_parser("restore", help="Run a restore")
    restore_parser.add_argument("id", help="Select the ID", nargs="*")
    restore_parser.add_argument("--name", help="Filter to a specific name", default=False)
    restore_parser.add_argument("--clean", action="store_true", help="Clean backup on completion", default=False)
    restore_parser.add_argument("--folder", help="Restore to specific path", default=False)
    restore_parser.set_defaults(restore=True)

    rm_parser = sub_parser.add_parser("rm", help="Delete existing backup")
    rm_parser.add_argument("id", help="Select the ID", nargs="*")
    rm_parser.add_argument("--name", help="Filter to a specific name", default=False)
    rm_parser.add_argument("--all", help="Remove all copies", default=True, action="store_true")
    rm_parser.add_argument("--target", help="Remove from a specific agent", default=False)
    rm_parser.set_defaults(rm=True)

    ls_parser = sub_parser.add_parser("ls", help="List backups")
    ls_parser.set_defaults(ls=True)

    mv_parser = sub_parser.add_parser("mv", help="Move mounted backup")
    mv_parser.add_argument("id", help="Select the ID")
    mv_parser.add_argument("dst", help="Select the Destination")
    mv_parser.set_defaults(mv=True)
    mv_parser.set_defaults(name=False)

    relocate_parser = sub_parser.add_parser("mv", help="Relocate a certain backup")
    relocate_parser.add_argument("id", help="Select the ID")
    relocate_parser.add_argument("src", help="Select the Source")
    relocate_parser.add_argument("dst", help="Select the Dest")
    relocate_parser.set_defaults(relocate=True)
    relocate_parser.set_defaults(name=False)

    agent_add_parser = sub_parser.add_parser("agent-add", help="ADD, DELETE agents")
    agent_add_parser.add_argument("host", help="host of agent")
    agent_add_parser.add_argument("port", help="port of agent")
    agent_add_parser.set_defaults(agent_add=True)
    agent_add_parser.set_defaults(name=False)

    agent_rm_parser = sub_parser.add_parser("agent-rm", help="ADD, DELETE agents")
    agent_rm_parser.add_argument("id", help="ID of agent")
    agent_rm_parser.set_defaults(agent_rm=True)
    agent_rm_parser.set_defaults(name=False)


    agent_ls_parser = sub_parser.add_parser("agent-ls", help="ADD, DELETE agents")
    agent_ls_parser.set_defaults(agent_ls=True)
    agent_ls_parser.set_defaults(name=False)

    self.args = parser.parse_args()
  def run(self):
    args = self.args
    backup_dir = lback_backup_dir()
    db = lback_db()
    def check_parser(name):
      if  name in dir( args ) and getattr( args, name ):
        return True
      return False
    client = Client()
    operation_args = [ args, client, db ]
    if check_parser("backup"):
      operation = OperationBackup(*operation_args)
    if check_parser("modify"):
      operation = OperationModify(*operation_args)
    if check_parser("restore"):
      operation = OperationRestore(*operation_args)
    if check_parser("rm"):
      operation = OperationRm(*operation_args)
    if check_parser("ls"):
      operation = OperationLs(*operation_args)
    if check_parser("mv"):
      operation = OperationMv(*operation_args)
    if check_parser("relocate"):
      operation = OperationRelocate(*operation_args)
    if check_parser("agent_add"):
      operation = OperationAgentAdd(*operation_args)
    if check_parser("agent_rm"):
      operation = OperationAgentRm(*operation_args)
    if check_parser("agent_ls"):
      operation = OperationAgentLs(*operation_args)
    operation.run()
    db.close()
