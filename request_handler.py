from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
import urlparse
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

class request_handler(BaseHTTPRequestHandler):
    def do_POST(self):
        body=self.rfile.read()
        param=urlparse.parse_qs(body)
        action=param["action"][0]
        print(param["action"][0]=="pull")
        
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
        if action=="push":
            self.wfile.write("Push")
            print("push")
        elif action== "pull":
            print("pull")
            self.wfile.write("pull")

