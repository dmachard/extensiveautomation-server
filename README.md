ExtensiveAutomation
===================

Introduction
------------

<a href="https://www.extensiveautomation.org/" target="_blank"><img width="100" src="https://www.extensiveautomation.org/img/logo_extensive_testing.png" alt="ExtensiveAutomation logo"></a>

ExtensiveAutomation is a generic automation framework for integration, regression and end-to-end usages. The framework provided a rich and collaborative workspace environment.

Installing from source
----------------------

1. Clone this repository on your linux server

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
 
2. As precondition, install the libraries `pip` and `libxslt` on your system then install the additional python libraries: 
    
        pip install wrapt scandir pycnic lxml
        
3. Finally start the server

        cd extensiveautomation
        python extensiveautomation --start

   REST API is running on port tcp/8081. 
   
   By the way, don't forget to authorize the following tcp ports if you have a firewall running on your server:
    - tcp/8081
    - tcp/8082
    - tcp/8083
    
   The following users are available by default:
    - admin
    - tester
    - monitor
    
   The default password is `password`.
   
4. Checking if the server is running fine.

        cd extensiveautomation
        python extensiveautomation --status
        Extensive Automation is running
        
5. Checking if the REST api working fine with curl command.

        curl -X POST http://127.0.0.1:8081/session/login -H "Content-Type: application/json" -d '{"login": "admin", "password": "password"}'
    
    The swagger of the api is available in the folder `Build/swagger`:
     - common_restapi.yaml
     - admin_restapi.yaml
     - tester_restapi.yaml

Installing from dockerhub
-----------------------------

1. Downloading the image

        docker pull extensiveautomation/extensiveautomation-server:20.0.0

2. Start the container without persistance for tests data

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name=extensive extensiveautomation
   
   By the way, don't forget to authorize the following tcp ports 
   if you have a firewall running on your server:
    - tcp/8081
    - tcp/8082
    - tcp/8083
    
3. Now you can use the qt client or REST api to interact with the server   
   - tcp/8081 enable to use the REST api of the server
   - tcp/8082 is used by the qt client to have a bidirectionnal link
   - tcp/8083 is used by agents to have a bidirectionnal link
   
Installation from dockerhub with persistant data
------------------------------------------------

1. For this, we will use the following minimal directory structure and files in the specific container:

    ├── extensiveautomation-data
    │   ├── Dockerfile
    │   └── var/
    │        ├── data.db
    │        ├── documentations.dat
    │        ├── __init__.py
    │        └── tests/
    │          └── 1/ (default tests)
    │        └── templates/

2. Create the main folder 

    mkdir extensiveautomation-data
    cd extensiveautomation-data

3. Copy the content of the `Var` directory in server side.

    git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
    cp -rf extensiveautomation-server/Var .
    rm -rf extensiveautomation-server
    
4. And add the Dockerfile for the data volume, basing on an `Alpine` image:

    FROM alpine:3.10

    WORKDIR /home/extensive

    COPY . /home/extensive/Var/

    RUN adduser -D extensive && \
        cd /home/extensive && \
        chown -R extensive:extensive /home/extensive

    VOLUME /home/extensive/Var
 
    USER extensive
    CMD ["echo", "Data volume for ExtensiveAutomation"]

5. Now, we have to build the image and create the container, just as any other container:

    docker build -t extensiveautomation-data .
    docker run --name=extensive-data extensiveautomation-data

6. Finally start the server and indicating that it has to use the data volume:

    docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083  --volumes-from=extensive-data --name=extensive-server extensiveautomation/extensiveautomation-server:20.0.0
  
Installing reverse proxy
----------------------

If you want to use the qt application client or qt agents toolbox. You need to install a reverse proxy in front of the extensive server.

1. Install the example provided `Build\reverseproxy\extensiveautomation_api.conf` in your apache instance. If you install the reverse proxy on a new server, don't forget to replace the 127.0.0.1 address by the ip of your extensive server.

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

        curl -X POST https://127.0.0.1:8080/session/login --insecure -H "Content-Type: application/json" -d '{"login": "admin", "password": "password"}'

Documentations
--------------

If you want a complete documentation on usages, go to the specific documentations

 - For english users - http://extensiveautomation.readthedocs.io/en/latest/

 - Pour les utilisateurs français - http://extensiveautomation.readthedocs.io/fr/latest/
 
     
Author
-------

It was created by *Denis MACHARD*
 