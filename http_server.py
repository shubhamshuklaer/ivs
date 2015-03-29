from PooledProcessMixIn import PooledProcessMixIn
from BaseHTTPServer import HTTPServer
import ssl

#http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

class http_server(PooledProcessMixIn,HTTPServer):
    def __init__(self,num_processes,num_threads_per_process,port,request_handler):
        self._process_n=num_processes
        self._thread_n=num_threads_per_process
        HTTPServer.__init__(self,("127.0.0.1",port),request_handler)
        
        #wrap socket provides a socket-like wrapper that also encrypts and decrypts the data going over the socket with SSL.
        self.socket=ssl.wrap_socket(self.socket,keyfile='server.pem',certfile='server.pem',server_side=True)
        self._init_pool()

