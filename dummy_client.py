import requests
import base64

http_proxy  = "http://127.0.0.1:20100"

proxyDict = {
              "http"  : http_proxy,
            }

r = requests.get('http://127.0.0.1:20106/sample.txt', proxies=proxyDict)
if r.status_code == 407:
    username = input("Enter username: ")
    passwd = input("Enter password: ")
    headers = {'Authorization': b"Basic " + base64.b64encode(str.encode(username + ':' + passwd))}
    r = requests.get('http://127.0.0.1:20106/sample.txt', headers=headers, proxies=proxyDict)
print(r.status_code)
print(r.text)
