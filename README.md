# Proxy Server
Multi-threaded HTTP Proxy Server using sockets. Implemented in Python3

## Run
`python3 server.py`  
`python3 proxy.py`  
`python3 client.py`

## Features

* Server takes in port number as input
* Server handles GET & POST requests
* Basic Access Authentication implemented. For authentication username is `admin` and password is `password`
* Client takes destination url as input
* URL blacklisting can be achieved by specifying it in proxy/blacklist.txt. Handles CIDR format.
* Frequently accessed files are cached on the server

## Directory Structure
```
.
├── Client
│   └── client.py
├── Proxy
│   ├── blacklist.txt
│   └── proxy.py
├── README.md
└── Server
    └── server.py
```

## License
The MIT License https://rohanc.mit-license.org/  
Copyright &copy; 2019 Rohan Chacko <rohanchacko007@gmail.com>
