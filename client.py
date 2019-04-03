# import requests
# import base64

# http_proxy  = "http://127.0.0.1:20100"

# proxyDict = {
#               "http"  : http_proxy,
#             }

# r = requests.get('http://127.0.0.1:20106/sample.txt', proxies=proxyDict)
# if r.status_code == 407:
#     username = input("Enter username: ")
#     passwd = input("Enter password: ")
#     headers = {'Authorization': b"Basic " + base64.b64encode(str.encode(username + ':' + passwd))}
#     r = requests.get('http://127.0.0.1:20106/sample.txt', headers=headers, proxies=proxyDict)
# print(r.status_code)
# print(r.text)

import socket

url = input("Enter URL: ")

l = url.split('/')
addr = '/'.join(l[:-1])
print(addr)
resource = '/' + l[-1]
l = addr.split(':')
port = l[-1]
host = ':'.join(l[:-1])
host = addr.lstrip('htp:/')
# print(host)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 20094))
sock.connect(('127.0.0.1', 20100))
sock.send(str.encode("GET " + resource + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"))
response = sock.recv(4096)
print(response)

