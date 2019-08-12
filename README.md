# ExtensiveAutomation

| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2019  Denis Machard <d.machard@gmail.com> |
| License |  LGPL2.1 |
| Homepage |  https://www.extensiveautomation.org/ |
| Docs |  https://extensiveautomation.readthedocs.io/en/latest/ |
| Github |  https://github.com/ExtensiveAutomation |   
| Docker Hub | https://hub.docker.com/u/extensiveautomation |   
| PyPI |  https://pypi.org/project/extensiveautomation-server/ |
| Google Users | https://groups.google.com/group/extensive-automation-users |
| Twitter | https://twitter.com/Extensive_Auto |
| | |

## Table of contents
* [Introduction](#introduction)
* [Installation](#installation)
	* [PyPI package](#pypi-package)
	* [Docker image](#docker-image)
	* [Source code](#source-code)
* [Plugins](#plugins)
* [Adding ReverseProxy](#reverse-proxy)

## Introduction

**ExtensiveAutomation**  is a generic automation framework for integration, regression and end-to-end usages. The framework provided a rich and collaborative workspace environment. 
The server can run on both Python 2 and Python 3, and also run on Linux and Windows.

## Installation

### PyPI package

1. Run the following command

        pip install extensiveautomation_server

2. Type the following command on your shell to start the server

        extensiveautomation --start
        
3. Now you can use the qt/web client or REST api to interact with the server   
   - tcp/8081 enable to use the REST api of the server
   - tcp/8082 is used by the qt client to have a bidirectionnal link
   - tcp/8083 is used by agents to have a bidirectionnal link        
   
4. Checking if the REST api working fine with curl or postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'
    
    The swagger of the api is available in the folder `scripts/swagger`:
     - common_restapi.yaml
     - admin_restapi.yaml
     - tester_restapi.yaml
     
   The following users are available by default:
    - admin
    - tester
    - monitor
    
   The default password is `password`.
   
### docker image

1. Downloading the image

        docker pull extensiveautomation/extensiveautomation-server:20.0.0

2. Start the container without persistance for tests data

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name=extensive extensiveautomation
        
3. Now you can use the qt/web client or REST api to interact with the server   
   - tcp/8081 enable to use the REST api of the server
   - tcp/8082 is used by the qt client to have a bidirectionnal link
   - tcp/8083 is used by agents to have a bidirectionnal link
   
4. Checking if the REST api working fine with curl or postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'
    
    The swagger of the api is available in the folder `scripts/swagger`:
     - common_restapi.yaml
     - admin_restapi.yaml
     - tester_restapi.yaml
     
   The following users are available by default:
    - admin
    - tester
    - monitor
    
   The default password is `password`.
   
 ### Source code
 
1. Clone this repository on your linux server

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
 
2. As precondition, install the additional python libraries with `pip` command: 
   
    * Python3 environment
    
            pip install wrapt pycnic lxml jsonpath_ng
          
    * Python2 environment, the `libxslt` library must be installed
    
            pip install wrapt scandir pycnic lxml jsonpath_ng
        
3. Finally start the server. On linux the server is running as daemon.

        cd src/
        python extensiveautomation.py --start

   REST API is running on port tcp/8081.
   
   The following users are available by default:
    - admin
    - tester
    - monitor
    
   The default password is `password`.
   
4. Checking if the server is running fine.

        cd src
        python extensiveautomation.py --status
        Extensive Automation is running
        
5. Checking if the REST api working fine with curl command.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'
    
    The swagger of the api is available in the folder `scripts/swagger`:
     - common_restapi.yaml
     - admin_restapi.yaml
     - tester_restapi.yaml

## Plugins

Plugins allow to interact with the system to be controlled. But by default the server is provided without plugins. So you need to install them one by one according to your needs.

* [CLI plugin (ssh)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)
* [WEB plugin (http/https)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web)
* [GUI plugin (selenium, sikulix and adb)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)
* [And many others...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Adding reverse proxy

Adding a reverse proxy the from of server enables to expose only one tcp port (8080) 
and to have a tls link between the client and the server. 
Also, the default behaviour of the QT client and toolbox is to try to connect 
on the tcp/8080 port (can be modifed).

If you want to install a reverse proxy, please to follow this procedure.

1. Install the example provided `scripts\reverseproxy\extensiveautomation_api.conf` in your apache instance. If you install the reverse proxy on a new server, don't forget to replace the 127.0.0.1 address by the ip of your extensive server.

        Listen 8080

        <VirtualHost *:8080>
          SSLEngine on

          SSLCertificateFile /etc/pki/tls/certs/localhost.crt
          SSLCertificateKeyFile /etc/pki/tls/private/localhost.key

          LogLevel warn
          ErrorLog  /var/log/extensiveautomation_api_error_ssl_rp.log
          CustomLog /var/log/extensiveautomation_api_access_ssl_rp.log combined

          Redirect 307 / /rest/session/login

          ProxyPass /rest/ http://127.0.0.1:8081/
          ProxyPassReverse /rest/ http://127.0.0.1:8081/
          
          ProxyPass /wss/client/ ws://127.0.0.1:8082 disablereuse=on
          ProxyPassReverse /wss/client/ ws://127.0.0.1:8082 disablereuse=on

          ProxyPass /wss/agent/ ws://127.0.0.1:8083 disablereuse=on
          ProxyPassReverse /wss/agent/ ws://127.0.0.1:8083 disablereuse=on
        </VirtualHost>

    With this configuration in apache, the REST API is now running on the port tcp/8080 (tls).

2. Checking if the REST api working fine with curl command.

       curl -X POST https://127.0.0.1:8080/rest/session/login --insecure \ 
         -H "Content-Type: application/json" \
         -d '{"login": "admin", "password": "password"}'
