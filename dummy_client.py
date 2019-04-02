import requests

http_proxy  = "http://127.0.0.1:20100"
https_proxy = "https://127.0.0.1:20100"
ftp_proxy   = "ftp://127.0.0.1:20100"

proxyDict = { 
              "http"  : http_proxy, 
              "https" : https_proxy, 
              "ftp"   : ftp_proxy
            }

payload = {'key1': 'value1', 'key2': 'value2'}
r = requests.get('http://127.0.0.1:20105/', params=payload, proxies=proxyDict)
