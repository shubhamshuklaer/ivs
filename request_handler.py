from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
import urlparse
import server_settings
from pymongo import Connection
import os
from bson.json_util import dumps,loads
from get_data_for_commits import get_data_for_commits
from apply_data import apply_data
from ivs_base import ivs
import shutil
from google.appengine.ext import webapp
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

class request_handler(webapp.RequestHandler):
    def do_POST(self):
        user_name=self.request.headers["user"]
        passwd=self.request.headers['passwd']
        data_to_send=""
        mong_conn_users=Connection()
        db_users=mong_conn_users[server_settings.user_auth_db_name]
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
            if db_users.users.find({"user_name":user_name}).count() > 0:
                data_to_send=dumps("user already exist")
            else:
                db_users.users.insert({"user_name":user_name,"passwd":passwd,"repo":[""]})
                data_to_send=dumps("user added")
            res_code=200
        else:
            auth_ret=db_users.users.find({"user_name":user_name,"passwd":passwd,"repo":path}).count()>0

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
                        temp_ret_struct=db_users.users.update({"user_name":user_name},{
                            "$addToSet" : {
                                    "repo": user_name+"/"+new_repo
                                }
                        })
                        data_to_send=dumps("Initialized new repo "+user_name+"/"+new_repo)
                    res_code=200
                else:
                    mongo_conn=Connection()
                    repo_path=os.path.abspath(os.path.join(server_settings.service_dir,path))    
                    ivs_folder=os.path.abspath(os.path.join(repo_path,".ivs"))
                    db_name_file_name=os.path.abspath(os.path.join(ivs_folder,"db_name"))

                    if not os.path.exists(db_name_file_name):
                        res_code=404
                    else: 
                        db_name_file=open(db_name_file_name,"r")
                        db_name=db_name_file.readline().rstrip("\n")
                        db_name_file.close()

                        db=mongo_conn[db_name]
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
                            if db_users.users.find({"user_name":add_perm_for_user}).count()>0:
                                db_users.users.update({"user_name":add_perm_for_user},{
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
                            db_users.users.update({},{
                                "$pull": {
                                        "repo": path
                                    }},
                                        multi= True
                            )
                            mongo_conn.drop_database(db_name) 
                            shutil.rmtree(repo_root)
                            data_to_send="Deleted repo"
                            
                            res_code=200
                        elif action=="get_need" or action=="pull":

                            for result in db.commits.find({ },{ 'uid': 1, 'child_ids':1, '_id':0 }):
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

        self.send_response(res_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.response.write(data_to_send)
        

