import socket
import base64

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
sock.bind(('', 20096))
sock.connect(('127.0.0.1', 20100))
sock.send(str.encode("GET " + resource + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n"))
response = sock.recv(4096)
lines = response.split(b'\n')
if b'407' in lines[0]:
    username = input("Enter username: ")
    passwd = input("Enter password: ")
    auth_string = base64.b64encode(str.encode(username + ':' + passwd))
    sock.send(b"GET " + resource.encode() + b" HTTP/1.1\r\nHost: " + host.encode() + b"\r\nAuthorization: Basic " + auth_string + b"\r\n\r\n")
    response = sock.recv(4096)
print(response.decode())
