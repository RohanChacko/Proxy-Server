# Proxy-Server
Multi-threaded HTTP Proxy Server using sockets


# Run
`python3 server.py`  
`python3 proxy.py`  
`python3 dummy_client.py`

# Issues
* ~~Need to fix small things in caching and test it~~
* Multiple clients are not able to stay connected simultaneously
* Need to do basic authentication
* CIDR format
* Binary files cannot be sent in GET Request. Need to do corresponding checking
* Need to send the file to client side from proxy
