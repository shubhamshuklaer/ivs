import mongo_db_name_setting

def define_classes(server=False):
    if server:
        from google.appengine.ext import db
        
        class base_class:

            @staticmethod
            def insert(obj,_class,input_dict):
                for key in input_dict:
                    setattr(obj,key,input_dict[key])
                obj.put()

            @staticmethod
            def update_entity(entity,_class,update_dict):
                for key in update_dict:
                    if key == "$set":
                        for temp_key in update_dict[key]:
                            setattr(entity,temp_key,update_dict[key][temp_key])
                    elif key == "$addToSet":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            if type(update_dict[key][temp_key]) is list:
                                temp_list=temp_list+update_dict[key][temp_key]
                            else:
                                temp_list.append(update_dict[key][temp_key])
                            setattr(entity,temp_key,temp_list)
                    elif key == "$pull":
                        for temp_key in update_dict[key]:
                            temp_list=getattr(entity,temp_key)
                            temp_list.remove(update_dict[key][temp_key])
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

                count=0
                for match in matches:
                    count=count+1

                if count==0 and upsert:
                    temp_entity=_class()
                    temp_entity.insert(update_dict)
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
            def find(_class,search_dict):
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
                match_dict_list=[]

                for match in matches:
                    match_dict_list.append(db.to_dict(match))

                return match_dict_list


            @staticmethod
            def delete(_class,search_dict):
                matches=base_class.find(_class,search_dict)
                for match in matches:
                    match.delete()
                
        class db_name_coll(db.Model):
            repo_path=db.StringProperty()
            db_name=db.StringProperty()

        class commits_coll(db.Model):
            uid=db.StringProperty()
            patch_ids=db.StringListProperty()
            ts=db.DateTimeProperty()
            msg=db.StringProperty()
            added=db.StringListProperty()
            deleted=db.StringListProperty()
            parent_id=db.StringProperty()
            branch=db.StringProperty()
            child_ids=db.StringListProperty()
            num=db.IntegerProperty()
            level=db.IntegerProperty()
            db_name=db.StringProperty()

        class branches_coll(db.Model):
            name=db.StringProperty()
            commit_ids=db.StringListProperty()
            head=db.StringProperty()
            tail=db.StringProperty()
            parent_branches=db.StringListProperty()
            db_name=db.StringProperty()

        class files_coll(db.Model):
            name=db.StringProperty()
            path=db.StringProperty()
            staged=db.BooleanProperty()
            staged_ts=db.DateTimeProperty()
            patch_ids=db.StringListProperty()
            is_present=db.BooleanProperty()
            to_remove=db.BooleanProperty()
            to_add=db.BooleanProperty()
            added_cids=db.StringListProperty()
            deleted_cids=db.StringListProperty()
            db_name=db.StringProperty()

        class patches_coll(db.Model):
            uid=db.StringProperty()
            diff_dict=db.StringProperty()
            num=db.IntegerProperty()
            file_path=db.StringProperty()
            cid=db.StringProperty()
            branch=db.StringProperty()
            db_name=db.StringProperty()

        class params_coll(db.Model):
            path=db.StringProperty()
            db_name=db.StringProperty()
            first_cid=db.StringProperty()
            cur_com_num=db.IntegerProperty()
            last_cid=db.StringProperty()
            cur_com_level=db.StringProperty()
            cur_branch=db.IntegerProperty()
            cur_patch_num=db.IntegerProperty()
            db_name=db.StringProperty()

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

                if matches.count()>0:
                    for match in matches:
                        break
                    return match
                else:
                    return None

            @staticmethod
            def find(_class,search_dict):
                mongo_conn=Connection()
                db=mongo_conn[mongo_db_name_setting.mongo_db_name]
                coll_name=_class().__class__.__name__[:-5] # removing the _coll from end
                return db[coll_name].find(search_dict)


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
