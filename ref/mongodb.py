#!/usr/bin/python

from pymongo import Connection
from pymongo import MongoClient
import os
import shutil
import sys
import time

class ivs:
	def __init__(self):
		print "New repo initiated"

	def set_path(self, path):
		self.path = path

	def get_path(self):
		return self.path

	def set_conn(self, conn):
		self.conn = conn

	def get_conn(self):
		return self.conn

	def set_db(self, db):
		self.db = db

	def get_db(self):
		return self.db

	def get_dbname(self):
		return self.dbname

	def set_dbname(self, name):
		self.dbname = name

	def set_params(self):
		self.params.insert({
				"path": self.path,
				"dbname": self.dbname
			}
		)
		

	def load_params(self, dbname):
		self.set_conn(Connection())
		self.set_db(self.conn[dbname])

		self.files = self.db.files
		self.commits = self.db.commits
		self.staged = self.db.staged
		self.params = self.db.params


	def init(self):

		if not os.path.exists(os.path.join(self.path, '.ivs')):
			os.makedirs(os.path.join(self.path, '.ivs'))
		else:
			self.load_params('test_database')

		for root, dirs, files in os.walk(os.path.join(self.path, '.ivs')):
			for f in files:
				os.unlink(os.path.join(root, f))
			for d in dirs:
				shutil.rmtree(os.path.join(root, d))

	def add(self, path):
		if path == "-a":
			for root, dirs, files in os.walk(self.path):
				for f in files:
					entry = self.files.find({"path": os.path.join(root, f)})
					if(entry.count() == 0):
						self.files.insert({
								"name": f, 
								"path": os.path.relpath(os.path.join(root, f), self.path), 
								"staged": True, "staged_ts": os.path.getmtime(os.path.join(root, f))
							}
						)
					else:
						self.files.update({
								"path": os.path.relpath(os.path.join(root, f), self.path)
							},
							{
								'$set': {
									"staged": True, 
									"staged_ts": os.path.getmtime(os.path.join(root, f))
								}
							}
						)
		else:
			entry = self.files.find({"path": path})
			if(entry.count() == 0):
				print "add insert"
				self.files.insert({
						"name": os.path.basename(path), 
						"path": path, 
						"staged": True, 
						"staged_ts": os.path.getmtime(os.path.join(self.path, path))
					}
				)
			else:
				print "add update"
				self.files.update({
						"path": path
					},
					{ 
						'$set': {
							"staged": True, 
							"staged_ts": os.path.getmtime(os.path.join(self.path, path))
						} 
					} 
				)

	def status(self):
		print "untracked: \t"
		for root, dirs, files in os.walk(self.path):
			for f in files:
				entry = self.files.find({
					"path": os.path.relpath(os.path.join(root, f), self.path)
				})
				if(entry.count() == 0):
					print "\t" + os.path.relpath(os.path.join(root, f), self.path)

		entries = self.files.find()
		for entry in entries:
			if not os.path.exists(os.path.join(self.path, entry.get("path"))):
				print "deleted: \t" + entry.get("path")
			elif os.path.getmtime(os.path.join(self.path, entry.get("path"))) > entry.get("staged_ts"):
				print "unstaged: \t" + entry.get("path")

	def update(self):
		print "update"

	def delete(self):
		print "Deleting"
		self.db.drop_collection('files')
		self.db.drop_collection('commits')
		self.db.drop_collection('staged')
		self.conn.drop_database('test_database')

	def show(self, col, name):
		print "Showing: " + name
		entry = col.find()
		for e in entry:
			print e

if __name__ == "__main__":

	repo = ivs()

	# cmdline_len = len(sys.argv)

	# if(cmdline_len > 1):
	# 	if sys.argv[1] == "init":
	# 		repo.set_path(sys.argv[2])
	# 		repo.init()
	# 	elif sys.argv[1] == "add":
	# 		repo.add(sys.argv[2])
	# 	elif sys.argv[1] == "delete":
	# 		repo.delete()
				
	repo.set_path("/home/kunal15595/Documents/theory")
	repo.set_dbname("test_database")
	
	repo.init()
	repo.show(repo.files, "files")

	repo.add("networks/forouzan/ch01.ppt")
	repo.show(repo.files, "files")
	repo.show(repo.commits, "commits")
	repo.show(repo.staged, "staged")
	repo.status()

	# repo.delete()