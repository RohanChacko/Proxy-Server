# Proxy-Server
Multi-threaded HTTP Proxy Server using sockets


# Compile
`gcc -pthread -o proxy proxy_server.c`  
`gcc -pthread -o client client.c`

# Run
`./proxy`  
`./client`

# Issues
* When unauthorized client port connects with proxy, error message received by client has extra random characters in receive buffer 
