from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
import urlparse
import server_settings
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

class request_handler(BaseHTTPRequestHandler):
    def do_POST(self):
        user_name=self.headers.getheader('user')
        passwd=self.headers.getheader('passwd')
        if user_name=="shubham" and passwd=="shubham":
            length = int(self.headers.getheader('content-length'))
            body=self.rfile.read(length)
            param=urlparse.parse_qs(body)
            action=param["action"][0]
            
            if action=="push":
                self.wfile.write("Push")
                print("push")
            elif action== "pull":
                print("pull")
                self.wfile.write("pull")
            self.wfile.write(server_settings.service_dir)
            res_code=200
        else:
            res_code=403

        self.send_response(res_code)
        self.send_header('Content-type','text/html')
        self.end_headers()
        

