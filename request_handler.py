from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
import urlparse
import server_settings
# from pymongo import Connection
import os
from json import dumps,loads
from get_data_for_commits import get_data_for_commits
from apply_data import apply_data
from ivs_base import ivs
import shutil
import webapp2
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

import mongo_db_name_setting



from define_classes import define_classes
ret_list=define_classes(server=True)

mongo_db_name_setting.init()
mongo_db_name_setting.mongo_db_name="ivs_client"
mongo_db_name_setting.db_name_coll=ret_list[0]
mongo_db_name_setting.commits_coll=ret_list[1]
mongo_db_name_setting.branches_coll=ret_list[2]
mongo_db_name_setting.files_coll=ret_list[3]
mongo_db_name_setting.params_coll=ret_list[4]
mongo_db_name_setting.base_class=ret_list[5]


mongo_db_name=mongo_db_name_setting.mongo_db_name
db_name_coll=mongo_db_name_setting.db_name_coll
commits_coll=mongo_db_name_setting.commits_coll
branches_coll=mongo_db_name_setting.branches_coll
files_coll=mongo_db_name_setting.files_coll
params_coll=mongo_db_name_setting.params_coll
base_class=mongo_db_name_setting.base_class

from google.appengine.ext import db

class users_coll(db.Model):
    user_name=db.StringProperty(required=True)
    passwd=db.StringProperty(required=True)
    repo=db.StringListProperty(required=True)

class request_handler(webapp2.RequestHandler):
    def post(self):
        print("hello")
        global mongo_db_name
        global db_name_coll
        global commits_coll
        global branches_coll
        global files_coll
        global params_coll
        global base_class

        user_name=self.request.headers["user"]
        passwd=self.request.headers['passwd']
        data_to_send=""
        length = int(self.request.headers['content-length'])
        body=self.request.body_file.read(length)
        param=urlparse.parse_qs(body,True)#true keeps blank entries in dict
        action=param["action"][0]
        message=""
        if param["message"][0] != "":
            message=loads(param["message"][0])
        path=""
        if param["path"][0] !="":
            path=param["path"][0][1:]#[1:] is so that we skip the first char which is /


        if action in ["user_add"]:
            matches=base_class.find(users_coll,{"user_name":user_name})
            
            count=0
            for match in matches:
                count=count+1

            if count > 0:
                data_to_send=dumps("user already exist")
            else:
                temp_entity=users_coll()
                base_class.insert(temp_entity,users_coll,{"user_name":user_name,"passwd":passwd,"repo":[""]})
                data_to_send=dumps("user added")
            res_code=200
        else:
            matches=base_class.find(users_coll,{"user_name":user_name,"passwd":passwd,"repo":path})

            count=0
            for match in matches:
                count=count+1

            auth_ret=count>0

            if auth_ret:
                if action=="serv_create":
                    new_repo=self.headers.getheader("new_repo")
                    new_repo_path=os.path.join(server_settings.service_dir,user_name)
                    new_repo_path=os.path.join(new_repo_path,new_repo)

                    if os.path.exists(new_repo_path):
                        data_to_send=dumps("Repo already exist")
                    else:
                        repo=ivs()
                        repo_root=new_repo_path
                        db_name=self.headers.getheader("db_name")
                        repo.set_path(repo_root)
                        repo.set_dbname(user_name+"_"+db_name)
                        repo.init(True)
                        temp_ret_struct=base_class.update(users_coll,{"user_name":user_name},{
                            "$addToSet" : {
                                    "repo": user_name+"/"+new_repo
                                }
                        })
                        data_to_send=dumps("Initialized new repo "+user_name+"/"+new_repo)
                    res_code=200
                else:
                    repo_path=os.path.abspath(os.path.join(server_settings.service_dir,path))    
                    ivs_folder=os.path.abspath(os.path.join(repo_path,".ivs"))
                    db_name_file_name=os.path.abspath(os.path.join(ivs_folder,"db_name"))

                    if not os.path.exists(db_name_file_name):
                        res_code=404
                    else: 
                        db_name_file=open(db_name_file_name,"r")
                        db_name=db_name_file.readline().rstrip("\n")
                        db_name_file.close()

                        list_commit_uids=[]
                        list_commit_child_ids=[]
                        diff_list=[]

                        if action=="push":

                            print("push message")
                            print(message)
                            
                            apply_data(db_name,message,repo_path,server=True)
                            res_code=200
                            data_to_send="Done"
                        elif action=="add_perm":
                            add_perm_for_user=self.headers.getheader("add_perm_for_user")
                            matches=base_class.find(users_coll,{"user_name":add_perm_for_user})
                            count=0
                            for match in matches:
                                count=count+1

                            if count>0:
                                base_class.update(users_coll,{"user_name":add_perm_for_user},{
                                    "$addToSet": {
                                            "repo": path
                                        }
                                })
                                data_to_send="Success"
                            else:
                                data_to_send=dumps(add_perm_for_user+" user doesn't exist")

                            res_code=200
                        elif action=="serv_del":
                            repo=ivs()
                            repo_root=os.path.join(server_settings.service_dir,path)
                            repo.set_path(repo_root)
                            repo.set_dbname(db_name)
                            repo.delete()
                            base_class.update(users_coll,{},{
                                "$pull": {
                                        "repo": path
                                    }},
                                        multi= True
                            )
                            shutil.rmtree(repo_root)
                            data_to_send="Deleted repo"
                            
                            res_code=200
                        elif action=="get_need" or action=="pull":

                            for result in base_class.find(commits_coll,{"db_name":db_name },{ 'uid': 1, 'child_ids':1, '_id':0 }):
                                list_commit_uids.append(result["uid"])
                                list_commit_child_ids.append(str(result["child_ids"]))

                            message_commit_uids=message["uid_list"]
                            message_commit_child_ids=message["child_ids_list"]

                            if action=="get_need":#items not on server i.e items not in list_commit_uids
                                temp_len=len(message_commit_uids)
                                if(temp_len<len(list_commit_uids)):
                                    data_to_send=dumps("s")
                                else:
                                    for i in range(temp_len):
                                        if message_commit_uids[i] not in list_commit_uids:
                                            diff_list.append(message_commit_uids[i])
                                        else:
                                            temp_index=list_commit_uids.index(message_commit_uids[i])
                                            if len(message_commit_child_ids[i]) > len(list_commit_child_ids[temp_index]):
                                                diff_list.append(message_commit_uids[i])

                                    data_to_send=dumps(diff_list)

                            elif action=="pull":#items not on client i.e items not in message

                                temp_len=len(list_commit_uids)
                                for i in range(temp_len):
                                    if list_commit_uids[i] not in message_commit_uids:
                                        diff_list.append(list_commit_uids[i])
                                    else:
                                        temp_index=message_commit_uids.index(list_commit_uids[i])
                                        if len(list_commit_child_ids[i]) > len(message_commit_child_ids[temp_index]):
                                            diff_list.append(list_commit_uids[i])

                                data_to_send=get_data_for_commits(db_name,diff_list,server=True)

                        res_code=200
            else:
                res_code=403

        self.response.status(res_code)
        print(res_code)
        # self.response.write(data_to_send)
        self.response.write("dsfds")
        

app = webapp2.WSGIApplication([
        ('/', request_handler),
        ], debug=True)
