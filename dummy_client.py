import requests

http_proxy  = "http://127.0.0.1:20100"

proxyDict = {
              "http"  : http_proxy,
            }

r = requests.get('http://127.0.0.1:20105/sample.txt', proxies=proxyDict)
