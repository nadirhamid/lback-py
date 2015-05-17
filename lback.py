"""
Backup tool for linux.
This performs the needed functionality
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

from dal import DAL, Field
import errno
import subprocess
import threading
import zipfile
import shutil
import socket
import select
import glob
import time
import json
import uuid
import sys
import os
import re

import zipfile,os.path

try:
	import boto
	from boto.s3.key import Key
	from boto.s3.connection import S3Connection
except:
	## no boto
	pass

LOCAL_BACKUP_DIR = '/usr/local/lback/backups/'

class Backup(object):
	def __init__(self, record_id, folder='./', client=True):
		global LOCAL_BACKUP_DIR
		if not folder[len(folder) - 1] == "/":
			folder += "/"

		self.things = []
		self.record_id = record_id
		if client:
			self.zip = zipfile.ZipFile(LOCAL_BACKUP_DIR + record_id + '.zip', 'w', zipfile.ZIP_DEFLATED)
		self.status = 0
		self.folder = folder

	def raw(self, content):
		global LOCAL_BACKUP_DIR
		
		try:
			from cStringIO import StringIO
		except:
			from StringIO import StringIO

		#fp = StringIO(content)
		#zfp = zipfile.ZipFile(fp, "w")
		#f = open("./backups/server.zip", "w+")
		f = open(self.get(), "w+")
		f.write(content)
		f.close()
		
		self.status = 1
		
	def run(self, pack=True):
		l = os.listdir(self.folder)
		#self.zip.write(self.folder)
		#self.things.append(self.folder)
		folders = [self._folder(i, self.folder) for i in l if os.path.isdir(self.folder + i)]
		files = [self._file(i, self.folder) for i in l if os.path.isfile(self.folder + i)]
		#self.things = glob.glob(self.folder + "*")
                if pack:
		     self.pack()
		
	def get(self):
		return LOCAL_BACKUP_DIR + self.record_id + '.zip'
		
	def pack(self):
		print "Files have been gathered. Forming archive.."
		for i in self.things:
			self.zip.write(i, os.path.relpath(i, self.folder))
		print "Files found: "
		print self.things
		#Util().zip(self.folder, self.get())
		self.zip.close()
		self.status = 1
		

	def _folder(self, anchor, prefix=''):
		l = os.listdir(prefix + anchor)

		folders = [self._folder(i, prefix + anchor + "/") for i in l if os.path.isdir(prefix + anchor + "/" + i)]
		files = [self._file(i, prefix + anchor + "/") for i in l if os.path.isfile(prefix + anchor + "/" + i)]
		self.things.append(prefix + anchor)

		return prefix + anchor
		
	def _file(self, anchor, prefix=''):
		print "added => " + prefix + anchor
		self.things.append(prefix + anchor)
		
		return prefix + anchor
	
class Restore(object):
	def __init__(self, zip_file_loc, folder='./', clean=False):
		self.zip_file,self.status = zip_file_loc, 0
		self.clean = clean
		self.folder = folder
	def run(self, local=False, uid=''):
		global LOCAL_BACKUP_DIR
		if local:
			self.zip_file = LOCAL_BACKUP_DIR + uid + ".zip"

		if self.clean:
			shutil.rmtree(self.folder)
			Util().unzip(self.zip_file, self.folder)
		else:
			Util().unzip(self.zip_file, self.folder)		
		self.status = 1

import time,socket

def recvall(the_socket,timeout=''):
    #setup to use non-blocking sockets
    #if no data arrives it assumes transaction is done
    #recv() returns a string
    the_socket.setblocking(0)
    total_data=[];data=''
    begin=time.time()

    if not timeout:
        timeout=1
    while 1:
        #if you got some data, then break after wait sec
        if total_data and time.time()-begin>timeout:
            break
        #if you got no data at all, wait a little longer
        elif time.time()-begin>timeout*2:
            break
        wait=0
        try:
            data=the_socket.recv(4096)
            if data:
                total_data.append(data)
                begin=time.time()
                data='';wait=0
            else:
                time.sleep(0.1)
        except:
            pass
        #When a recv returns 0 bytes, other side has closed
    result=''.join(total_data)
    return result
	
class Server(object):
	def __init__(self, port, ip, db, table):
		self.status = 0
		self.ip = ip
		self.db = db
		self.port = port
		self.db_table = table
	
	def cmd(self):
		pass
		
	def run(self):
		global LOCAL_BACKUP_DIR
		s = socket.socket()         # Create a socket object
		self.port = int(self.port)              # Reserve a port for your service.
		s.bind((self.ip, self.port))        # Bind to the port
		#s.setblocking(0)

		s.listen(1)                 # Now wait for client connection.
		while True:
		   c, addr = s.accept()     # Establish connection with client.
		   #print connections
		   print 'Got connection from', addr
		   
		   message = recvall(c)

		   """
		   what command is this?
		   """
		   if len(re.findall(r'RESTORE', message)) > 0:
				print "Running 'RESTORE'"
				uid = False
				uid = re.findall('UID:\s+"([\w\d\-\.]+)",', message)[0]

				version = re.findall('VERSION:\s+"([\w\d\-]+)",', message)[0]
				if not uid:
					continue

				if version.lower() == 'latest':
					r = self.db(((self.db[self.db_table].uid == uid) | 
						     (self.db[self.db_table].name == uid) |  
						     (self.db[self.db_table].folder == uid))).select().last()

				elif version.lower() == 'oldest':
					r = self.db(((self.db[self.db_table].uid == uid) | 
						     (self.db[self.db_table].name == uid) |  
						     (self.db[self.db_table].folder == uid))).select().first()

				else:
					r = self.db(((self.db[self.db_table].uid == uid) | 
						     (self.db[self.db_table].name == uid) |  
						     (self.db[self.db_table].folder == uid)) &
						     (self.db[self.db_table].version == version)).select().first()
				if not r:
					print "SERVER couldn\'t find backup.."
					continue
				else:
					uid = row.uid


					
				fi = open(LOCAL_BACKUP_DIR + uid + '.zip', 'r+')
				contents = fi.read()
				fi.close()
				fullmsg = "SUCCESS" + "\n" + "CONTENTS: " + contents
				it = 0
				while True:
					try:
						tmsg = fullmsg[it:it+2048]
						if tmsg != "":
							c.send(tmsg)
						else:
							break
						it += 2048
					except socket.error, e:
						if e.errno != errno.EAGAIN:
							raise e
							
						select.select([], [c], [])
					
				print "Restore backup fetched."
				print "Sending to client.."
				print "Transaction ID: " + uid
				c.close()
		
				
					
		   if len(re.findall(r'BACKUP', message)) > 0:
				print "Running 'BACKUP'"
				uid = 0
				contents = 0
				folder = 0
				name = "N/A"
				size = 0
				c.sendall("SUCCESS")
				try:
					uid = re.findall('UID:\s+"([\w\d\-]+)",', message)[0]
				except:
					pass

				try:
					name = re.findall('NAME:\s+(.*)', message)[0]
				except:
					pass
					
				try:
					size = re.findall('SIZE:\s+([\d]+),', message)[0]
				except:
					pass

				try:
					version = re.findall('VERSION:\s+([\d\.]+),', message)[0]
				except:
					pass

				try:
					version = re.findall('JIT:\s+([\d\.]+),', message)[0]
				except:
					pass


				try:
					folder = re.findall('FOLDER:\s+"([^^]+)",', message)[0]
				except:
					pass
					
				try:
					contents = re.sub('.*CONTENTS:\s+', '', message)
					contents = re.sub('BACKUP.*\n', '', contents)
				except:
					pass

				if not uid:
					continue

				if not contents:
					continue

				bkp = Backup(uid, folder, False)
				bkp.raw(contents)
				
				if bkp.status:
					""" backed up, send back message """
					self.db[self.db_table].insert(uid=uid, time=time.time(), folder=folder, size=size, local=False, name=name, jit=True, version=version)
					self.db.commit()
					c.sendall("SUCCESS")
					print "Backup complete."
					print "Transaction ID: " + uid
					
				c.close()
		   #c.send('Thank you for connecting')
		   
		   
				
		pass
	
class Output(object):
	def __init__(self):
		pass
	def show(self,msg,times=0):
		if times == 0:
			print(msg)
		else:
			print(msg + "\n" * times)
	
class Client(object):
	def __init__(self, ip, port, server=dict()):
		self.status = 0
		self.server = server
	
	def run(self, cmd='BACKUP', folder=None, uid='', contents='',name='',version='1.0.0',size=0, jit=False):
		s = socket.socket()
		size = str(size)
		#s.setblocking(0)
		s.connect((self.server['ip'], int(self.server['port'])))
		smessage = cmd + ', ' + 'UID: "' + uid + '", ' + 'FOLDER: "' + folder + '", '  + 'JIT: "' + str(jit) +  '", ' +  "SIZE: " + size + ', ' + "VERSION: " + version + ', ' + "NAME: " + name + "\nCONTENTS: " + contents
		s.sendall(smessage)
		out = False
		if cmd == 'BACKUP':
			self.m = recvall(s)
		else:
			self.m = ""
			while True:
				if out:
					break
				try:
					m = s.recv(2048)
					if not m:
						break
					if m == "":
						out = True
						break
					if m != "" or m:
						self.m += m
					
				except socket.error, e:
					print "??"
					if e.errno != errno.EAGAIN:
						raise e
						
					select.select([s], [], [])
					
		try:
			if len(re.findall("CONTENTS:\s+", self.m)) > 0:
				self.m = re.sub('SUCCESS.*\n', '', self.m)
				self.m = re.sub(".*CONTENTS:\s+", "", self.m)
		except:
			pass
			
		s.close()
		self.status = 1
	
	def get(self):
		return self.m
	
	def send(self, data):
		pass
		
	def receive(self, data):
		pass
	
class Record(object):
	def __init__(self):
		pass
	def generate(self):
		return uuid.uuid4().__str__()


"""
Just in time backups
"""
class JIT(object):
	def __init__(self, db, db_table):
		self.db = db
		self.db_table = db_table

	def check(self, record=''):
		while True:
			if record:
				backups = self.db(self.db[self.db_table].uid == record).select()
			else:
				backups = self.db(self.db[self.db_table].jit == True).select()

			for i in backups:
				initial_time = float(i.time)
				local = i.local
				uid = i.uid
                                folder = i.folder
                                cpath = os.getcwd()
				
				files = os.listdir(folder)

				b = Backup(None, folder, False)
				b.run(False) ## dont actually run.. yet
				
				for f in b.things:
					if os.path.getmtime(f) > initial_time:
						print "Running JIT Backup file was edited.."
						""" time for a backup """
                                                os.chdir(cpath)
						bkp = Backup(uid, folder)
						bkp.run()

						if bkp.status == 1:
							size = str(Util().getFolderSize(folder))
							self.db(self.db[self.db_table].uid == uid).update(time = time.time(), size=size)
							self.db.commit()

							break

"""
Profile based backups
"""
class Profiler(object):
	def __init__(self,profiles,server_ip,server_port,ip,port,db,db_table):
		self.profiles = profiles
		self.server_ip = server_ip
		self.server_port = server_port
		self.ip = ip
		self.port = port
		self.db = db
		self.db_table = db_table
		self.o = Output()
	def run(self):
		client = Client(self.port, self.ip, dict(ip=self.server_ip, port=self.server_port))
		
		while True:
			now = int(time.time())
			for i in self.profiles:
				if not os.path.isdir(i['folder']):
					continue
					
				size = str(Util().getFolderSize(i['folder']))
				name = "N/A"
				if 'name' in i.keys():
					name = i['name']
					
				c = self.db((self.db[self.db_table].name == name) & (self.db[self.db_table].folder == i['folder'])).count()
				if c > 0:
					continue
		
				if int(i['time']) >= now:
					uid = Record().generate()
					bkp = Backup(uid, i['folder'])
					bkp.run()

					if bkp.status == 1:
						self.db[self.db_table].insert(uid=uid, time=time.time(), folder=i['folder'], local=i['local'],name=name,size=size)
						self.db.commit()
						if i['local']:
							self.o.show("Backup Ok -- Now saving to disk")
							self.o.show("Local Backup has been successfully stored")
							
						else:
							fc = open(bkp.get(), "r+").read()
							client.run('BACKUP', i['folder'], uid, fc,name,size)
							if client.status:
								self.o.show("Backup Ok -- Now transferring to server")
								
								fp = client.get()
								if len(re.findall("SUCCESS", fp)) > 0:
									self.o.show("Remote Backup has been successfully transferred")
									
									os.remove(bkp.get())
								else:
									self.o.show("Something went wrong on the server.. couldnt back that folder. Reverting changes")
							else:
								pass
					else:
						pass
				
	
		
class Util(object):
	def unzip(self, source_filename, dest_dir):
		with zipfile.ZipFile(source_filename) as zf:
			for member in zf.infolist():
				# Path traversal defense copied from
				# http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
				words = member.filename.split('/')
				path = dest_dir
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word)
					head, word = os.path.split(word)
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word)
				zf.extract(member, os.path.relpath(path))
	def zip(self, source_filename, dest_dir):
		with zipfile.ZipFile(source_filename) as zf:
			for member in zf.infolist():
				# Path traversal defense copied from
				# http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
				words = member.filename.split('/')
				path = dest_dir
				for word in words[:-1]:
					drive, word = os.path.splitdrive(word)
					head, word = os.path.split(word)
					if word in (os.curdir, os.pardir, ''): continue
					path = os.path.join(path, word)
				zf.write(member, path)
	def getFolderSize(self,p):
		from functools import partial
		prepend = partial(os.path.join, p)
		return sum([(os.path.getsize(f) if os.path.isfile(f) else self.getFolderSize(f)) for f in map(prepend, os.listdir(p))])
	
class Runtime(object):
	def __init__(self, a):
		global LEGAL_CMDS
		
		self.db_name = ''
		self.db_pass = ''
		self.db_host = ''
		self.db_table = ''
		self.db_user = ''
		self._settings()
		self._profiles()
		self.propagate()
		self.uid = Record().generate()
		self.o = Output()
		self.type = 'CLIENT'
		self.help = 0
		self.clean = 0
		self.name = "N/A"
		self.version = "1.0.0"
                self.is_jit = False
		self.s3 = False
		self.has_version = False

                if not len(a) > 1:
			self.help = True
			self.type = ''

		for _i in range(0, len(a)):
			i = a[_i]
			try:
				j = a[_i + 1]
			except:
				j = a[_i]
				
			if i in ['-c', '--client']:
				self.type = 'CLIENT'
			if i in ['-s', '--server']:
				self.type = 'SERVER'
			if i in ['-h', '--help']:
				self.help = True
			if i in ['-b', '--backup']:
				self.backup = True
			if i in ['-r', '--restore']:
				self.restore = True
			if i in ['-i', '--ip']:
				self.ip = j
			if i in ['-p', '--port']:
				self.port = j
			if i in ['-x', '--compress']:
				self.compress = True
			if i in ['-e', '--encrypt']:
				self.encrypt = True
			if i in ['-l', '--local']:
				self.local = True
			if i in ['-f', '--folder']:
				self.folder = j
			if i in ['-li', '--list']:
				self.list = True
			if i in ['-p', '--profiler']:
				self.profiler = True
				self.type = 'PROFILER'
			if i in ['-rm', '--remove']:
				self.remove = True
			if i in ['-n', '--name']:
				self.name = j
			if i in ['-cl', '--clean']:
				self.clean = True
			if i in ['-id', '--id']:
				self.id = j
                        if i in ['-g', '--graceful']:
				self.graceful = True
			if i in ['-re', '--restart']:
				self.restart = True
			if i in ['-st', '--start']:
				self.start = True
			if i in ['-sp', '--stop']:
				self.stop = True
			if i in ['-sn', '--snapshot']:
				self.snapshot = True
			if i in ['-v', '--version']:
				self.version = j 
				self.has_version = True
			if i in ['-j', '--just-in-time', '-jit']:
				self.jit = True
                                self.is_jit = True
			if i in ['--settings']:
				self.settings = True
			if i in ['--stop-profiler']:
				self.stop_profiler = True
			if i in ['-st', '--status']:
				self.status = True
			if i in ['-s3', '--s3']:
				self.s3 = True
	
		if self.help:
			self._help()
			return

		if not self.has_version and 'restore' in dir(self):
			self.version = "latest" 

		self.o.show("Running in {0} mode".format(self.type))
		self.perform()
	"""
	try to set up the database
	"""
	def propagate(self):
		if self.db_family == 'mysql':
			self.db = DAL(self.db_family + '://' + self.db_user + ':' + self.db_pass + '@' + self.db_host + '/' + self.db_name, pool_size=1, migrate_enabled=False)
			self.db.executesql("""
			CREATE DATABASE IF NOT EXISTS {0};
			""".format(self.db_name))
			self.db.executesql("""
			CREATE TABLE IF NOT EXISTS {0} (
				`id` int,
				`uid` varchar(255),
				`name` varchar(255),
				`time` varchar(255),
				`folder` varchar(255),
				`size` int,
			        `version` varchar(5),
				`jit` varchar(5),
				`local` varchar(255)
			); """.format(self.db_table))
		else:
			self.db = DAL('sqlite://storage.db', migrate_enabled=False, folder='/usr/bin/') 
			self.db.executesql("""
			CREATE TABLE IF NOT EXISTS {0} (
				`id` int,
				`uid` varchar(255),
				`name` varchar(255),
				`time` varchar(255),
				`folder` varchar(255),
				`size` int,
			        `version` varchar(5),
				`jit` varchar(5),
				`local` varchar(255)
			); """.format(self.db_table))


		self.db.define_table(
			self.db_table,
			Field('id'),
			Field('uid'),
			Field('name'),
			Field('time'),
			Field('folder'),
			Field('size'),
			Field('version'),
		        Field('jit'),
			Field('local'),
		)

		
	def perform(self):
		is_success = False

		if 'settings' in dir(self):
			self.o.show('Opening settings')	
			os.system('vim /usr/local/lback/settings.json')

		if 'graceful' in dir(self):
			""" TODO add graceful shutdown """
			self.o.show("Stopping server..")
			os.system("pkill -f 'python ./lback.py --server'")
			os.system("pkill -f 'python /usr/bin/lback.py --server'")
			exit()
			return

		if 'stop' in dir(self):	
			self.o.show("Stopping server..")

			os.system("pkill -f 'python ./lback.py --server'")
			os.system("pkill -f 'python /usr/bin/lback.py --server'")
			quit()
			return

		if 'restart' in dir(self):
			self.o.show("Restarting server..")

			os.system("pkill -f 'python ./lback.py --server'")
			os.system("pkill -f 'python /usr/bin/lback.py --server'")
			self.o.show("Started new instance..")

			time.sleep(1)
			os.system("lback-server --start")
			quit()
			return
		
		if 'status' in dir(self):
			self.o.show("Status of SERVER:")
			return

		if 'stop_profiler' in dir(self):
			self.o.show("Stopping profiler..")
			os.system("pkill -f 'python ./lback.py --profiler'")
			os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
			return
		
		if 'folder' in dir(self):
			self.size = Util().getFolderSize(self.folder)
		
		if 'profiler' in dir(self):
			profiler = Profiler(self.profiles,self.server_ip,self.server_port,self.ip,self.port,self.db,self.db_table).run()


                if 'stop-jit' in dir(self):
 			self.o.show("Stopping JIT instance..")
			os.system("pkill -f 'python ./lback.py --jit'")
			os.system("pkill -f 'python /usr/bin/lback.py --profiler'")
                        return
			
		if not 'local' in dir(self):
			self.isLocal = False
			if self.type == 'CLIENT':
				client = Client(self.port, self.ip, dict(ip=self.server_ip, port=self.server_port))
				self.o.show("Running on port: {0}, ip: {1}".format(self.server_port, self.server_ip))
			else:
				server = Server(self.server_port, self.server_ip, self.db, self.db_table)
				self.o.show("Running on port: {0}, ip: {1}".format(self.server_port, self.server_ip))
				server.run()
				# exit now and loop
		else:
			self.isLocal = True
				
		if 'backup' in dir(self):

			## do s3 backups
			if 's3' in dir(self) and self.s3:
				## create a directory
				## for the s3 buckets

				conn = S3Connection(self.aws_access_key, self.aws_secret)
				bucket = conn.get_bucket(self.folder)
			
				folder = self.folder = "/usr/local/lback/s3/{0}-{1}".format(folder, time.time())
				
				keys = bucket.get_all_keys()
				for j in keys:
					contents = j.get_contents_as_string()
					f = open("{0}/{1}".format(folder, j.Name))
						
					f.write(contents)
					f.close()

				self.o.show("Successfully backed up your s3 bucket!")

			if not 'folder' in dir(self):
				pass
			else:
				self.o.show("Gathering files.. this can take awhile")
				bkp = Backup(self.uid, self.folder)
				bkp.run()
				
				if bkp.status == 1:

					if self.version == '1.0.0':
						""" try to get previous version """
						""" and up the patch by one """
						r = self.db(self.db[self.db_table].folder == self.folder).select().last()

						if r:
							v = r['version'] 
							cv = re.findall("\d\.\d\.(\d)", v)[0]
							nv = int(cv) + 1
							self.version = re.sub('\d$', str(nv), v)
							

					self.db[self.db_table].insert(uid=self.uid, time=time.time(), folder=self.folder, size=self.size, local=self.isLocal,name=self.name, version=self.version, jit=True if self.is_jit else False)
					self.db.commit()
				
				
					is_success = True
					
					if self.isLocal:
						self.o.show("Backup Ok -- Now saving to disk")
						self.o.show("Local Backup has been successfully stored")
						self.o.show("Transaction ID: " + self.uid)
					else:
						fc = open(bkp.get(), 'r').read()
						client.run('BACKUP', self.folder, self.uid, fc, self.name,self.version,self.size)
						if client.status:
							self.o.show("Backup Ok -- Now transferring to server")
							
							fp = client.get()
							if len(re.findall("SUCCESS", fp)) > 0:
								self.o.show("Remote Backup has been successfully transferred")
								self.o.show("Transaction ID: " + self.uid)
								os.remove(bkp.get())
							else:
								self.o.show("Something went wrong on the server.. couldnt back that folder. Reverting changes")
						else:
							pass
				else:
					pass
				
		if 'restore' in dir(self):
			if 'id' in dir(self):

				if not self.has_version:
					r = self.db((self.db[self.db_table].uid == self.id)  | \
					            (self.db[self.db_table].name == self.id) | \
						    (self.db[self.db_table].folder == self.id)).select().last()

	
				else:

					if self.version == "latest":
						r = self.db((self.db[self.db_table].uid == self.id)  | \
					            (self.db[self.db_table].name == self.id) | \
						    (self.db[self.db_table].folder == self.id)).select().last()


					elif self.version.lower() == "oldest":
						r = self.db((self.db[self.db_table].uid == self.id)  | \
					            (self.db[self.db_table].name == self.id) | \
						    (self.db[self.db_table].folder == self.id)).select().first()

					else:
						r = self.db(((self.db[self.db_table].uid == self.id)  | \
							     (self.db[self.db_table].name == self.id) | \
							     (self.db[self.db_table].folder == self.id)) \
							   & (self.db[self.db_table].version == self.version)).select().first()

				if not r:
					self.o.show("ERROR: Backup not found.")
					return
					
				self.folder = r['folder']
				self.local = r['local']
				self.ruid = r['uid']

				## restore an s3 instance
				if 's3' in dir(self) and self.s3:
					pass
				
				if self.clean:
					self.o.show("Cleaning directory..")
					if not os.path.isdir(self.folder):
						os.makedirs(self.folder)
					
				if self.isLocal:
					self.o.show("Restore Ok -- Now restoring compartment")
					rst = Restore(False, self.folder, self.clean)
					rst.run(True, self.ruid)	
					
					if rst.status:
						self.o.show("Restore has been successfully performed")
					## restore an s3 instance
					if 's3' in dir(self) and self.s3:
						self.o.show("Now pushing to AWS, S3")
						conn = S3Connection(self.aws_access_key, self.aws_secret)
						bucket = conn.get_bucket(self.folder)

						fs = os.listdir(self.folder)
						for i in fs:
							k = Key(bucket)
							f = open(i, "r").read()
							k.set_contents_from_string(f)

				else:
					self.o.show("Pinging server for restore..")
					client.run('RESTORE', self.folder, self.ruid, '', '', self.version)
					self.o.show("Forming archive.. this can take some time")
					if client.status:
						self.o.show("Restore Retrieval Ok -- now attempting to restore")
						fp = open(LOCAL_BACKUP_DIR + self.ruid + '.zip', 'w+')
						fp.write(client.get())
						fp.close()
						
						rst = Restore(LOCAL_BACKUP_DIR + self.ruid + '.zip', self.folder, self.clean)
						rst.run(True, self.ruid)
						
						if rst.status:
							self.o.show("Restore Successful")
							
			else:
				pass

		if 'jit' in dir(self):
                        if 'id' in dir(self):
                        	jit = JIT(self.db, self.db_table).check(self.id)
			else:
                        	self.o.show("Starting a JIT instance on this backup")
                        	os.system("lback-jit --id '{0}' > /dev/null 2>&1".format(self.uid))


		## important to check for success
		## on this command
		
		if 'remove' in dir(self) and is_success:
			if 'folder' in dir(self):
				shutil.rmtree(self.folder)
				self.o.show("Directory successfully deleted..")
			
		if 'list' in dir(self):
			rows = self.db(self.db[self.db_table].time > 0).select().as_list()
			self.o.show("Full list of stored backups")
			for i in rows:
				print i
	
	def _help(self):
		print """
usage: lback [options] required_input required_input2
options:
-c, --client     Run a command as a client (required)
-s, --server     Initiate a server (required)
-b, --backup     Run a backup
-r, --restore    Run a restore
-f, --folder     Specify a folder (required *) for backups
-i, --id,        Specify an id (required *) for restores [ this can be a folder or name of backup ]
-n, --name       Name for backup (optional)
-rm, --remove    Remove a directory on backup
-x, --compress   Compress an archive (default)
-l, --list       Generate a full list of your backups
-i, --ip         Specify an ip (overridden by settings.json if found)
-p, --port       Specify a port (overridden by settings.json if found)
-h, --help       Print this text
-s3, --s3        Backup S3 components
-jit, --just-in-time  Just in time backups (read docs for more) [accepts singular file or document]
-v, --version specify a version to restore (for restores you can use: LATEST|OLDEST)
--settings       Opens settings in VIM

SERVER SPECIFIC
-g, --graceful  Perform a graceful shutdown
-re, --restart  Restart the server
-st, --start    Start the server
-sp, --stop     Force a shutdown
-st, --status   Is the server running or stopped

PROFILER SPECIFIC
-st, --start Start the profiler
--stop_profiler Stop the profiler

JIT SPECIFIC
--st, --start starts a JIT instance
--stop        Stop the JIT instance
		"""
	
	def try_hard_to_find(self):
		pass
		
	def _settings(self):
		if os.path.isfile("/usr/local/lback/settings.json"):
			settings = json.loads(open("/usr/local/lback/settings.json").read())
		elif os.path.isfile("../settings.json"):
			settings = json.loads(open("../settings.json").read())
		for i in settings.keys():
			setattr(self, i, settings[i])
			
		self.ip = settings['client_ip']
		self.port = settings['client_port']
		self.server_ip = settings['server_ip']
		self.server_port = settings['server_port']
		
		if not 'db_family' in settings.keys():
			self.db_family = 'mysql'
		else:
			self.db_family = settings['db_family']

		if 'aws_access_key' in settings.keys():
			self.aws_access_key = settings['aws_access_key']

		if 'aws_secret' in settings.keys():
			self.aws_secret = settings['aws_secret']
		
	def _profiles(self):
		if os.path.isfile("/usr/local/lback/profiles.json"):
			self.profiles = json.loads(open("/usr/local/lback/profiles.json").read())
		elif os.path.isfile("../profiles.json"):
			self.profiles = json.loads(open("../profiles.json").read())	

	
if __name__ == '__main__':
	r = Runtime(sys.argv)
