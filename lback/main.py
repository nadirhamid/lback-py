""" Backup tool for linux.  This performs ehe needed functionality
behind this specifcation.

Implementors must deciede which 
version to run and on what port. This
file acts as 'both' a client and server
and can be started from the command line
via -c or -s respectively.
"""
"""
guide to commands

NEEDS to work on OpenSUSE with RPM
and compiled in py2exe and p2app

"""

from lback.lib.dal import DAL, Field
import errno
import subprocess
import threading
import datetime
import zipfile
import shutil
import socket
import select
import glob
import time
import json
import uuid
import hashlib
import sys
import os
import re

import zipfile,os.path
from datetime import timedelta
from .runtime import Runtime


if __name__ == '__main__':
  r = Runtime(sys.argv)
