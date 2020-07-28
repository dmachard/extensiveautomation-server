# ExtensiveAutomation

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/extensiveautomation-server)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Python%20Package/badge.svg)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Docker%20Image/badge.svg)

**ExtensiveAutomation** enable you to create custom workflows to automate your project.
 - a workflow is the combination of differents actions.
 - an action is individual python code source with enriched parameters.

The architecture is composed of 3 parts:
 - [automation server](https://github.com/ExtensiveAutomation/extensiveautomation-server)
 - [web client (optional)](https://github.com/ExtensiveAutomation/extensiveautomation-webclient)
 - [remote agents (optional)](https://github.com/ExtensiveAutomation/extensiveautomation-agent)
 
## Table of contents
* [Server Installation](#server-installation)
    * [About the server](#about-the-server)
	* [PyPI package](#pypi-package)
	* [Docker image](#docker-image)
	* [Source code](#source-code)
	* [Install plugins](#install-plugins)
* [Server is running fine](#server-is-running-fine) 
	* [Testing using Curl](#testing-using-curl)
* [Understand the Data Storage](#understand-the-data-storage)
	* [Get the location](#get-the-location)
* [Working with actions](#working-with-actions)
	* [About actions](#about-actions)
	* [HelloWorld action](#helloworld-action)
* [Working with workflows](#working-with-workflows)
	* [About workflows](#about-workflows)
	* [HelloWorld workflow](#helloworld-workflow)
	* [SSH workflow](#ssh-workflow)
	* [HTTP workflow](#http-workflow)
	* [Selenium workflow](#selenium-workflow)
	* [Sikulix workflow](#sikulix-workflow)
* [Automation using the Web Interface](#automation-using-the-web-interface)
    * [About Web Client](#about-web-client)
    * [Schedule a job](#schedule-a-job)
    * [Get job logs](#get-job-logs)
* [Automation using the REST API](#automation-using-the-rest-api) 
    * [About API](#about-api)
	* [Get api secret key](#get-api-secret-key)
	* [Schedule a job](#schedule-a-job)
	* [Get job logs](#get-job-logs)
* [More security](#more-security)
	* [Adding ReverseProxy](#reverse-proxy)
	* [LDAP users authentication](#ldap-users-authentication)
* [Migration from old version](#migration-from-old-version)
    * [Tests convertion to YAML format](#tests-convertion-to-yaml-format)
* [About](#about)

## Server Installation

### About the server

The server is the main part of the **ExtensiveAutomation** project. 

It's is running on the following tcp ports:
- tcp/8081: REST API
- tcp/8082: Websocket tunnel for app client
- tcp/8083: Websocket tunnel for agents

A user account is required, you can use the default ones or create your own account.
Default user accounts and passwords:
- admin/password
- tester/password
- monitor/password

YAML files storage can be split into different workspaces. 
The `Common` workspace is available by default, attached to the previous users.
 
### PyPI package

1. Run the following command

    ```bash
    python3 -m pip install extensiveautomation_server
    ```
    
2. Type the following command on your shell to start the server

    ```bash
    extensiveautomation --start
    ```
    
3. Finally, check if the [server is running fine](#connection-to-server-with-curl).

### Docker image

1. Downloading the image

    ```bash
    docker pull extensiveautomation/extensiveautomation-server:latest
    ```
    
2. Start the container

    ```bash
    docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 \
    --name=extensive extensiveautomation
    ```
    
   If you want to start the container with persistant tests data, go to [Docker Hub](https://hub.docker.com/r/extensiveautomation/extensiveautomation-server) page.

3. Finally, check if the [server is running fine](#connection-to-server-with-curl).
   
### Source code
 
1. Clone this repository on your linux server

    ```bash
    git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
    cd extensiveautomation-server/
    ```
    
2. As precondition, install the additional python libraries with `pip` command: 
   
    ```bash
    python3 -m pip install wrapt pycnic lxml jsonpath_ng pyyaml
    ```
    
3. Start the server. On linux the server is running as daemon.

    ```bash
    cd src/
    python3 extensiveautomation.py --start
    ```
      
4. Finally, check if the [server is running fine](#connection-to-server-with-curl).
 
### Install plugins

You can add plugins to your extensive automation server to add more functionnalities like 
make http requests, send ssh commands.

By default the server comes without plugins so you need 
to install them one by one according to your needs.

| Plugins | Description |
| ------------- | ------------- | 
| [CLI](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)  | This plugin enable to execute commands in a remote system throught the SSH protocol. |
| [WEB](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web) | This plugin enable to send http request to a remote web server through the HTTP protocol. This plugin is based on the curl command. |
| [GUI](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)  | This plugin enable to interact with graphical user interface. This plugin is based on selenium, sikulix or adb for android. |

[And many others (old ones)...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Server is running fine

### Testing using Curl

Checking if the REST api working fine using curl or postman.

```bash
curl -X POST http://127.0.0.1:8081/session/login \
-H "Content-Type: application/json" \
-d '{"login": "admin", "password": "password"}'
```

success response:

```json
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
```

## Understand the Data Storage

### Get the location

All data necessary  for the server is stored in a specific folder.
The location of the storage can be found with the following command:

```bash
extensiveautomation --show-data-path
/<install_project>/ea/var/
```

Data storage overview:

```bash
var/
  tests/
    <project_id>/
        [...yaml files...]
  testsresult/
    <project_id>/
        <result_id>/
  logs/
    output.log
  data.db
```

## Working with actions

Action is individual python code source with parameters and must be defined with YAML file.

### About actions

You can create your own actions but some actions are available by default in the folder `/actions`
Actions must be defined with YAML file.

The default ones:
- [basic/helloworld.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#basichelloworldyml)
- [basic/wait.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#basicwaityml)
- [cache/log.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#cachelogyml)
- [generator/random_string.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#generatorrandom_stringyml)
- [generator/random_integer.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#generatorrandom_integeryml)

Additional actions are available with plugins:
- [WEB plugin actions](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web#about-actions)
- [CLI plugin actions](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli#about-actions)
- [GUI plugin actions](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui#about-actions)

### HelloWorld action

This following action is available in the data storage in "/actions/basic/" folder.
This basic action shows how to write python source code with parameters in YAML format.

```yaml
properties:
  parameters:
   - name: msg
     value: hello world
python: |
    class HelloWorld(Action):
        def definition(self):
            self.info(input("msg"))
    HelloWorld().execute()
```

## Working with workflows

A workflow is the combination of differents actions and must be defined with YAML file.
Parameters from actions can be easily overwritten and conditions between actions can be defined.

### About workflows

You can create your own workflows but some workflows are available by default in the folder `/workflows`
Workflows must be defined with YAML file.

The default ones:
- [basic/helloworld.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_workflows.md#basichelloworldyml)
- [basic/wait.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_workflows.md#basicwaityml)
- [generators/random.yml](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_workflows.md#generatorsrandomyml)

Additional workflows are available with plugins:
- [WEB plugin workflows](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web#about-workflows)
- [CLI plugin workflows](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli#about-workflows)
- [GUI plugin workflows](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui#about-workflows)

### HelloWorld workflow

This following workflow is available in the data storage in "/workflows/basic/" folder.
This workflow shows how to use actions with updated parameters.

```yaml
actions:
- description: HelloWorld
  file: Common:actions/basic/helloworld.yml
  parameters:
   - name: msg
     value: Hola Mundo
```
     
### SSH workflow

This example describe how to write a ssh workflow to execute some commands remotely using SSH.
The SSH plugin must be installed, please refer to the chapter [Install plugins](#install-plugins).

The following example show how to execute remote ssh commands.

```yaml
actions:
- description: execute commands remotely using SSH 
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
```

If your want to run the previous workflow with a remote agent:
- you must deploy and register a `ssh` agent in your automation server
- you must define the agent to use in your worflow like below

```yaml
properties:
  parameters:
    - name: agent-curl
      value:
        name: 13ae34f7-e2f6-40b6-9c87-6c275423127e
```

Additional examples are available in the data storage `./workflows/ssh/`.

### HTTP workflow

This example describe how to write a HTTP workflow to send HTTP requests.
The WEB plugin must be installed, please refer to the chapter [install plugins](#install-plugins).

The following example show how to send a http request 
and waiting response with specific json key.

```yaml
actions:
- description: Get my origin IP
  file: Common:actions/http/curl.yml
  parameters:
   - name: curl-hosts
     value: https://httpbin.org/ip
   - name: response-body-json
     value: |
        origin -> [!CAPTURE:externalip:]
- description: Log external IP
  file: Common:actions/cache/log.yml
  parameters:
   - name: key
     value: externalip
```

If your want to run the previous workflow with a remote agent:
- you must deploy and register a `curl` agent in your automation server
- you must define the agent to use in your worflow like below

```yaml
properties:
  parameters:
    - name: agent-curl
      value:
        name: 13ae34f7-e2f6-40b6-9c87-6c275423127e
```

Additional examples are available in the data storage `./workflows/http/`.

### Selenium workflow

This example describe how to write a Selenium workflow.

Some prerequisites to follow:
- The `GUI plugin` must be installed on your automation server, please refer to the chapter [install plugins](#install-plugins).
- Agent must be deployed with the `selenium` plugin [installed](https://github.com/ExtensiveAutomation/extensiveautomation-agent-plugin-selenium) 
- Your agent must be [running](https://github.com/ExtensiveAutomation/extensiveautomation-agent#running-agent).

The following example show how to open the web browser, 
that loads the url www.google.com and finally  close-it after.

```yaml
properties:
  parameters:
    - name: agent
      value:
        name: 13ae34f7-e2f6-40b6-9c87-6c275423127e
    - name: browser
      value: chrome
actions:
- description: open browser
  file: Common:actions/selenium/openbrowser.yml
  id: 1
  parameters:
   - name: url
     value: https://www.google.com
- description: close browser
  file: Common:actions/selenium/closebrowser.yml
  id: 2
  parent: 1
```

Additionals examples are available in the data storage `./workflows/selenium/`.

### Sikulix workflow

This example describe how to write a Sikulix workflow. Sikulix is nice to 
simulate keyboard and mouse interactions on your system.

Some prerequisites to follow:
- The `GUI plugin` must be installed, please refer to the chapter [install plugins](#install-plugins).
- Agent must be deployed with the `sikulix` plugin [installed](https://github.com/ExtensiveAutomation/extensiveautomation-agent-plugin-sikulix) 
- Your agent must be [running](https://github.com/ExtensiveAutomation/extensiveautomation-agent#running-agent).

The following example show how to execute `Windows + R` shorcut and run a command.

```yaml
properties:
  parameters:
    - name: agent
      value:
        name: 13ae34f7-e2f6-40b6-9c87-6c275423127e
actions:
- description: Type Windows+R on keyboard 
  file: Common:actions/sikulix/type_shorcut.yml
  id: 1
  parameters:
   - name: key
     value: KEY_WIN
   - name: other-key
     value: r
- description: "Type text: cmd"
  file: Common:actions/sikulix/type_text.yml
  id: 1
  parent: 1
  parameters:
   - name: text
     value: cmd
```

## Automation using the Web Interface

### About Web Client

The [web client](https://github.com/ExtensiveAutomation/extensiveautomation-webclient#web-interface-for-extensiveautomation) is optional because you can do everything from the REST API of the server.
But on some cases, it's more user friendly to use the web interface to manage:
- users
- projects
- variables
- and more...

### Schedule a job

Go to the menu `Automation > Job > Add Job`

Select the your action or worflow and click on the button `CREATE`

### Get job logs

Go to the menu `Automation > Executions` and display Logs


## Automation using the REST API

### About API

You can do everything from the REST API, below a small overview.
Take a look to the [swagger](https://github.com/ExtensiveAutomation/extensiveautomation-server/tree/master/src/ea/scripts/swagger).
    
### Get api secret key

Get the API secret for the user admin

```bash
extensiveautomation --generate-api-key admin
API key: admin
API secret: 6977aa6a443bd3a6033ebb52557cf90d24c79857
```

### Schedule a job

Make a POST on `/v1/jobs` with basic auth to create a job wich will execute your actions or workflows.

Copy/Paste the following curl command:

```bash
curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
-d '{"yaml-file": "/workflows/basic/helloworld.yml"}' \
-H "Content-Type: application/json" \
-X POST http://127.0.0.1:8081/v1/jobs?workspace=1
```
             
Success response:

```json
{
    "cmd": "/v1/jobs",
    "message": "background", 
    "job-id": 2,
    "execution-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a"
}
```
       
### Get job logs

Make a GET on `/v1/executions` with basic auth to get logs generated by the job.

Copy/Paste the following curl command:

```bash
curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
"http://127.0.0.1:8081/v1/executions?workspace=1&id=eab41766-c9b6-4632-8a73-42232a431051"
```
  
Success response:

```json
{
    "cmd": "/v1/executions",
    "execution-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
    "status": "complete", 
    "verdict": "pass", 
    "logs": "10:50:10.7241 task-started
    10:50:10.7243 script-started helloworld
    10:50:10.7309 script-stopped PASS 0.007
    10:50:10.7375 task-stopped 0.006909608840942383", 
    "logs-index": 156
}
```
           
## More security

### Adding reverse proxy

Adding a reverse proxy in the front of server enables to expose only one tcp port (8080) 
and to have a TLS link between the client and the server. 
Also, the default behaviour of the QT client and toolbox is to try to connect 
on the tcp/8080 port with ssl (can be modifed).

If you want to install a reverse proxy, please to follow this procedure.

1. Install the example provided `scripts\reverseproxy\extensiveautomation_api.conf` in your apache instance. If you install the reverse proxy on a new server, don't forget to replace the 127.0.0.1 address by the ip of your extensive server.

    ```bash
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
    ```

    With this configuration in apache, the REST API is now running on the port tcp/8080 (tls).

2. Checking if the REST api working fine with curl command.

    ```bash
    curl -X POST https://127.0.0.1:8080/rest/session/login --insecure \ 
    -H "Content-Type: application/json" \
    -d '{"login": "admin", "password": "password"}'
    ```
         
### LDAP users authentication

By default, users are authenticated locally from database (by checking hash password).
This behavior can be modified by using a remote authentication server. In this mode, you always need to add users in the local database.

Follow this procedure to enable LDAP authentication:

1. Install python dependancies with the `pip` command:

    ```bash
    python3 -m pip install ldap3
    ```

2. Configure the `settings.ini`  file to enable ldap authentication and other stuff

    ```bash
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
    ```

3. Restart the server

    ```bash
    cd src/
    python3 extensiveautomation.py --stop
    python3 extensiveautomation.py --start
    ```
    
4. Check the new user authentication method

    ```bash
    curl -X POST http://127.0.0.1:8081/session/login \
    -H "Content-Type: application/json" \
    -d '{"login": "admin", "password": "password"}'
    ```
    
## Migration from old version

Since version 22 of the server, a major change has been introduced on the test files.
All the old tests in XML can still be used but they are obsolete. We must favor the new YAML format.

### Tests convertion to YAML format

XML to YAML conversion can be done with the following command.
A new YML file will be created automatically after converting the XML reading.

```bash
extensiveautomation --convert-to-yaml
```

## About

This project is an effort, driven in my spare time.

|  | |
| ------------- | ------------- |
| Copyright |  Copyright (c) 2010-2020  Denis Machard <d.machard@gmail.com> |
| License |  LGPL2.1 |
| Homepage |  https://www.extensiveautomation.org/ |
| Docs |  https://extensiveautomation.readthedocs.io/en/latest/ |
| Github |  https://github.com/ExtensiveAutomation |   
| Docker Hub | https://hub.docker.com/u/extensiveautomation |   
| PyPI |  https://pypi.org/project/extensiveautomation-server/ |
| Google Users | https://groups.google.com/group/extensive-automation-users |
| Twitter | https://twitter.com/Extensive_Auto |