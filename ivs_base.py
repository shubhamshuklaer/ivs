#!/usr/bin/python
from __future__ import division
from uuid import uuid4 as ObjectId
import os
import shutil
import sys
import time
import unittest
import diff_match_patch as dmp_module
import datetime
from json import dumps,loads
import mongo_db_name_setting


import string


mongo_db_name=None
db_name_coll=None
commits_coll=None
branches_coll=None
files_coll=None
params_coll=None
patches_coll=None
base_class=None


class ivs:
	def __init__(self,_server=False):
		# self.conn=None
		# self.db=None
		# self.files =None
		# self.commits =None
		# self.staged =None
		# self.params =None
		# self.patches =None
		# self.branches =None
		# self.ivs =None
		self.first_cid =None
		self.cur_com_num =None
		self.last_cid =None
		self.cur_com_level =None
		self.cur_branch =None
		self.cur_patch_num =None
		self.dmp =None
		self.patch_obj =None
		self.path=None
                self.server=_server
		self.dbname=None

                global mongo_db_name
                global db_name_coll
                global commits_coll
                global branches_coll
                global files_coll
                global params_coll
                global base_class
                global patches_coll

                mongo_db_name=mongo_db_name_setting.mongo_db_name
                db_name_coll=mongo_db_name_setting.db_name_coll
                commits_coll=mongo_db_name_setting.commits_coll
                branches_coll=mongo_db_name_setting.branches_coll
                files_coll=mongo_db_name_setting.files_coll
                patches_coll=mongo_db_name_setting.patches_coll
                params_coll=mongo_db_name_setting.params_coll
                base_class=mongo_db_name_setting.base_class
	def set_uname(self,name):
		self.name=name;

	def get_uname(self):
		return self.name

	def set_path(self, path):
		self.path = path

	def get_path(self):
		return self.path

	# def set_conn(self, conn):
		# self.conn = conn

	# def get_conn(self):
		# return self.conn

	# def set_db(self, db):
		# self.db = db

	# def get_db(self):
		# return self.db

        def get_dbname(self):
                return self.dbname

        def set_dbname(self, name):
                self.dbname = name

	def get_next_com_num(self):
		self.cur_com_num += 1
		return self.cur_com_num
	
	def inc_com_num(self):
		self.cur_com_num += 1

	def get_next_patch_num(self):
		self.cur_patch_num += 1
		return self.cur_patch_num
	
	def inc_patch_num(self):
		self.cur_patch_num += 1

	def get_next_com_level(self):
		self.cur_com_level += 1
		return self.cur_com_level

	def inc_com_level(self):
		self.cur_com_level += 1

	def dec_com_level(self):
		self.cur_com_level -= 1

	def dec_com_num(self):
		self.cur_com_num -= 1

	def set_cur_com_level(self, num):
		self.cur_com_level = num

	def save_params(self):
		param = base_class.find_one(params_coll,{
                    "db_name": self.dbname,
                    "path": self.path})
		if(param == None):
                        temp_entity=params_coll()
			base_class.insert(temp_entity,params_coll,{
				"path": self.path,
				"db_name": self.dbname,
	#			"uname": self.name,      # added the attributes
				"first_cid": self.first_cid,
				"cur_com_num": self.cur_com_num,
				"last_cid": self.last_cid,
				"cur_com_level": self.cur_com_level,
				"cur_branch": self.cur_branch,
				"cur_patch_num": self.cur_patch_num
				}
			)
		else:
			base_class.update(params_coll,{
                                        "db_name": self.dbname,
					"path": self.path
				},{
					'$set': {
						"path": self.path,
						"db_name": self.dbname,
		#				"uname": self.name,       # added the attributes
						"first_cid": self.first_cid,
						"cur_com_num": self.cur_com_num,
						"last_cid": self.last_cid,
						"cur_com_level": self.cur_com_level,
						"cur_branch": self.cur_branch,
						"cur_patch_num": self.cur_patch_num
					}
					
				}
			)

	def load_params(self):
		# self.set_conn(Connection())
		# self.set_db(self.conn[self.dbname])

		# self.files = self.db.files
		# self.commits = self.db.commits
		# self.staged = self.db.staged
		# self.params = self.db.params
		# self.patches = self.db.patches
		# self.branches = self.db.branches
		# self.ivs = self.db.ivs

		param = base_class.find_one(params_coll,{
                    "db_name": self.dbname,
                    "path": self.path})
		if(param == None):
			pass
		else:
			self.dbname = param["db_name"]
			self.first_cid = param["first_cid"]
			self.cur_com_num = param["cur_com_num"]
			self.last_cid = param["last_cid"]
			self.cur_com_level = param["cur_com_level"]
			self.cur_branch = param["cur_branch"]
			self.cur_patch_num = param["cur_patch_num"]
		
		self.dmp = dmp_module.diff_match_patch()
		self.patch_obj = dmp_module.patch_obj()

	def get_last_cid(self):
		return self.last_cid

	def set_last_cid(self, cid):
		self.last_cid = cid

	def get_cur_branch(self):
		return self.cur_branch

	def set_cur_branch(self, branch):
		self.cur_branch = branch

	def get_full_path(self, path):
		return os.path.join(self.path, path)

	def init(self,server=False):
		
		repo_dir=os.path.join(self.path,".ivs")

		if not os.path.exists(os.path.join(self.path, '.ivs')):
			if not self.server:
				os.makedirs(os.path.join(self.path, '.ivs'))

			print "Loading parameters ..."
			self.load_params()

			
			self.cur_branch = "master"
			tmp_id = str(ObjectId())

			if not server:
				temp_entity=commits_coll()
				base_class.insert(temp_entity,commits_coll,{
					"uid":  tmp_id,
					"db_name": self.dbname,
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
				temp_entity=branches_coll()
				base_class.insert(temp_entity,branches_coll,{
					"name": "master",
					"commit_ids": [],
					"db_name": self.dbname,
					"head": tmp_id,
					"tail": tmp_id,
					"parent_branches": []
					}
					)
			
			self.first_cid = tmp_id
			self.cur_com_num = 1
			self.last_cid = tmp_id
			self.cur_com_level = 1
			self.cur_patch_num = 0
			
			# client = MongoClient()
			# dbs = client['ivs']   # the database to store the connections
	# #		dbs.ivs.insert( {'repo': self.dbname } )   # separte entry for each repo
			# # TODO
	# #		dbs.ivs.insert( {'repo': self.dbname , 'user': } )   # separte entry for each repo
		
		# #	self.ivs.insert( { 'repo': self.dbname } )

		else:
			self.delete()
			self.init(server)

			if not server:
				self.save_params()

			if not self.server:
				db_name_file=open(os.path.join(repo_dir,"db_name"),'w')
				db_name_file.write(self.dbname+"\n")
				db_name_file.close()

	def is_all_committed(self):
            entries = base_class.find(files_coll,{"db_name":self.dbname,"is_present": True})

            for entry in entries:
                    if not os.path.exists(os.path.join(self.path, entry["path"])):
                            return False
                    if self.is_diff(entry):
                            print "unstaged: " + entry["path"]
                            return False
            return True

	def restore_branch_data(self, branch):
		print "Restoring data on branch : " + str(branch)
		entry = base_class.find_one(branches_coll,{"db_name":self.dbname,"name": branch})
		self.rollback(entry["head"])

	def checkout(self, branch):
		self.load_params()
		if self.cur_branch == branch:
			print "Already on branch. Aborted"
			return
		self.load_params()
		if(base_class.find_one(branches_coll,{"db_name":self.dbname,"name": str(branch)}) == None):
			print "Branch doesn't exists. Aborting"
			return
		if not self.is_all_committed():
			print "You have uncommitted changes. Aborting checkout"
			return
		
		print "\nChecking out : " + str(branch)
		self.restore_branch_data(branch)
		self.cur_branch = branch
		branch = base_class.find_one(branches_coll,{"db_name":self.dbname,"name": str(branch)})
		self.last_cid = branch["head"]
		commit = base_class.find_one	(commits_coll,{"db_name":self.dbname,"uid": self.last_cid})
		self.cur_com_level = commit["level"]
		self.save_params()
	
	def create_branch(self, branch):
		self.load_params()
		if(base_class.find_one(branches_coll,{"db_name":self.dbname,"name": str(branch)}) != None):
			print "Branch already exists. Aborting"
			return

		upstream_branches = base_class.find_one(branches_coll,{"db_name":self.dbname,"name": self.get_cur_branch()})["parent_branches"]
		upstream_branches.append(self.get_cur_branch())
                temp_entity=branches_coll()
		base_class.insert(temp_entity,branches_coll,{
			"name": str(branch),
			"commit_ids": [],
                        "db_name": self.dbname,
			"tail": self.last_cid,
			"head": self.last_cid,
			"parent_branches": upstream_branches
			}
		)
		
		cid = str(ObjectId())
                temp_entity=commits_coll()
		base_class.insert(temp_entity,commits_coll,{
			"uid":  cid,
			"patch_ids": [],
			"ts": time.time(),
			"msg": "Initial Commit on "+str(branch),
                        "db_name": self.dbname,
			"added": [],
			"deleted": [],
			"parent_id": self.last_cid,
			"branch": str(branch),
			"child_ids": [],
			"num": self.get_next_com_num(),
			"level": self.get_next_com_level()

			}
		)
		base_class.update(commits_coll,{
                        "db_name": self.dbname,
			"uid": self.last_cid
			},{
				'$addToSet': {
					"child_ids": cid
				}
			}
		)
		self.dec_com_level()
		base_class.update(branches_coll,{
                        "db_name": self.dbname,
			"name": str(branch)
			},{
				'$set': {
					"head": cid
				}
			}
		)

	def add(self, path):
		self.load_params()

		if path == "-a":
			for root, dirs, files in os.walk(self.path):
				dirs[:] = [d for d in dirs if d not in ".ivs"]

				for f in files:
					if not self.istext(os.path.join(root, f)):
						print str(os.path.relpath(os.path.join(root, f), self.path)) + " : File type not supported. Aborting"
						continue
					entry = base_class.find_one(files_coll,{"db_name":self.dbname,"path": os.path.relpath(os.path.join(root, f), self.path)})
					
					if(entry == None):
                                                temp_entity=files_coll()
						base_class.insert(temp_entity,files_coll,{
								"name": str(os.path.relpath(os.path.join(root, f), self.path)), 
								"path": str(os.path.relpath(os.path.join(root, f), self.path)), 
								"staged": True, 
								"staged_ts": os.path.getmtime(os.path.join(root, f)),
								"patch_ids": [],
                                                                "db_name": self.dbname,
								"is_present": True,
								"to_remove": False,
								"to_add": True,
								"added_cids": [],
								"deleted_cids": []
							}
						)
					else:
						if not self.is_diff(entry):
							continue
						base_class.update(files_coll,{
                                                                "db_name": self.dbname,
								"path": os.path.relpath(os.path.join(root, f), self.path)
							},
							{
								'$set': {
									"staged": True, 
									"staged_ts": os.path.getmtime(os.path.join(root, f)),
									"is_present": True,
									"to_remove": False
								}
							}
						)
		elif not os.path.isfile(os.path.join(self.path, str(path))):
			print "Improper path. Aborting"
			return	
		else:
			entry = base_class.find_one(files_coll,{"db_name":self.dbname,"path": path})
			if(entry == None):

				print "Staging new file: " + str(path)
                                temp_entity=files_coll()
				base_class.insert(temp_entity,files_coll,{
						"name": os.path.basename(path), 
						"path": str(path), 
						"staged": True, 
						"staged_ts": os.path.getmtime(os.path.join(self.path, path)),
						"patch_ids": [],
                                                "db_name": self.dbname,
						"is_present": True,
						"to_remove": False,
						"to_add": True,
						"added_cids": [],
						"deleted_cids": []
					}
				)
			else:
				if not self.istext(os.path.join(self.path, entry["path"])):
					print str(entry["path"]) + " : File type not supported. Aborting"
					return
				if self.is_diff(entry):
					print "\nStaging modified file: " + str(path)
					base_class.update(files_coll,{
                                                        "db_name": self.dbname,
							"path": path
						},
						{ 
							'$set': {
								"staged": True, 
								"staged_ts": time.time(),
								"is_present": True,
								"to_remove": False
							} 
						} 
					)
				else:
					print "No change since last commit. Aborting"
		self.save_params()
	
	def remove(self, path):
		self.load_params()
		entries = base_class.find(files_coll,{"db_name":self.dbname,"path": path, "is_present": True})
		for entry in entries:
			base_class.update(files_coll,{
                                        "db_name": self.dbname,
					"path": entry["path"]
				},
				{ 
					'$set': {
						"staged": True,
						"to_remove": True
					} 
				} 
			)
		self.save_params()
	
	def commit(self, msg):
		self.load_params()
		entries = base_class.find(files_coll,{"db_name":self.dbname,"staged": True, "is_present": True})

                count=0
                for match in entries:
                    count=count+1
		# print entries.count()
		if(count == 0):
			print "Nothing to commit. Aborting"
			return
		else:
			print "\nCommit"
		cid = str(ObjectId())
                temp_entity=commits_coll()
		base_class.insert(temp_entity,commits_coll,{
			"uid":  cid,
			"patch_ids": [],
                        "db_name": self.dbname,
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
		base_class.update(branches_coll,{
                                "db_name": self.dbname,
				"name": self.cur_branch
			},{
				'$set': {
					"head": cid
				}
			}
		)
		for entry in entries:
			if entry["to_remove"] :
				print "Removing : " + str(entry["path"])
				base_class.update(files_coll,{
                                                "db_name": self.dbname,
						"path": str(entry["path"])
					},
					{ 
						'$set': {
							"staged": False,
							"is_present": False,
							"to_remove": False
						} 
					} 
				)
				(tmp_txt, data) = self.get_diff(entry)
				patches = self.dmp.patch_make(data.decode('utf-8'), "".decode('utf-8'))

                                count=0
                                for match in patches:
                                    count=count+1

				if( count > 0):
					
					base_class.update(commits_coll,{
                                                "db_name": self.dbname,
						"uid": self.last_cid
						},{
							'$addToSet': {
								"child_ids": cid
							}
						}
					)
					

					# print patches[0].patchs
					for patch in patches:
						pid = str(ObjectId())
                                                temp_entity=patches_coll()
                                                print("fasdasdfsadfsdfsadfsadfsdfdsafsadfsafsadfasd")
						base_class.insert(temp_entity,patches_coll,{
							"uid": pid,
							"diff_dict": dumps(patch.patch_dict),
							"num": self.get_next_patch_num(),
                                                        "db_name": self.dbname,
							"file_path": entry["path"],
							"cid": cid,
							"branch": self.get_cur_branch()
							}
						)

						base_class.update(files_coll,{
                                                                "db_name": self.dbname,
								"path": entry["path"]
							},
							{ 
								'$set': {
									"staged": False, 
									"staged_ts": time.time(),
									"is_present": False
								},
								'$addToSet': {
									"patch_ids": pid,
									"deleted_cids": cid
								}
							} 
						)

						base_class.update(commits_coll,{
                                                                "db_name": self.dbname,
								"uid": cid
							},
							{
								'$addToSet': {
									"patch_ids": pid,
									"deleted": entry["path"]
								},
								
							}
						)

			elif entry["to_add"]:
				print "Adding : " + str(entry["path"])
				base_class.update(files_coll,{
                                                "db_name": self.dbname,
						"path": str(entry["path"])
					},
					{ 
						'$set': {
							"staged": False,
							"to_add": False
						} 
					} 
				)
				# print self.files.find_one({"path": entry["path"]})["staged"]
				(tmp_txt, data) = self.get_diff(entry)
				# print type(tmp_txt) 
				patches = self.dmp.patch_make(tmp_txt, data.decode('utf-8'))

                                count=0
                                for match in patches:
                                    count=count+1

				if( count > 0):
					print "Committing : " + str(entry["path"])
					base_class.update(commits_coll,{
                                                "db_name": self.dbname,
						"uid": self.last_cid
						},{
							'$addToSet': {
								"child_ids": cid
							}
						}
					)

					# print patches[0].patchs
					for patch in patches:
						pid = str(ObjectId())
                                                temp_entity=patches_coll()
						base_class.insert(temp_entity,patches_coll,{
							"uid": pid,
							"diff_dict": dumps(patch.patch_dict),
							"num": self.get_next_patch_num(),
                                                        "db_name": self.dbname,
							"file_path": entry["path"],
							"cid": cid,
							"branch": self.get_cur_branch()
							}
						)
						
						base_class.update(files_coll,{
                                                                "db_name": self.dbname,
								"path": entry["path"]
							},
							{ 
								'$set': {
									"staged": False, 
									"staged_ts": time.time()
								},
								'$addToSet': {
									"patch_ids": pid,
									"added_cids": cid
								}
							} 
						)
						base_class.update(commits_coll,{
                                                                "db_name": self.dbname,
								"uid": cid
							},
							{
								'$addToSet': {
									"patch_ids": pid,
									"added": entry["path"]
								}
								
							}
						)
			else:
				# print "Committing file " + str(entry["path"])
				base_class.update(files_coll,{
                                                "db_name": self.dbname,
						"path": str(entry["path"])
					},
					{ 
						'$set': {
							"staged": False
						} 
					} 
				)
				# print self.files.find_one({"path": entry["path"]})["staged"]
				(tmp_txt, data) = self.get_diff(entry)
				# print type(tmp_txt) 
				patches = self.dmp.patch_make(tmp_txt, data.decode('utf-8'))
                                
                                count=0
                                for match in patches:
                                    count=count+1

				if(count > 0):
					print "Committing : " + str(entry["path"])
					
					base_class.update(commits_coll,{
                                                "db_name": self.dbname,
						"uid": self.last_cid
						},{
							'$addToSet': {
								"child_ids": cid
							}
						}
					)

					# print patches[0].patchs
					for patch in patches:
						pid = str(ObjectId())
                                                temp_entity=patches_coll()
                                                base_class.insert(temp_entity,patches_coll,{
                                                    "uid": pid,
                                                    "diff_dict": dumps(patch.patch_dict),
                                                    "num": self.get_next_patch_num(),
                                                    "file_path": entry["path"],
                                                    "db_name": self.dbname,
                                                    "cid": cid,
                                                    "branch": self.get_cur_branch()
                                                    }
                                                )
						
						
						base_class.update(files_coll,{
                                                                "db_name": self.dbname,
								"path": entry["path"],
								"is_present": True
							},
							{ 
								'$set': {
									"staged": False, 
									"staged_ts": time.time()
								},
								'$addToSet': {
									"patch_ids": pid
								}
							} 
						)
						base_class.update(commits_coll,{
                                                                "db_name": self.dbname,
								"uid": cid
							},
							{
								'$addToSet': {
									"patch_ids": pid,
									"added": entry["path"]
								}
								
							}
						)
		self.last_cid = cid
		self.save_params()


	def path_to_commit(self, cid):
		path = [cid]
		com = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": cid})
		if not com:
			return path
		while len(path) < 100 and cid != self.first_cid:
			cid = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": cid})["parent_id"]
			path.insert(0, cid)
		return path

	def rollback(self, cid):
		self.load_params()
		com = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": cid})

		path = self.path_to_commit(cid)

		if len(path) == 0:
			print "Improper cid. Aborting"
			return
		# print "Rolling back to : " + str(cid)
		files_to_delete = set()
		files_content_dict=dict()
		for com_id in path:
			commit = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": com_id})
			for f in commit["added"]:
				if not os.path.exists(os.path.dirname(self.get_full_path(f))):
					os.makedirs(os.path.dirname(self.get_full_path(f)))
				if f in files_to_delete:
					files_to_delete.remove({f})
				open(self.get_full_path(f), 'w').close()
			for f in commit["deleted"]:
				files_to_delete.update({f})
			if len(commit["patch_ids"])==0:
				continue
			
			mongo_patch_cur=base_class.find(patches_coll,{"db_name":self.dbname,"uid": { "$in": commit["patch_ids"]}})

			file_path = None
			for mongo_patch in mongo_patch_cur:

				patch_dict=dict()
				# print(mongo_patch)
                                mongo_patch_dict=loads(mongo_patch["diff_dict"])
				patch_dict["diffs"]=mongo_patch_dict["diffs"]
				patch_dict["start1"]=int(mongo_patch_dict["start1"])
				patch_dict["start2"]=int(mongo_patch_dict["start2"])
				patch_dict["length1"]=int(mongo_patch_dict["length1"])
				patch_dict["length2"]=int(mongo_patch_dict["length2"])

				patch_obj=dmp_module.patch_obj()
				patch_obj.fill_dict(patch_dict)

				file_path = mongo_patch["file_path"]
				if file_path not in files_content_dict:
					files_content_dict[file_path]=[]

				files_content_dict[file_path].append(patch_obj)	


		for file_path in files_content_dict:
			recover_text = self.dmp.patch_apply(files_content_dict[file_path], "")[0]
			#print("recover text for file "+file_path+" : " + recover_text)
			fp = open(self.get_full_path(file_path),'w')
			fp.write(recover_text)
			fp.close()

		for file_path in files_to_delete:
			os.unlink(os.path.join(self.path, file_path))
		self.last_cid = cid
		self.cur_com_level = com["level"]
		self.make_files_db(cid)
		#self.delete_tree(cid)

	def delete_tree(self, cid):
		child_ids = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": cid})["child_ids"]
		for child_id in child_ids:
			self.delete_tree(child_id)

	def tree(self, level = 0):
		print "tree"


	def log(self):
		self.load_params()
		print "\n"
		commits = base_class.find(commits_coll,{})
                commits = sorted(commits, key=lambda k: k['ts'],reverse=True) 
		for commit in commits:
			print "Commit \t: " + str(commit["uid"])
			print "Message\t: " + str(commit["msg"])
			print "" + datetime.datetime.fromtimestamp(commit["ts"]).strftime('%Y-%m-%d %H:%M:%S')
			print "\n"

	def is_diff(self, entry):
		if not entry:
			return False
		if not os.path.exists(os.path.join(self.path, entry["path"])):
			return false
		(past, cur) = self.get_diff(entry)
		return past != cur.decode('utf-8')

	def get_diff(self, entry):
		recover_text = ""
		patch_ids = entry["patch_ids"]
		parent_branches=[]
		temp_cur=base_class.find_one(branches_coll,{"name": self.get_cur_branch()})#["parent_branches"]
		parent_branches = parent_branches + temp_cur["parent_branches"]
		parent_branches.append(self.get_cur_branch())
		# print patch_ids
		if(patch_ids !=None and len(patch_ids) > 0):
			# print len(patch_ids)
			# for patch_id in patch_ids:
				# print patch_id

			# mongo_patch = self.patches.find_one({"uid": patch_id})
                        mongo_patch_cur = base_class.find(patches_coll,{"db_name":self.dbname,"uid":{'$in': patch_ids}})
			files_content=None
			patch_obj_arr=[]

                        count=0
                        for match in mongo_patch_cur:
                            count=count+1
			
			if count < 1:
				pass
			else:
				for mongo_patch in mongo_patch_cur:
					if not mongo_patch["branch"] in parent_branches:
						continue

					patch_dict=dict()
                                        mongo_patch_dict=loads(mongo_patch["diff_dict"])
					# print(mongo_patch)
					patch_dict["diffs"]=mongo_patch_dict["diffs"]
					patch_dict["start1"]=int(mongo_patch_dict["start1"])
					patch_dict["start2"]=int(mongo_patch_dict["start2"])
					patch_dict["length1"]=int(mongo_patch_dict["length1"])
					patch_dict["length2"]=int(mongo_patch_dict["length2"])

					patch_obj=dmp_module.patch_obj()
					patch_obj.fill_dict(patch_dict)
					patch_obj_arr.append(patch_obj)

				recover_text = self.dmp.patch_apply(patch_obj_arr, "")[0]

		if not os.path.exists(os.path.join(self.path, entry["path"])):
			present_data = ""
		else:
			with open (os.path.join(self.path, entry["path"]), "r") as myfile:
				present_data = myfile.read()

		return (recover_text, present_data)

	def status(self):
		self.load_params()
		print "untracked: \t"
		for root, dirs, files in os.walk(self.path):
			dirs[:] = [d for d in dirs if d not in ".ivs"]
			for f in files:
				if not self.istext(os.path.join(root, f)):
					continue
				entry = base_class.find_one(files_coll,{"db_name":self.dbname,
					"path": os.path.relpath(os.path.join(root, f), self.path)
				})
				if(entry == None):
					print "\t" + os.path.relpath(os.path.join(root, f), self.path)

		entries = base_class.find(files_coll,{"db_name":self.dbname,"is_present": True})
		for entry in entries:
			if not os.path.exists(os.path.join(self.path, entry["path"])):
				print "deleted: \t" + entry["path"]
				if(entry["staged"]):
					print "deleted + staged: \t" + entry["path"]
				else:
					print "deleted + unstaged: \t" + entry["path"]

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
		self.load_params()
		print "Deleting"
                    
                print(self.dbname)
                base_class.delete(commits_coll,{"db_name":self.dbname}) 
                base_class.delete(params_coll,{"db_name":self.dbname}) 
                base_class.delete(branches_coll,{"db_name":self.dbname}) 
                base_class.delete(patches_coll,{"db_name":self.dbname}) 
                base_class.delete(files_coll,{"db_name":self.dbname}) 
                
                # self.db.drop_collection('files')
                # self.db.drop_collection('commits')
                # self.db.drop_collection('staged')
                if not self.server:
                    shutil.rmtree(os.path.join(self.path, '.ivs'))

	# def show(self, col, name):
		# print "Showing: " + name
		# entry = col.find()
		# for e in entry:
			# print e

	def istext(self, filename):
	    s=open(filename).read(512)
	    text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
	    _null_trans = string.maketrans("", "")
	    if not s:
	        # Empty files are considered text
	        return True
	    if "\0" in s:
	        # Files with null bytes are likely binary
	        return False
	    # Get the non-text characters (maps a character to itself then
	    # use the 'remove' option to get rid of the text characters.)
	    t = s.translate(_null_trans, text_characters)
	    # If more than 30% non-text characters, then
	    # this is considered a binary file
	    if float(len(t))/float(len(s)) > 0.30:
	        return False
	    return True


	def make_files_db(self,cid):
		files_collection=dict()
		self.load_params()
		path=self.path_to_commit(cid)
		patch_ids=[]
		delete_collection=dict()

		for cid in path:
			commit = base_class.find_one(commits_coll,{"db_name":self.dbname,"uid": cid})
			patch_ids=commit["patch_ids"]
			for path in commit["added"]:
				if path not in files_collection:
					files_collection[path]=self.create_file_entry(path)
					delete_collection[path]=False
				files_collection[path]["added_cids"].append(cid)
				delete_collection[path]=False
				
			for path in commit["deleted"]:
				if path not in files_collection:
					files_collection[path]=self.create_file_entry(path)
					delete_collection[path]=False
				files_collection[path]["deleted_cids"].append(cid)
				delete_collection[path]=True

			for patch in base_class.find(patches_coll,{"db_name":self.dbname,"uid" :{"$in":patch_ids}}):
				if patch["file_path"] not in files_collection:
					files_collection[path]=self.create_file_entry(path)
					delete_collection[path]=False

				files_collection[patch["file_path"]]["patch_ids"].append(patch["uid"])


		self.db.drop_collection("files")
		self.files=self.db.files
		for key in files_collection:
			if not delete_collection[key]:
                                temp_entity=files_coll()
				base_class.insert(temp_entity,files_coll,files_collection[key])


						


	def create_file_entry(self,path):
		return {
			"name": path, 
			"path": path,
			"staged": False, 
			"staged_ts": os.path.getmtime(os.path.join(self.path,path)),
			"patch_ids": [],
                        "db_name": self.dbname,
			"is_present": True,
			"to_remove": False,
			"to_add": False,
			"added_cids": [],
			"deleted_cids": []
			}
