import socket
from time import gmtime, strftime, time
import sys
import threading
import signal
import json
import fnmatch
import os
import errno
from time import gmtime, strftime, localtime
from datetime import datetime
import threading
import logging
import urllib
import binascii
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler
from http.client import HTTPResponse
from io import StringIO
import re
import base64

class StringToHTTPResponse():
    def __init__(self, response_str):
        self._file = StringIO(response_str)

    def makefile(self, *args, **kwargs):
        return self._file


class ProxyServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(
            socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 20100))
        self.server_socket.listen(10)

        self.accesses = {}
        self.cache_file_dict = {}
        self.cache_header_dict = {}
        self.cache_filename = []
        self.passwd = {'admin': 'password'}

        with open('blacklist.txt', 'r') as f:
            self.blacklist = f.readlines()

    def listenForClient(self):
        while True:
            (clientSocket, client_address) = self.server_socket.accept()
            d = threading.Thread(name="proxy_client", target=self.proxy_thread, args=(
                clientSocket, client_address))
            d.daemon = True
            d.start()
        self.shutdown(0, 0)

    def proxy_thread(self, conn, addr):
        request_text = conn.recv(1024)
        if not 20000 <= addr[1] < 20100:
            print("INVALID PORT")
            conn.send(b"HTTP/1.1 403 Forbidden\n\n")
            conn.close()
            return
        
        first_line = request_text.split(b'\r\n')[0]
        resource = first_line.split(b' ')[1]
        headers_list = [i.decode() for i in request_text.split(
            b'\r\n') if re.match('[a-zA-Z]+: ', i.decode())]
        print(headers_list)
        headers = {h.split(': ')[0]: h.split(': ')[1] for h in headers_list}
        print(headers)
        filename = [i.decode() for i in request_text.split(b'\r\n')
                    ][0].split('?')[0].split('/')[-1]

        auth_obtained = True
        for b in self.blacklist:
            if headers['Host'] in b:
                auth_obtained = False
                if 'Authorization' in headers:
                    auth_type, pass_string = headers['Authorization'].split()
                    for user in self.passwd:
                        print(base64.b64encode(str.encode(user+':'+self.passwd[user])))
                        if base64.b64encode(str.encode(user+':'+self.passwd[user])) == str.encode(pass_string):
                            auth_obtained = True
                            print("USER AUTHENTICATED")
                    if not auth_obtained:
                        conn.send(str.encode("HTTP/1.1 403 Forbidden\n\n"))
                        conn.close()
                        print("AUTHENTICATION FAILED")
                        return
                elif not auth_obtained:
                    print("ERROR: BLACKLISTED SITE")
                    ####################### CLOSE CONNECTION #######################
                    conn.send(str.encode("HTTP/1.1 407 Proxy Authentication Required\nProxy-Authenticate: Basic realm=\"Access blacklisted site\"\n\n"))
                    request_text = conn.recv(1024)
                    first_line = request_text.split(b'\r\n')[0]
                    resource = first_line.split(b' ')[1]
                    headers_list = [i.decode() for i in request_text.split(
                        b'\r\n') if re.match('[a-zA-Z]+: ', i.decode())]
                    print(headers_list)
                    headers = {h.split(': ')[0]: h.split(': ')[1] for h in headers_list}
                    print(headers)
                    filename = [i.decode() for i in request_text.split(b'\r\n')
                                ][0].split('?')[0].split('/')[-1]
                    if 'Authorization' in headers:
                        auth_type, pass_string = headers['Authorization'].split()
                        for user in self.passwd:
                            print(base64.b64encode(str.encode(user+':'+self.passwd[user])))
                            if base64.b64encode(str.encode(user+':'+self.passwd[user])) == str.encode(pass_string):
                                auth_obtained = True
                                print("USER AUTHENTICATED")
                        if not auth_obtained:
                            conn.send(str.encode("HTTP/1.1 403 Forbidden\n\n"))
                            conn.close()
                            print("AUTHENTICATION FAILED")
                            return
            else:
                pass
        
        url = headers['Host'] + resource.decode()
        if url in self.accesses:
            self.accesses[url].append(time())
        else:
            self.accesses[url] = [time()]
        
        to_cache = False
        curr_time = time()
        if len(self.accesses[url]) > 3:
            for t in self.accesses[url]:
                count = 0
                if t > curr_time - 300:
                    count += 1
                to_cache = (count > 3)

        if filename in self.cache_header_dict:
            print("####################### USING CACHE #######################")
            

            if 'must-revalidate' in self.cache_header_dict[filename]['Cache-control']:

                date = self.cache_header_dict[filename]['Date']
                c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                c.connect((headers['Host'].split(':')[0],
                           int(headers['Host'].split(':')[1])))

                req = request_text.decode()[:-2]
                req += "If-Modified-Since: " + date + "\r\n\r\n"
                req = req.encode()

                c.send(req)
                temp_string = c.recv(4096)
                response_file_string = ""
                response_header_string = temp_string.decode()

                temp_string = c.recv(4096)
                while temp_string:
                    response_file_string += temp_string.decode()
                    temp_string = c.recv(4096)

                c.close()

                print("RESPONSE HEADER => ", response_header_string)
                print("RESPONSE => ", response_file_string)

                if '530' in response_header_string:
                    self.cache_file_dict[filename] = base64.b64encode(
                        response_file_string.encode()).decode()

                    self.cache_header_dict[filename] = {}

                    self.cache_header_dict[filename]['Response'] = response_header_string.split('\r\n')[
                        0]
                    self.cache_header_dict[filename]['Server'] = response_header_string.split('\r\n')[
                        1].split(':')[1].lstrip()
                    self.cache_header_dict[filename]['Date'] = response_header_string.split('\r\n')[
                        2].split(':', 1)[1].lstrip()
                    self.cache_header_dict[filename]['Cache-control'] = response_header_string.split('\r\n')[
                        3].split(':')[1].lstrip()

                elif '304' in response_header_string:
                    print("CACHE CAN BE USED. NO MODIFICATION AFTER REVALIDATION.")

            else:
                print("USE CACHE. NO REVALIDATION")

        else:
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # try:

            c.connect((headers['Host'].split(':')[0],
                       int(headers['Host'].split(':')[1])))

            # SEND REQUEST FROM CLIENT TO OUTSIDE SERVER
            c.send(request_text)

            temp_string = c.recv(4096)
            response_file_string = ""
            response_header_string = temp_string.decode()
            temp_string = ""

            temp_string = c.recv(4096)
            while temp_string:
                response_file_string += temp_string.decode()
                temp_string = c.recv(4096)

            c.close()

            # RESPONSE STRING CONTAINS THE RESPONSE CODE (200/404/..)
            # AND THE REQUESTED FILE CONTENTS

            print("RESPONSE => ", response_file_string)

            if '200' in response_header_string and to_cache:

                if(len(self.cache_filename) > 3):

                    name = self.cache_filename[0]
                    del self.cache_filename[0]
                    self.cache_file_dict.pop(name)
                    self.cache_header_dict.pop(name)

                self.cache_filename.append(filename)
                self.cache_file_dict[filename] = base64.b64encode(
                    response_file_string.encode()).decode()
                self.cache_header_dict[filename] = {}

                self.cache_header_dict[filename]['Response'] = response_header_string.split('\r\n')[
                    0]
                self.cache_header_dict[filename]['Server'] = response_header_string.split('\r\n')[
                    1].split(':')[1].lstrip()
                self.cache_header_dict[filename]['Date'] = response_header_string.split('\r\n')[
                    2].split(':', 1)[1].lstrip()
                self.cache_header_dict[filename]['Cache-control'] = response_header_string.split('\r\n')[
                    3].split(':')[1].lstrip()
                
            if not to_cache:
                conn.send(b"HTTP/1.1 200 OK\n\n" + response_file_string.encode())
                conn.close()
                return 


        # SEND RESPONSE TO CLIENT
        conn.send(b"HTTP/1.1 200 OK\n\n" + base64.b64decode(self.cache_file_dict[filename]))
        conn.close()

if __name__ == '__main__':
    proxy = ProxyServer()
    proxy.listenForClient()
