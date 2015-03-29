import httplib
import sys
import getopt
from urlparse import urlparse
import urllib


def pull_process(data):
    print(data)

    
def push_process(data):
    print(data)



def process(repo,action,message,callback):
    remote_repo_location=urlparse(repo)
    header={"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    param={"path":remote_repo_location.path,"action":action,"message":message}
    body=urllib.urlencode(param)
    conn=httplib.HTTPSConnection(remote_repo_location.netloc)
    conn.request("POST","",body,header)
    response=conn.getresponse()
    data=response.read()
    callback(data)


try:
    optlist,arg_list=getopt.getopt(sys.argv[1:],"h")
except getopt.GetoptError:
    print("Wrong format type use -h for help")

for opt,arg in optlist:
    if opt=="-h":
        print("Usage")
        print("pull remote_repo")
        print("push remote_repo")
        sys.exit(0)

if len(arg_list) != 2:
    print("Wrong format use -h for help")
    sys.exit(2)

if arg_list[0] == "pull":
    process(arg_list[1],arg_list[0],"pull_message",pull_process)
elif arg_list[0] == "push":
    process(arg_list[1],arg_list[0],"push_message",push_process)
else:
    print("wrong arguments use -h for help")
    sys.exit(2)


