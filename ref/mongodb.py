#!/usr/bin/python

from pymongo import Connection
from pymongo import MongoClient
import os
import shutil
import sys
import time
import unittest
import diff_match_patch as dmp_module
import datetime
import bson
import json

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
		self.patches = self.db.patches


	def init(self):
		if not os.path.exists(os.path.join(self.path, '.ivs')):
			os.makedirs(os.path.join(self.path, '.ivs'))
		else:
			print "Loading parameters ..."
			self.load_params('test_database')

		for root, dirs, files in os.walk(os.path.join(self.path, '.ivs')):
			for f in files:
				os.unlink(os.path.join(root, f))
			for d in dirs:
				shutil.rmtree(os.path.join(root, d))

		self.dmp = dmp_module.diff_match_patch()
		self.patch_obj = dmp_module.patch_obj()

	def add(self, path):
		if path == "-a":
			for root, dirs, files in os.walk(self.path):
				for f in files:
					entry = self.files.find({"path": os.path.join(root, f)})
					if(entry.count() == 0):
						self.files.insert({
								"name": f, 
								"path": os.path.relpath(os.path.join(root, f), self.path), 
								"staged": True, 
								"staged_ts": os.path.getmtime(os.path.join(root, f)),
								"patch_ids": []
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
			entry = self.files.find_one({"path": path})
			if(entry == None or len(entry) == 0):
				print "add insert"
				self.files.insert({
						"name": os.path.basename(path), 
						"path": path, 
						"staged": True, 
						"staged_ts": os.path.getmtime(os.path.join(self.path, path)),
						"patch_ids": []
					}
				)
			else:
				if self.is_diff(entry):
					print "add update"
					self.files.update({
							"path": path
						},
						{ 
							'$set': {
								"staged": True, 
								"staged_ts": time.time()
							} 
						} 
					)

	def commit(self, msg):
		print "committing"
		entries = self.files.find({"staged": True})
		for entry in entries:
			(tmp_txt, data) = self.get_diff(entry)

			# print type(tmp_txt) 
			patches = self.dmp.patch_make(tmp_txt, data.decode('utf-8'))

			if(len(patches) > 0):
				commit_id = self.commits.insert({
					"patch_ids": [],
					"ts": time.time(),
					"msg": msg
					}
				)
				# print patches[0].patchs
				for patch in patches:
					#patch_id = self.patches.insert({
							#"obj": {
								#"diffs": patch.diffs,
							    #"start1": patch.start1,
							    #"start2": patch.start2,
							    #"length1": patch.length1,
							    #"length2": patch.length2
							#}
						#}
					#)
                                        patch_id = self.patches.insert(patch.patch_dict)

					self.files.update({
							"staged": True,
							"path": entry["path"]
						},
						{ 
							'$set': {
								"staged": False, 
								"staged_ts": time.time()
							},
							'$addToSet': {
								"patch_ids": patch_id
							}
						} 
					)

					self.commits.update({
						"_id": commit_id
						},
						{
							'$addToSet': {
								"patch_ids": patch_id
							}
						}
					)

	def log(self):
		commits = self.commits.find( { '$query': {}, '$orderby': { "ts" : -1 } } )
		for commit in commits:
			print "Commit \t: " + str(commit["_id"])
			print "Message\t: " + str(commit["msg"])
			print "" + datetime.datetime.fromtimestamp(commit["ts"]).strftime('%Y-%m-%d %H:%M:%S')
			print "\n\n"

	def is_diff(self, entry):
		(past, cur) = self.get_diff(entry)
		return past != cur.decode('utf-8')

	def get_diff(self, entry):
		tmp_txt = ""
		patch_ids = entry["patch_ids"]
		# print patch_ids
		patch_obj_arr = []
		if(patch_ids !=None and len(patch_ids) > 0):
			print len(patch_ids)
			for patch_id in patch_ids:
				# print patch_id

				for mongo_patch in self.patches.find({"_id": patch_id}):
					#patch_obj = {
						#"diffs": patch["obj"]["diffs"],
						#"start1": patch["obj"]["start1"],
						#"start2": patch["obj"]["start2"],
						#"length1": patch["obj"]["length1"],
						#"length2": patch["obj"]["length2"]
					#}
                                        patch_dict=dict()
                                        print(mongo_patch)
                                        patch_dict["diffs"]=mongo_patch["diffs"]
                                        patch_dict["start1"]=int(mongo_patch["start1"])
                                        patch_dict["start2"]=int(mongo_patch["start2"])
                                        patch_dict["length1"]=int(mongo_patch["length1"])
                                        patch_dict["length2"]=int(mongo_patch["length2"])

                                        patch_obj=dmp_module.patch_obj()
                                        patch_obj.fill_dict(patch_dict)
					patch_obj_arr.append(patch_obj)	

				tmp_txt = self.dmp.patch_apply(patch_obj_arr, "")[0]
		with open (os.path.join(self.path, entry["path"]), "r") as myfile:
			data=myfile.read()
		print "data: " + data
		print "text: " + tmp_txt
		# print type(data) 
		return (tmp_txt, data)

	def status(self):
		print "untracked: \t"
		for root, dirs, files in os.walk(self.path):
			for f in files:
				entry = self.files.find({
					"path": os.path.relpath(os.path.join(root, f), self.path)
				})
				# if(entry.count() == 0):
				# 	print "\t" + os.path.relpath(os.path.join(root, f), self.path)

		entries = self.files.find()
		for entry in entries:
			if not os.path.exists(os.path.join(self.path, entry["path"])):
				print "deleted: \t" + entry["path"]
			elif self.is_diff(entry):
				print "unstaged: \t" + entry["path"]
			else:
				pass

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

        repo.set_path("/home/shubham/Documents/theory")
        repo.set_dbname("test_database")

        repo.init()

        repo.add("patch_test/a.txt")


        repo.status()
        repo.commit("yo")
        repo.log()
        repo.show(repo.files, "files")
        repo.show(repo.commits, "commits")
        repo.show(repo.staged, "staged")

        #repo.delete()
