import os
import time
import socketserver
from http.server import SimpleHTTPRequestHandler

PORT = 20105

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
                if os.path.isfile(filename):
                    a = time.ctime(os.path.getmtime(filename))
                    b = self.headers.get('If-Modified-Since', None)

                if a > b:
                    self.send_response(530)
                    self.send_header('Cache-control', 'must-revalidate')
                    self.end_headers()
                    self.wfile.write(f.read())
                    f.close()

                return

            # THE BELOW CODE WRITES THE RESPONSE AND FILE CONTENTS ALL TOGETHER IN A SINGLE BUFFER
            self.send_response(200)
            self.end_headers()
            self.wfile.write(str.encode(f.read()))

        return

    # def do_POST(self):
    #     filename = self.path.strip("/")
    #     print("fuck me ", filename)
    #     try:
    #         f = open(filename, 'r')
    #     except IOError:
    #         self.send_error(404, "File not found")
    #         return None
    #
    #     if f:
    #         self.wfile.write(f.read())
    #         f.close()

    # def do_HEAD(self):
    #
    #     filename = self.path.strip("/")
    #     print("@@@@@@@@@@@@@@@@@@ ", filename)
    #     if filename == "sample.txt":
    #         self.send_header('Cache-control', 'no-cache')
    #     else:
    #         self.send_header('Cache-control', 'must-revalidate')
    #
    #     self.end_headers()
    #
    #     return SimpleHTTPRequestHandler.do_HEAD(self)

socketserver.TCPServer.allow_reuse_address = True
s = socketserver.ThreadingTCPServer(("", PORT), HTTPCacheRequestHandler)
s.allow_reuse_address = True
print("Serving on port", PORT)
s.serve_forever()
