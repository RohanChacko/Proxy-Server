import os
import time
import socketserver
from http.server import SimpleHTTPRequestHandler

port_no = int(input("Enter port number to serve on: "))
PORT = port_no

class HTTPCacheRequestHandler(SimpleHTTPRequestHandler):

    def do_GET(self):


        filename = self.path.split('/')[-1].split('/')[-1]

        if self.command != "POST":
            try:
                f = open(filename, 'r')
            except:

                self.send_error(404)
                self.end_headers()
                self.wfile.write("File not found\n\n")

            if self.headers.get('If-Modified-Since', None):
                print("Entered if modified")
                if os.path.isfile(filename):
                    a = time.gmtime(time.mktime(time.strptime(time.ctime(os.path.getmtime(filename)), "%a %b %d %H:%M:%S %Y")))
                    b = time.strptime(self.headers.get('If-Modified-Since', None), "%a, %d %b %Y %H:%M:%S GMT")
                if a > b:
                    self.send_response(530)
                    self.send_header('Cache-control', 'must-revalidate')
                    self.end_headers()
                    self.wfile.write(str.encode(f.read()))
                else:
                    self.send_response(304)
                    self.end_headers()
            else:
                # THE BELOW CODE WRITES THE RESPONSE AND FILE CONTENTS ALL TOGETHER IN A SINGLE BUFFER
                self.send_response(200)
                # self.send_header('Cache-control', 'no-cache')
                self.send_header('Cache-control', 'must-revalidate')
                self.end_headers()
                self.wfile.write(str.encode(f.read()))

            f.close()

        return

    def do_POST(self):
        filename = self.path.split('/')[-1].split('/')[-1]
        try:
            f = open(filename,'r')
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(f.read()))
            f.close()

        except:
            self.send_error(404)
            self.end_headers()
            self.wfile.write("File not found\n\n")

        return

socketserver.TCPServer.allow_reuse_address = True
s = socketserver.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)
s.allow_reuse_address = True
print("Serving on port", PORT)
s.serve_forever()
