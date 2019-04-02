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
from io import StringIO
import re

class ProxyServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('', 20100))
        self.server_socket.listen(10)
        with open('blacklist.txt', 'r') as f:
            self.blacklist = f.readlines()

    def listenForClient(self):
        while True:
            (clientSocket, client_address) = self.server_socket.accept()
            d = threading.Thread(name="proxy_client", target=self.proxy_thread, args=(clientSocket, client_address))
            d.daemon = True
            d.start()
        self.shutdown(0, 0)
    
    def proxy_thread(self, conn, addr):
        request_text = conn.recv(1024)
        headers_list = [i.decode() for i in request_text.split(b'\r\n') if re.match('[a-zA-Z]+: ', i.decode())]
        print(headers_list)
        headers = {h.split(': ')[0]:h.split(': ')[1]  for h in headers_list}
        print(headers)
        for b in self.blacklist:
            if headers['Host'] in b:
                print("BLACKLISTED SITE")

if __name__ == '__main__':
    proxy = ProxyServer()
    proxy.listenForClient()
