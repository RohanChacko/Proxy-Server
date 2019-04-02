import socket
from time import gmtime, strftime
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
from http.server import BaseHTTPRequestHandler
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

        self.cache_file_dict = {}
        self.cache_header_dict = {}
        self.cache_filename = []

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
        headers_list = [i.decode() for i in request_text.split(
            b'\r\n') if re.match('[a-zA-Z]+: ', i.decode())]
        print(headers_list)
        headers = {h.split(': ')[0]: h.split(': ')[1] for h in headers_list}
        print(headers)
        filename = [i.decode() for i in request_text.split(b'\r\n')
                    ][0].split('?')[0].split('/')[-1]

        for b in self.blacklist:
            if headers['Host'] in b:
                print("ERROR: BLACKLISTED SITE")
                ####################### CLOSE CONNECTION #######################
            else:
                pass

        if filename in self.cache_header_dict:
            print("##### USING CACHE #####")
            print(self.cache_header_dict[filename])
            print(self.cache_file_dict[filename])

            if 'must-revalidate' in self.cache_header_dict[filename]:
                # date = cache_header['date']                           # NEED TO CORRECT THIS
                c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                c.connect((headers['Host'].split(':')[0],
                           int(headers['Host'].split(':')[1])))

                req = request.text.decode()[:-2]
                req += "If-Modified-Since: " + date + "\r\n"
                req = req.encode()

                c.send(req)
                temp_string = c.recv(4096)
                response_string = ""

                while temp_string:
                    response_string += temp_string.decode()
                    temp_string = c.recv(4096)

                c.close()

                print("RESPONSE => ", response_string)

                if '200' in response_string:
                    self.cache_header_dict[filename] = response_string
                    self.cache_file_dict[filename] = base64.b64encode(
                        response_string)
                else:
                    print("Error during file transmission")

                c.close()

            else:
                pass

        else:
            c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # try:

            c.connect((headers['Host'].split(':')[0],
                       int(headers['Host'].split(':')[1])))

            # SEND REQUEST FROM CLIENT TO OUTSIDE SERVER
            c.send(request_text)

            temp_string = c.recv(4096)
            response_string = ""

            while temp_string:
                response_string += temp_string.decode()
                temp_string = c.recv(4096)

            c.close()

            # RESPONSE STRING CONTAINS THE RESPONSE CODE (200/404/..)
            # AND THE REQUESTED FILE CONTENTS

            print("RESPONSE => ", response_string)

            if '200' in response_string:

                if(len(self.cache_filename) > 3):

                    name = self.cache_filename[0]
                    del self.cache_filename[0]
                    self.cache_file_dict.pop(name)
                    self.cache_header_dict.pop(name)

                self.cache_filename.append(filename)
                self.cache_file_dict[filename] = base64.b64encode(
                    response_string.encode()).decode()
                self.cache_header_dict[filename] = response_string

            # SEND RESPONSE TO CLIENT


if __name__ == '__main__':
    proxy = ProxyServer()
    proxy.listenForClient()
