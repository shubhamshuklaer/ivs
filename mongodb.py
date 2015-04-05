#!/usr/bin/python

from pymongo import Connection
from pymongo import MongoClient
from bson.objectid import ObjectId
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
	def __init__(self,db_name):
		self.load_params(db_name)

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

	def save_params(self):
		param = self.params.find_one({"path": self.path})
		if(param == None):
			self.params.insert({
				"path": self.path,
				"dbname": self.dbname,
				"first_cid": self.first_cid,
				"cur_com_num": self.cur_com_num,
				"last_cid": self.last_cid,
				"cur_com_level": self.cur_com_level,
				"cur_branch": self.cur_branch
				}
			)
		else:
			self.params.update({
					"path": self.path
				},{
					'$set': {
						"path": self.path,
						"dbname": self.dbname,
						"first_cid": self.first_cid,
						"cur_com_num": self.cur_com_num,
						"last_cid": self.last_cid,
						"cur_com_level": self.cur_com_level,
						"cur_branch": self.cur_branch
					}
					
				}
			)

	def get_next_com_num(self):
		self.cur_com_num += 1
		return self.cur_com_num
	
	def get_next_com_level(self):
		self.cur_com_level += 1
		return self.cur_com_level

	def inc_com_level(self):
		self.cur_com_level += 1

	def inc_com_num(self):
		self.cur_com_num += 1

	def set_cur_com_level(num):
		self.cur_com_level = num

	def load_params(self, dbname):
		self.set_conn(Connection())
		self.set_db(self.conn[dbname])

		self.files = self.db.files
		self.commits = self.db.commits
		self.staged = self.db.staged
		self.params = self.db.params
		self.patches = self.db.patches
		self.branches = self.db.branches

		self.dmp = dmp_module.diff_match_patch()
		self.patch_obj = dmp_module.patch_obj()

		param = self.params.find_one({"path": self.path})
		if(param == None):
			pass
		else:
			self.dbname = param["dbname"]
			self.first_cid = param["first_cid"]
			self.cur_com_num = param["cur_com_num"]
			self.last_cid = param["last_cid"]
			self.cur_com_level = param["cur_com_level"]
			self.cur_branch = param["cur_branch"]
		
	def get_last_cid(self):
		return self.last_cid

	def set_last_cid(self, cid):
		self.last_cid = cid

	def get_cur_branch(self):
		return self.cur_branch

	def set_cur_branch(self, branch):
		self.cur_branch = branch

	def init(self):
		print "Loading parameters ..."
		self.load_params(self.dbname)
                
                repo_dir=os.path.join(self.path,".ivs")

		if not os.path.exists(repo_dir):
			os.makedirs(repo_dir)

			self.branches.insert({
				"name": "master",
				"commit_ids": [],
				"head": None,
				"tail": None
				}
			)
			self.cur_branch = "master"
			tmp_id = ObjectId()
			commit_id = self.commits.insert({
				"uid":  tmp_id,
				"patch_ids": [],
				"ts": time.time(),
				"msg": "Initial Commit on master",
				"added": [],
				"deleted": [],
				"parent_id": None,
				"branch": self.cur_branch,
				"child_ids": [],
				"num": 1,
				"level": 1
				}
			)
			self.branches.update({
				"name": "master"
				},{
					'$set': {
						"head": tmp_id,
						"tail": tmp_id
					}
				}
			)
			self.first_cid = tmp_id
			self.cur_com_num = 1
			self.last_cid = tmp_id
			self.cur_com_level = 1
		else:
			for root, dirs, files in os.walk(repo_dir):
				for f in files:
					os.unlink(os.path.join(root, f))
				for d in dirs:
					shutil.rmtree(os.path.join(root, d))
                
                db_name_file=open(os.path.join(repo_dir,"db_name"),'w')
                db_name_file.write(self.dbname+"\n")
                db_name_file.close()
                self.save_params()
	def is_all_committed(self):
		entries = self.files.find({"is_present": True})
		for entry in entries:
			if is_diff(entry):
				return false
		return true

	def restore_branch_data(branch):
		entry = self.branches.find_one({"name": branch})
		rollback(entry["head"])

	def checkout(branch):
		print "Checking out : " + str(branch)
		if not is_all_committed:
			print "You have uncommitted changes. Aborting checkout"
		self.restore_branch_data(branch)
		self.cur_branch = branch
		branch = self.branches.find_one({"name": str(branch)})
		self.last_cid = branch["head"]
		commit = self.commits.find({"uid": self.last_cid})
		self.cur_com_level = commit["level"]

	def create_branch(branch):

		self.branches.insert({
			"name": str(branch),
			"commit_ids": [],
			"tail": self.last_cid,
			"head": self.last_cid
			}
		)
		tmp_id = objectid()
		commit_id = self.commits.insert({
			"uid":  tmp_id,
			"patch_ids": [],
			"ts": time.time(),
			"msg": "Initial Commit on "+str(branch),
			"added": [],
			"deleted": [],
			"parent_id": self.last_cid,
			"branch": str(branch)
			}
		)
		self.branches.update({
			"name": str(branch)
			},{
				'$set': {
					"head": tmp_id
				}
			}
		)

	def add(self, path):
                self.load_params(self.dbname)
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
								"patch_ids": [],
								"is_present": True,
								"removed": False
							}
						)
					else:
						self.files.update({
								"path": os.path.relpath(os.path.join(root, f), self.path)
							},
							{
								'$set': {
									"staged": True, 
									"staged_ts": os.path.getmtime(os.path.join(root, f)),
									"is_present": True,
									"removed": False
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
						"patch_ids": [],
						"is_present": True,
						"removed": False
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
								"staged_ts": time.time(),
								"is_present": True,
								"removed": False
							} 
						} 
					)
                self.save_params()
	def remove(self, path):
		entries = self.files.find({"path": path, "is_present": True})
		for entry in entries:
			self.files.update({
					"path": entry["path"]
				},
				{ 
					'$set': {
						"staged": True,
						"removed": True
					} 
				} 
			)

	def commit(self, msg):
                self.load_params(self.dbname)
		entries = self.files.find({"staged": True, "is_present": True})
		for entry in entries:
			if ( not os.path.exists(os.path.join(self.path, entry["path"])) ) or entry["removed"] :
				print "Removing file " + str(entry["path"])
				self.files.update({
						"path": entry["path"]
					},
					{ 
						'$set': {
							"is_present": False
						} 
					} 
				)
				(tmp_txt, data) = self.get_diff(entry)
				patches = self.dmp.patch_make(data.decode('utf-8'), "".decode('utf-8'))
				tmp_id = ObjectId()
				if(len(patches) > 0):
					commit_id = self.commits.insert({
						"uid":  tmp_id,
						"patch_ids": [],
						"ts": time.time(),
						"msg": msg,
						"added": [],
						"deleted": [],
						"parent_id": self.last_cid,
						"branch": self.cur_branch,
						"child_ids": [],
						"num": self.get_next_com_num(),
						"level": self.get_next_com_level()
						}
					)

					self.commits.update({
						"uid": self.last_cid
						},{
							'$addToSet': {
								"child_ids": tmp_id
							}
						}
					)
					self.last_cid = tmp_id

					# print patches[0].patchs
					for patch in patches:

						patch_id = self.patches.insert(patch.patch_dict)

						self.files.update({
								"staged": True,
								"path": entry["path"],
							},
							{ 
								'$set': {
									"staged": False, 
									"staged_ts": time.time(),
									"is_present": False
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

			else:
				if(entry["removed"] == False):
					(tmp_txt, data) = self.get_diff(entry)
					# print type(tmp_txt) 
					patches = self.dmp.patch_make(tmp_txt, data.decode('utf-8'))
					tmp_id = ObjectId()
					if(len(patches) > 0):
						print "committing changes to " + str(entry["path"])
						commit_id = self.commits.insert({
							"uid":  tmp_id,
							"patch_ids": [],
							"ts": time.time(),
							"msg": msg,
							"added": [],
							"deleted": [],
							"parent_id": self.last_cid,
							"branch": self.cur_branch,
							"child_ids": [],
							"num": self.get_next_com_num(),
							"level": self.get_next_com_level()
							}
						)
						self.commits.update({
							"uid": self.last_cid
							},{
								'$addToSet': {
									"child_ids": tmp_id
								}
							}
						)
						self.last_cid = tmp_id

						# print patches[0].patchs
						for patch in patches:
							patch_id = self.patches.insert(patch.patch_dict)
							self.files.update({
									"staged": True,
									"path": entry["path"],
									"is_present": True
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
                self.save_params()
	def rollback(self, commit_id):
		print "Rolling back to : " + str(commit_id)
		entries = self.files.find()
		for entry in entries:
			(tmp_txt, data) = self.get_diff(entry)

	def tree(self):
		print "tree"

	def log(self):
		print "\n"
		commits = self.commits.find( { '$query': {}, '$orderby': { "ts" : -1 } } )
		for commit in commits:
			print "Commit \t: " + str(commit["_id"])
			print "Message\t: " + str(commit["msg"])
			print "" + datetime.datetime.fromtimestamp(commit["ts"]).strftime('%Y-%m-%d %H:%M:%S')
			print "\n"

	def is_diff(self, entry):
		if not os.path.exists(os.path.join(self.path, entry["path"])):
			return false
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
		# print "data: " + data
		# print "text: " + tmp_txt
		# print type(data) 
		return (tmp_txt, data)

	def status(self):
                self.load_params(self.dbname)
		print "untracked: \t"
		for root, dirs, files in os.walk(self.path):
			for f in files:
				entry = self.files.find_one({
					"path": os.path.relpath(os.path.join(root, f), self.path)
				})
				if(entry == None):
					print "\t" + os.path.relpath(os.path.join(root, f), self.path)

		entries = self.files.find({"is_present": True})
		for entry in entries:
			if not os.path.exists(os.path.join(self.path, entry["path"])):
				print "deleted: \t" + entry["path"]
				if(entry["staged"]):
					print "deleted + staged: \t" + entry["path"]
				else:
					print "deleted + unstaged: \t" + entry["path"]
				# self.files.update({
				# 		"path": entry["path"]
				# 	},
				# 	{ 
				# 		'$set': {
				# 			"is_present": False, 
				# 			"staged": False
				# 		} 
				# 	} 
				# )
			elif self.is_diff(entry):
				if(entry["staged"]):
					print "modified + staged: \t" + entry["path"]
				else:
					print "modified + unstaged: \t" + entry["path"]
			else:
				pass
                
	def update(self):
		print "update"

	def delete(self):
                self.load_params(self.dbname)
		print "Deleting"
		self.db.drop_collection('files')
		self.db.drop_collection('commits')
		self.db.drop_collection('staged')
		self.conn.drop_database('test_database')

		shutil.rmtree(os.path.join(self.path, '.ivs'))

	def show(self, col, name):
		print "Showing: " + name
		entry = col.find()
		for e in entry:
			print e

#if __name__ == "__main__":

	#repo = ivs()

        #repo.set_path("/home/kunal15595/Documents/theory")
        #repo.set_dbname("test_database")

        #repo.init()

        #repo.add("networks/tanenbaum/a.txt")
         #repo.remove("networks/tanenbaum/a.txt")

        #repo.status()
        #repo.commit("yo")
        #repo.log()
        #repo.show(repo.files, "files")
        #repo.show(repo.commits, "commits")
        #repo.show(repo.staged, "staged")

        #repo.save_params()
        
        # repo.delete()
