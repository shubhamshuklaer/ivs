# from PooledProcessMixIn import PooledProcessMixIn
# from BaseHTTPServer import HTTPServer
# from request_handler import request_handler
# import ssl
# import server_settings

# #http://code.activestate.com/recipes/442473-simple-http-server-supporting-ssl-secure-communica/

# class http_server(PooledProcessMixIn,HTTPServer):
    # def __init__(self):
        # self._process_n=server_settings.num_forks
        # self._thread_n=server_settings.num_threads_per_fork
        # HTTPServer.__init__(self,("0.0.0.0",server_settings.port),request_handler)
        
        # #wrap socket provides a socket-like wrapper that also encrypts and decrypts the data going over the socket with SSL.
        # self.socket=ssl.wrap_socket(self.socket,keyfile='server.pem',certfile='server.pem',server_side=True)
        # self._init_pool()

