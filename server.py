from http_server import http_server
from request_handler import request_handler
import getopt
import sys
import __future__
import time

if __name__=="__main__":
    port=8080
    num_forks=2
    num_threads_per_fork=2

    try:
        optlist,args=getopt.getopt(sys.argv[1:],"hp:f:t:")
    except getopt.GetoptError:
        print("usage python server.py [-p port_num] [-f num_forks] [-t num_threads_per_fork]")
        sys.exit(2)

    for opt,arg in optlist:
        if opt =="-h":
            print("usage python server.py [-p port_num] [-f num_forks] [-t num_threads_per_fork]")
            sys.exit(0)
        elif opt =="p":
            port=arg
        elif opt =="-f":
            num_forks=arg
        elif opt == "-t":
            num_threads_per_fork=arg

    
    server=http_server(num_forks,num_threads_per_fork,port,request_handler)
    
    print("Starting server "+str(time.asctime()))
    print("Port "+str(port))
    print("Num forks "+str(num_forks))
    print("Num threads per fork "+str(num_threads_per_fork))

    
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

