def define_classes(server=False):
    global db_name_coll
    global commits_coll
    global branches_coll
    global files_coll
    global params_coll
    global base_class
	global mongo_db_name

    if server:
        from google.appengine.ext import db
        
        class _base_class:

            @staticmethod
            def insert(obj,_class,input_dict):
                for key in input_dict:
                    setattr(obj,key,input_dict[key])
                self.put()

            @staticmethod
            def update_entity(entity,_class,update_dict):
                for key in update_dict:
                    if key == "$set":
                        for temp_key in update_dict[key]:
                            setattr(entity,temp_key,update_dict[key][temp_key])
                    elif key == "$addToSet":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            temp_list=temp_list+update_dict[key][temp_key]
                            setattr(entity,temp_key,temp_list)
                    elif key == "$pull":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            temp_list.remove(update_dict[key][temp_key])
                            setattr(entity,temp_key,temp_list)
                    
                entity.put()


            @staticmethod
            def update(_class,search_dict,update_dict,upsert=False,multi=False):
                query=""
                for key in search_dict:
                    val=search_dict[key]
                    if type(val) is dict:
                        if "$in" in val:
                            query=key+" IN "+val["$in"]
                    else:
                        query=key+" ="+val

                matches=_class.all().filter(query)

                if matches.count()==0 and upsert:
                    temp_entity=_class()
                    temp_entity.insert(update_dict)
                elif matches.count()>0:
                    if not multi:
                        match=matches[0]
                        update_entity(match,update_dict)
                    else:
                        for match in matches:
                            update_entity(match,update_dict)

            @staticmethod
            def find_one(_class,search_dict):
                res=_base_class.find(_class,search_dict)

                if res.count()>0:
                    return res[0]
                else:
                    return None

            @staticmethod
            def find(_class,search_dict):
                query=""
                for key in search_dict:
                    val=search_dict[key]
                    if type(val) is dict:
                        if "$in" in val:
                            query=key+" IN "+val["$in"]
                    else:
                        query=key+" ="+val
                return _class.all().filter(query)
                
        class _db_name_coll(db.Model):
            repo_path=db.StringProperty(required=True)
            db_name=db.StringProperty(required=True)

        class _commits_coll(db.Model):
            uid=db.StringProperty(required=True)
            patch_ids=db.StringListProperty(required=True)
            ts=db.datetime(required=True)
            msg=db.StringProperty(required=True)
            added=db.StringListProperty(required=True)
            deleted=db.StringListProperty(required=True)
            parent_id=db.StringProperty(required=True)
            branch=db.StringProperty(required=True)
            child_ids=db.StringListProperty(required=True)
            num=db.IntegerProperty(required=True)
            level=db.IntegerProperty(required=True)
            db_name=db.StringProperty(required=True)

        class _branches_coll(db.Model):
            name=db.StringProperty(required=True)
            commit_ids=db.StringListProperty(required=True)
            head=db.StringProperty(required=True)
            tail=db.StringProperty(required=True)
            parent_branches=db.StringListProperty(required=True)
            db_name=db.StringProperty(required=True)

        class _files_coll(db.Model):
            name=db.StringProperty(required=True)
            path=db.StringProperty(required=True)
            staged=db.BooleanProperty(required=True)
            staged_ts=db.datetime(required=True)
            patch_ids=db.StringListProperty(required=True)
            is_present=db.BooleanProperty(required=True)
            to_remove=db.BooleanProperty(required=True)
            to_add=db.BooleanProperty(required=True)
            added_cids=db.StringListProperty(required=True)
            deleted_cids=db.StringListProperty(required=True)
            db_name=db.StringProperty(required=True)

        class _patches_coll(db.Model):
            uid=db.StringProperty(required=True)
            diff_dict=db.StringProperty(required=True)
            num=db.IntegerProperty(required=True)
            file_path=db.StringProperty(required=True)
            cid=db.StringProperty(required=True)
            branch=db.StringProperty(required=True)
            db_name=db.StringProperty(required=True)

        class _params_coll(db.Model):
            path=db.StringProperty(required=True)
            db_name=db.StringProperty(required=True)
            first_cid=db.StringProperty(required=True)
            cur_com_num=db.IntegerProperty(required=True)
            last_cid=db.StringProperty(required=True)
            cur_com_level=db.StringProperty(required=True)
            cur_branch=db.IntegerProperty(required=True)
            cur_patch_num=db.IntegerProperty(required=True)
            db_name=db.StringProperty(required=True)

    else:
        from pymongo import Connection

        class _base_class():
            @staticmethod
            def insert(obj,_class,input_dict):
                for key in input_dict:
                    setattr(obj,key,input_dict[key])
                
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                db[coll_name].insert(input_dict)


            @staticmethod
            def update(_class,search_dict,update_dict,upsert=False,multi=False):
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                db[coll_name].update(search_dict,update_dict,upsert=upsert,multi=multi)

            @staticmethod
            def find_one(_class,search_dict):
                res=_base_class.find(_class,search_dict)

                if res.count()>0:
                    return res[0]
                else:
                    return None

            @staticmethod
            def find(_class,search_dict):
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                return db[coll_name].find(search_dict)

        class _db_name_coll():
            def __init__(self):
                self.repo_path=""
                self.db_name=""

        class _commits_coll():
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

        class _branches_coll():
            def __init__(self):
                self.name=""
                self.commit_ids=[]
                self.head=""
                self.tail=""
                self.parent_branches=[]
                self.db_name=""

        class _files_coll():
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

        class _patches_coll():
            def __init__(self):
                self.uid=""
                self.diff_dict=""
                self.num=None
                self.file_path=""
                self.cid=""
                self.branch=""
                self.db_name=""

        class _params_coll():
            def __init__(self):
                self.path=""
                self.db_name=""
                self.first_cid=""
                self.cur_com_num=None
                self.last_cid=""
                self.cur_com_level=""
                self.cur_branch=None
                self.cur_patch_num=None

    db_name_coll=_db_name_coll
    commits_coll=_commits_coll
    branches_coll=_branches_coll
    files_coll=_files_coll
    params_coll=_params_coll
    base_class=_base_class
