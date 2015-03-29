from BaseHTTPServer import BaseHTTPRequestHandler
import CGIHTTPServer
#The CGIHTTPServer module defines a request-handler class, 
#interface compatible with BaseHTTPServer.BaseHTTPRequestHandler 
#and inherits behavior from SimpleHTTPServer.SimpleHTTPRequestHandler 
#but can also run CGI scripts.

class request_handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        self.wfile.write("Hello")
