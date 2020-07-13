# ExtensiveAutomation

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/extensiveautomation-server)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Python%20Package/badge.svg)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Docker%20Image/badge.svg)

| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2020  Denis Machard <d.machard@gmail.com> |
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
* [Server Installation](#installation)
	* [PyPI package](#pypi-package)
	* [Docker image](#docker-image)
	* [Source code](#source-code)
	* [Adding plugins](#adding-plugins)
* [Connecting to server](#connecting-to-server) 
	* [Connection using Curl](#connection-using-curl)
	* [Connection using Web client](#connection-using-web-client)
	* [Connection using App client](#connection-using-app-client)
* [Understand the Data Storage](#understand-the-data-storage)
	* [Get the location](#get-the-location)
* [Automation using the Web Interface](#automation-using-the-web-interface)
    * [Tasks execution](#tasks-execution)
    * [Display tasks result](#display-tasks-result)
* [Automation using the REST API](#automation-using-the-rest-api) 
	* [Get api secret key](#get-api-secret-key)
	* [Run task from sample](#run-task-from-sample)
	* [Get task logs](#get-task-logs)
* [Write and working with tasks](#write-and-working-with-tasks)
	* [Basic task](#basic-task)
	* [SSH task](#ssh-task)
	* [HTTP task](#http-task)
* [More security](#more-security)
	* [Adding ReverseProxy](#reverse-proxy)
	* [LDAP users authentication](#ldap-users-authentication)

## Introduction

**ExtensiveAutomation**  is a generic automation framework in 100% Python for integration, regression and end-to-end usages. The framework provided a rich and collaborative workspace environment. 

## Server Installation

### PyPI package

1. Run the following command

        python3 -m pip install extensiveautomation_server

2. Type the following command on your shell to start the server

        extensiveautomation --start

3. Finally, check if the [server is running fine](#connection-to-server-with-curl).

### Docker image

1. Downloading the image

        docker pull extensiveautomation/extensiveautomation-server:latest

2. Start the container

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 \
                   --name=extensive extensiveautomation

   If you want to start the container with persistant tests data, go to [Docker Hub](https://hub.docker.com/r/extensiveautomation/extensiveautomation-server) page.

3. Finally, check if the [server is running fine](#connection-to-server-with-curl).
   
### Source code
 
1. Clone this repository on your linux server

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
        cd extensiveautomation-server/
        
2. As precondition, install the additional python libraries with `pip` command: 
   
        python3 -m pip install wrapt pycnic lxml jsonpath_ng pyyaml

3. Start the server. On linux the server is running as daemon.

        cd src/
        python3 extensiveautomation.py --start
        
4. Finally, check if the [server is running fine](#connection-to-server-with-curl).
 
### Adding plugins

Plugins allow to interact with the system to be controlled. But by default the server is provided without plugins. So you need to install them one by one according to your needs.

* [CLI plugin (ssh)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)

        pip install extensiveautomation_plugin_cli
        ./extensiveautomation --reload
         
* [WEB plugin (http/https)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web)

        pip install extensiveautomation_plugin_web
        ./extensiveautomation --reload
         
* [GUI plugin (selenium, sikulix and adb)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)
* [And many others...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Connecting to server

### Connection using Curl

1. Please to take in consideration the following points:
	
	 - The server is running on the following tcp ports (don't forget to open these ports on your firewall):
	    - tcp/8081: REST API
	    - tcp/8081: Websocket tunnel for app client
	    - tcp/8082: Websocket tunnel for agents
	 - The `admin`, `tester` and `monitor` users are available and the default passoword is `password`. 
	 - The `Common` project is created by default, attached to the previous users.
	 - Swagger for the REST API is available in the `scripts/swagger` folder.
    
2. Checking if the REST api working fine with curl or postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'

   success response:

        {
            "cmd": "/session/login", 
            "message": "Logged in", 
            "session_id": "MjA1OWI1OTc1MWM0NDU2NDg4MjQxMjRjNWFmN2FkNThhO", 
            "expires": 86400, 
            "user_id": 1, 
            "levels": ["Administrator"], 
            "project_id": 1, 
            "api_login": "admin", 
            "api_secret": "6977aa6a443bd3a6033ebb52557cf90d24c79857", 
            "client-available": false, 
            "version": "",
            "name": ""
        }

### Connection using Web client

To use the server from the web interface, please to read the following [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-webclient#web-interface-for-extensiveautomation).
This user interface enables to:
- manage users
- manage projects
- manage variables
- and more...

### Connection using App client
  
To use the server from the rich application, please to read the following [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-appclient#qt-application-for-extensiveautomation).

## Understand the Data Storage

### Get the location

All data necessary  for the server is stored in a specific folder.
The location of the storage can be found with the following command:

        python3 extensiveautomation.py --datastorage
        /<install_project>/ea/var/

## Automation using the Web Interface

Install the web interface as describe on the page [Connection to server with the web client](#connection-to-server-with-the-web-client).

### Tasks executions

Go to the menu `Automation > Task > Add Task`

Select the your test and click on the button `CREATE`

### Display tasks result

Go to the menu `Automation > Run` and display Logs


## Automation using the REST API

### Get api secret key

Get the API secret for the user admin

        python3 extensiveautomation.py --apisecret admin
        API key: admin
        API secret: 6977aa6a443bd3a6033ebb52557cf90d24c79857

### Run task from sample

Tasks samples are available in the default data storage <projectpath_install>/var/tests/1/

Curl command:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"project-id": 1,"test-extension": "yml", "test-name": "01_testunit",
              "test-path": "YAML_samples/Framework_Tests/"}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/tasks/schedule
              
Success response:

        {
            "cmd": "/tasks/schedule",
            "message": "background", 
            "task-id": 2,
            "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
            "tab-id": 0,
            "test-name": "01_testunit"
        }
        
### Get task logs

Run the following command with your test id:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", "project-id": 1}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/results/details
        
Success response:

        {
            "cmd": "/results/details",
            "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
            "test-status": "complete", 
            "test-verdict": "pass", 
            "test-logs": "10:50:10.7241 task-started
            10:50:10.7243 script-started 01_testunit
            10:50:10.7309 script-stopped PASS 0.007
            10:50:10.7375 task-stopped 0.006909608840942383", 
            "test-logs-index": 156
        }

## Write and working with tasks

### Basic task

This example describe how to write a basic testunit with some parameters and python code
This example is available in the data storage in "samples" folder.

        properties:
          parameters:
          - name: hello
            value: bonjour
        testunit: |
            def description(self):
                self.step1 = self.addStep(summary="step sample")
                
            def definition(self):
                self.step1.start()
                self.info( "%s" % input("hello") )
                self.step1.setPassed()
                
            def cleanup(self, aborted):
                pass

### SSH task

This example describe how to write a ssh task to execute some commands remotely using SSH.

The SSH plugin must be installed, please refer to [Adding plugins](#adding-plugins).

Two actions are available to create SSH task.
- send_commands.yml: execute commands remotely using SSH 
- send_expect.yml: automate your SSH session by interacting with-it

Examples are available in the data storage in `./samples/ssh/` folder.

        testplan:
        - alias: execute commands remotely using SSH 
          file: Common:actions/ssh/send_commands.yml
          parameters:
          - name: ssh-hosts
            value:
              - ssh-host: 10.0.0.55
                ssh-login: root
                ssh-password: ESI23xgx4yYukF9rsA1O
          - name: ssh-commands
            value: |-
                echo "hello world" >> /var/log/messages
                echo "hola mondu" >> /var/log/messages

### HTTP task

This example describe how to write a HTTP task to send HTTP requests.

The WEB plugin must be installed, please refer to [Adding plugins](#adding-plugins).

One action is available to create HTTP task.
- curl.yml: send http requests and analyse response

Examples are available in the data storage in `./samples/http/` folder.

        testplan:
        - alias: Get my origin IP
          file: Common:actions/http/curl.yml
          parameters:
          - name: curl-hosts
            value: https://httpbin.org/ip
          - name: response-body-json
            value: |
                origin -> [!CAPTURE:externalip:]
        - alias: Log external IP
          file: Common:actions/cache/log.yml
          parameters:
          - name: key
            value: externalip
            
## More security

### Adding reverse proxy

Adding a reverse proxy in the front of server enables to expose only one tcp port (8080) 
and to have a TLS link between the client and the server. 
Also, the default behaviour of the QT client and toolbox is to try to connect 
on the tcp/8080 port with ssl (can be modifed).

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
         
### LDAP users authentication

By default, users are authenticated locally from database (by checking hash password).
This behavior can be modified by using a remote authentication server. In this mode, you always need to add users in the local database.

Follow this procedure to enable LDAP authentication:

1. Install python dependancies with the `pip` command:

        python3 -m pip install ldap3

2. Configure the `settings.ini`  file to enable ldap authentication and other stuff

        [Users_Session]
        
        ; enable ldap user authentication for rest api session only
        ; 0=disable 1=enable
        ldap-authbind=1
        ; remote addresses of your ldap servers
        ; ldaps://127.0.0.1:636 
        ldap-host=[ "ldap://127.0.0.1:389" ]
        ; username form
        ; uid=%%s,ou=People,dc=extensive,dc=local
        ldap-dn=[ "uid=%%s,ou=People,dc=extensive,dc=local" ]


3. Restart the server

        cd src/
        python3 extensiveautomation.py --stop
        python3 extensiveautomation.py --start
        
4. Check the new user authentication method

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'
