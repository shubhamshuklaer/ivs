import mongo_db_name_setting
import itertools

def define_classes(server=False):
    if server:
        from google.appengine.ext import db
        
        class base_class:

            @staticmethod
            def insert(obj,_class,input_dict):
				for key in input_dict:
					if key=="$set":
						for temp_key in input_dict[key]:
							setattr(obj,temp_key,input_dict[key][temp_key])
							print(temp_key,getattr(obj,temp_key))
					elif key=="$addToSet":
						for temp_key in input_dict[key]:
							temp_val=input_dict[key][temp_key]
							if type(temp_val) is dict:
								temp_val=temp_val["$each"]
								print("fdsfsadfasd")
							else:
								temp_val=[temp_val]
							setattr(obj,temp_key,temp_val)
							print(temp_key,getattr(obj,temp_key))
					else:
						setattr(obj,key,input_dict[key])
				ret_val=obj.put()
				print(ret_val,_class)

            @staticmethod
            def update_entity(entity,_class,update_dict):
                for key in update_dict:
                    if key == "$set":
                        for temp_key in update_dict[key]:
                            setattr(entity,temp_key,update_dict[key][temp_key])
                    elif key == "$addToSet":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            if type(update_dict[key][temp_key]) is dict:
                                for temp_elem in update_dict[key][temp_key]["$each"]:
                                    if temp_elem not in temp_list:
                                        temp_list.append(temp_elem)
                            else:
                                temp_elem=update_dict[key][temp_key]
                                if temp_elem not in temp_list:
                                    temp_list.append(temp_elem)
                            setattr(entity,temp_key,temp_list)
                    elif key == "$pull":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            temp_list.remove(update_dict[key][temp_key])
                            print(temp_key,temp_list)
                            setattr(entity,temp_key,temp_list)
                    
                entity.put()


            @staticmethod
            def update(_class,search_dict,update_dict,upsert=False,multi=False):
                res=_class.all()
                for key in search_dict:
                    val=search_dict[key]
                    if type(val) is dict:
                        if "$in" in val:
                            res.filter(key+" IN",val["$in"])
                    else:
                        res.filter(key+" =",val)

                matches=res.run()
                matches_copy,matches=itertools.tee(matches)

                count=0
                for match in matches:
                    count=count+1

                matches=matches_copy

                if count==0 and upsert:
					obj=_class()
					base_class.insert(obj,_class,update_dict)
                elif count>0:
                    if not multi:
                        for match in matches:
                            break
                        base_class.update_entity(match,_class,update_dict)
                    else:
                        for match in matches:
                            base_class.update_entity(match,_class,update_dict)

            @staticmethod
            def find_one(_class,search_dict):
                matches=base_class.find(_class,search_dict)
                
                count=0
                for match in matches:
                    count=count+1

                if count>0:
                    for match in matches:
                        break
                    return match
                else:
                    return None

            @staticmethod
            def find_entities(_class,search_dict):
                res=_class.all()
                for key in search_dict:
                    val=search_dict[key]
                    if type(val) is dict:
                        if "$in" in val:
                            res.filter(key+" IN",val["$in"])
                    else:
                        print(_class)
                        res.filter(key+" =",val)

                matches=res.run()
                return matches

            @staticmethod
            def find(_class,search_dict):
				print("fdsdsafsafasdfsadfasdfsad")
				print(search_dict)
				res=_class.all()
				print(_class)
				for key in search_dict:
					val=search_dict[key]
					if type(val) is dict:
						if "$in" in val:
							res.filter(key+" IN",val["$in"])
					else:
						res.filter(key+" =",val)

				matches=res.run()
				match_dict_list=[]

				class_name=_class().__class__.__name__[:-5]



				for match in matches:
					if class_name == "files":
						temp_dict={
								"name":None,
								"path":None,
								"staged":None,
								"staged_ts":None,
								"patch_ids":[],
								"is_present":None,
								"to_remove":None,
								"to_add":None,
								"added_cids":[],
								"deleted_cids":[],
								"db_name":None,
								}
					elif class_name == "commits":
						temp_dict={
								"uid":None,
								"patch_ids":[],
								"ts":None,
								"msg":None,
								"added":[],
								"deleted":[],
								"parent_id":None,
								"branch":None,
								"child_ids":[],
								"num":None,
								"level":None,
								"db_name":None,
								}
					elif class_name == "db_name":
						temp_dict={
								"repo_path":None,
								"db_name":None,
								}
					elif class_name == "patches":
						temp_dict={
								"uid":None,
								"diff_dict":None,
								"num":None,
								"file_path":None,
								"cid":None,
								"branch":None,
								"db_name":None,
								}
					elif class_name == "branches":
						temp_dict={
								"name":None,
								"commit_ids":[],
								"head":None,
								"tail":None,
								"parent_branches":[],
								"db_name":None,
								}
					elif class_name == "params":
						temp_dict={
								"path":None,
								"db_name":None,
								"first_cid":None,
								"cur_com_num":None,
								"last_cid":None,
								"cur_com_level":None,
								"cur_branch":None,
								"cur_patch_num":None,
								"db_name":None,
								}
					elif class_name == "users":
						temp_dict={
								"user_name":None,
								"passed":None,
								"repo":[]
								}
					match_dict_list.append(db.to_dict(match,temp_dict))
					print("hellllll")

				return match_dict_list


            @staticmethod
            def delete(_class,search_dict):
                matches=base_class.find_entities(_class,search_dict)
                for match in matches:
                    match.delete()
                
        class db_name_coll(db.Model):
            repo_path=db.StringProperty(default=None)
            db_name=db.StringProperty(default=None)

        class commits_coll(db.Model):
            uid=db.StringProperty(default=None)
            patch_ids=db.StringListProperty(default=[])
            ts=db.FloatProperty(default=None)
            msg=db.StringProperty(default=None)
            added=db.StringListProperty(default=[])
            deleted=db.StringListProperty(default=[])
            parent_id=db.StringProperty(default=None)
            branch=db.StringProperty(default=None)
            child_ids=db.StringListProperty(default=[])
            num=db.IntegerProperty(default=None)
            level=db.IntegerProperty(default=None)
            db_name=db.StringProperty(default=None)

        class branches_coll(db.Model):
            name=db.StringProperty(default=None)
            commit_ids=db.StringListProperty(default=[])
            head=db.StringProperty(default=None)
            tail=db.StringProperty(default=None)
            parent_branches=db.StringListProperty(default=[])
            db_name=db.StringProperty(default=None)

        class files_coll(db.Model):
            name=db.StringProperty(default=None)
            path=db.StringProperty(default=None)
            staged=db.BooleanProperty(default=None)
            staged_ts=db.FloatProperty(default=None)
            patch_ids=db.StringListProperty(default=[])
            is_present=db.BooleanProperty(default=None)
            to_remove=db.BooleanProperty(default=None)
            to_add=db.BooleanProperty(default=None)
            added_cids=db.StringListProperty(default=[])
            deleted_cids=db.StringListProperty(default=[])
            db_name=db.StringProperty(default=None)

        class patches_coll(db.Model):
            uid=db.StringProperty(default=None)
            diff_dict=db.StringProperty(default=None)
            num=db.IntegerProperty(default=None)
            file_path=db.StringProperty(default=None)
            cid=db.StringProperty(default=None)
            branch=db.StringProperty(default=None)
            db_name=db.StringProperty(default=None)

        class params_coll(db.Model):
            path=db.StringProperty(default=None)
            db_name=db.StringProperty(default=None)
            first_cid=db.StringProperty(default=None)
            cur_com_num=db.IntegerProperty(default=None)
            last_cid=db.StringProperty(default=None)
            cur_com_level=db.StringProperty(default=None)
            cur_branch=db.IntegerProperty(default=None)
            cur_patch_num=db.IntegerProperty(default=None)
            db_name=db.StringProperty(default=None)

    else:
        from pymongo import Connection

        class base_class():
            @staticmethod
            def insert(obj,_class,input_dict):
                for key in input_dict:
                    setattr(obj,key,input_dict[key])
                
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name_setting.mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                db[coll_name].insert(input_dict)


            @staticmethod
            def update(_class,search_dict,update_dict,upsert=False,multi=False):
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name_setting.mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                db[coll_name].update(search_dict,update_dict,upsert=upsert,multi=multi)

            @staticmethod
            def find_one(_class,search_dict):
                matches=base_class.find(_class,search_dict)

                if len(matches)>0:
                    return matches[0]
                else:
                    return None

            @staticmethod
            def find(_class,search_dict):
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name_setting.mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                matches=db[coll_name].find(search_dict,{"_id":0})
                match_list=[]

                for match in matches:
                    match_list.append(match)

                return match_list


            @staticmethod
            def delete(_class,search_dict):
                coll_name=_class().__class__.__name__[:-5]
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name_setting.mongo_db_name]
                db[coll_name].remove(search_dict)

        class db_name_coll():
            def __init__(self):
                self.repo_path=""
                self.db_name=""

        class commits_coll():
            def __init__(self):
                self.uid=""
                self.patch_ids=[]
                self.ts=None
                self.msg=""
                self.added=[]
                self.deleted=[]
                self.parent_id=""
                self.branch=""
                self.child_ids=[]
                self.num=None
                self.level=None
                self.db_name=""

        class branches_coll():
            def __init__(self):
                self.name=""
                self.commit_ids=[]
                self.head=""
                self.tail=""
                self.parent_branches=[]
                self.db_name=""

        class files_coll():
            def __init__(self):
                self.name=""
                self.path=""
                self.staged=None
                self.staged_ts=None
                self.patch_ids=[]
                self.is_present=None
                self.to_remove=None
                self.to_add=None
                self.added_cids=[]
                self.deleted_cids=[]
                self.db_name=""

        class patches_coll():
            def __init__(self):
                self.uid=""
                self.diff_dict=""
                self.num=None
                self.file_path=""
                self.cid=""
                self.branch=""
                self.db_name=""

        class params_coll():
            def __init__(self):
                self.path=""
                self.db_name=""
                self.first_cid=""
                self.cur_com_num=None
                self.last_cid=""
                self.cur_com_level=""
                self.cur_branch=None
                self.cur_patch_num=None

    return [db_name_coll,commits_coll,branches_coll,files_coll,patches_coll,params_coll,base_class]
