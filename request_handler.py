from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
import urlparse
import server_settings
from pymongo import Connection
import os
from bson.json_util import dumps,loads
from get_data_for_commits import get_data_for_commits
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

class request_handler(BaseHTTPRequestHandler):
    def do_POST(self):
        user_name=self.headers.getheader('user')
        passwd=self.headers.getheader('passwd')
        data_to_send=""
        if user_name=="s" and passwd=="s":
            length = int(self.headers.getheader('content-length'))
            body=self.rfile.read(length)
            param=urlparse.parse_qs(body)
            action=param["action"][0]
            message=loads(param["message"][0])
            path=param["path"][0][1:]#[1:] is so that we skip the first char which is /

            mongo_conn=Connection()
            print(server_settings.service_dir)
            repo_path=os.path.abspath(os.path.join(server_settings.service_dir,path))    
            print(repo_path)
            ivs_folder=os.path.abspath(os.path.join(repo_path,".ivs"))
            db_name_file_name=os.path.abspath(os.path.join(ivs_folder,"db_name"))
            print(db_name_file_name)

            if not os.path.exists(db_name_file_name):
                res_code=404
            else: 
                db_name_file=open(db_name_file_name,"r")
                db_name=db_name_file.readline().rstrip("\n")
                db_name_file.close()

                db=mongo_conn[db_name]
                list_commit_uids=[]
                diff_list=[]

                if action=="push":
                    for entity in message["commits"]:
                        db.commits.insert(entity)
                        
                    for entity in message["patches"]:
                        db.patches.insert(entity)

                    data_to_send="Done"
                elif action=="get_need" or action=="pull":

                    for result in db.commits.find({ },{ 'uid': 1, '_id':0 }):
                        list_commit_uids.append(str(result["uid"]))


                    if action=="get_need":
                        for item in message:
                            if item not in list_commit_uids:
                                diff_list.append(item)

                        data_to_send=diff_list
                    elif action=="pull":
                        for item in list_commit_uids:
                            if item not in message:
                                diff_list.append(item)

                        data_to_send=get_data_for_commits(db_name,diff_list)

                res_code=200
        else:
            res_code=403

        self.send_response(res_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write(data_to_send)
        

