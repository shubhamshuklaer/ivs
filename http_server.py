from PooledProcessMixIn import PooledProcessMixIn
from BaseHTTPServer import HTTPServer

class http_server(PooledProcessMixIn,HTTPServer):
    def __init__(self,num_processes,num_threads_per_process,port,request_handler):
        self._process_n=num_processes
        self._thread_n=num_threads_per_process
        HTTPServer.__init__(self,("127.0.0.1",port),request_handler)
        self._init_pool()

