from http_server import http_server
import getopt
import sys
import __future__
import time
import os
import server_settings

if __name__=="__main__":

    server_settings.init()

    if not os.path.exists(server_settings.service_dir):
            os.makedirs(server_settings.service_dir)

    try:
        optlist,args=getopt.getopt(sys.argv[1:],"hp:f:t:d:")
    except getopt.GetoptError:
        print("wrong format use -h for help ")
        sys.exit(2)

    for opt,arg in optlist:
        if opt =="-h":
            print("usage python server.py [-p port_num] [-f num_forks] [-t num_threads_per_fork] [-d service_dir] ")
            sys.exit(0)
        elif opt =="-p":
            server_settings.port=int(arg)
        elif opt =="-f":
            server_settings.num_forks=int(arg)
        elif opt == "-t":
            server_settings.num_threads_per_fork=int(arg)
        elif opt == "-d":
            server_settings.service_dir=int(arg)

    
    server=http_server()
    
    print("Starting server "+str(time.asctime()))
    print("Port "+str(server_settings.port))
    print("Num forks "+str(server_settings.num_forks))
    print("Num threads per fork "+str(server_settings.num_threads_per_fork))

    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    print("Closing server "+str(time.asctime()))
    try:
        server.shutdown()
    except:
        print("hello")
        
    sys.exit(0)

