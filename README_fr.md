# ExtensiveAutomation

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/extensiveautomation-server)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Python%20Package/badge.svg)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Docker%20Image/badge.svg)

| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2020  Denis Machard <d.machard@gmail.com> |
| Licence |  LGPL2.1 |
| Site web |  https://www.extensiveautomation.org/ |
| Documentations |  https://extensiveautomation.readthedocs.io/fr/latest/ |
| Github |  https://github.com/ExtensiveAutomation |   
| Docker Hub | https://hub.docker.com/u/extensiveautomation |   
| PyPI |  https://pypi.org/project/extensiveautomation-server/ |
| Google Users | https://groups.google.com/group/extensive-automation-users |
| Twitter | https://twitter.com/Extensive_Auto |
| | |

## Table of contents
* [Introduction](#introduction)
* [Installation du serveur](#installation)
	* [PyPI](#pypi)
	* [Image Docker](#docker-image)
	* [Code source](#source-code)
	* [Ajout plugins](#ajout-des-plugins)
* [Connexion au serveur](#connexion-au-serveur ) 
	* [Utilisation de la commande curl](#utilisation-de-la-commande-curl)
	* [Connexion au serveur avec le client web](#connexion-au-serveur-avec-le-client-web)
	* [Connexion au serveur avec le client web](#connexion-au-serveur-avec-le-client-web)
* [Exécuter un test depuis l'API REST](#executer-un-test-depuis-l-api-rest) 
	* [Obtenir le secret pour l'API](#obtenir-le-secret-pour-l-api)
	* [Exécuter un test de base](#executer-un-test-de-base)
	* [Récupérer les logs du test](#recuperer-les-logs-du-test)
* [Sécurisation](#sécurisation)
	* [Ajout ReverseProxy](#reverse-proxy)
	* [Authentication utilisateurs via LDAP](#authentication-utilisateurs-via-ldap)

## Introduction

**ExtensiveAutomation** est un framework générique en 100% python pour automatiser les tâches de tests, d'exploitation et de déploiment.

## Installation du serveur

### PyPI

1. Exécuter la commande pip pour installer le serveur

        python3 -m pip install extensiveautomation_server

2. Après l'installation il est possible de démarrer le serveur avec la commande suivante

        extensiveautomation --start

3. Enfin vérifier le [bon fonctionnement du serveur](#utilisation-de-la-commande-curl).

### Docker image

1. Téléchargement de l'image depuis docker hub

        docker pull extensiveautomation/extensiveautomation-server:latest

2. Démarrer le container sans persistance des données de tests

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name=extensive extensiveautomation

3. Enfin vérifier le [bon fonctionnement du serveur](#utilisation-de-la-commande-curl).

### Source code
 
1. Cloner le projet avec git sur votre serveur linux

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
  
2. Installer les dépendances python suivantes avec la commande `pip`:
   
        python3 -m pip install wrapt pycnic lxml jsonpath_ng pyyaml
        
3. Démarrer le serveur. Sur Linux, le serveur est exécuté en tant que daemon.

        cd src
        python3 extensiveautomation.py --start
        
4. Enfin vérifier le [bon fonctionnement du serveur](#utilisation-de-la-commande-curl).
 
### Ajout des plugins

Les plugins permettent au serveur d'intéragir avec le système à controller.
Par défaut le serveur est fournit sans aucun plugin, il est donc nécessaire de les installer
un par un en fonction de vos besoins.

* [Plugin CLI (ssh)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)

        pip install extensiveautomation_plugin_cli
        
* [Plugin WEB (http/https)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web)

        pip install extensiveautomation_plugin_web

* [Plugin GUI (selenium, sikulix and adb)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)
* [Et d'autres encore...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Connexion au serveur

###  Connexion au serveur avec la commande curl

1. Merci de prendre en compte aussi les points suivants:
	
	 - Le serveur ecoute sur les pots TCP suivants (ne pas oublier d'autoriser ces ports sur votre firewall):
	    - tcp/8081: REST API
	    - tcp/8081: Tunnel Websocket pour le client lourd
	    - tcp/8082: Tunnel Websocket pour les agents
	 - Les comptes utilisateurs `admin`, `tester` et `monitor` sont disponibles avec le mot de passe par défaut `password`. 
	 - Le projet `Common` est crée par défaut, et est accessible par les utilisateurs précédement listés.
	 - Le swagger de l'api REST est disponible dans le répertoire `scripts/swagger`.
    
2. Vérifier si l'api REST est disponible avec la commande curl ou postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'

   success response:
   
```json
{"cmd": "/session/login", 
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
"name": ""}
```
        
### Connexion au serveur avec le client web

Pour utiliser le serveur depuis l'interface web, merci de lire la [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-webclient#web-interface-for-extensiveautomation) suivante.

L'interface web permet de:
- d'administrer les utilisateurs
- d'administrer les projets
- d'administrer les variables de tests

### Connexion au serveur avec le client lourd
  
Pour utiliser le serveur depuis le client lourd, merci de lire la [documentation](https://github.com/ExtensiveAutomation/extensiveautomation-appclient#qt-application-for-extensiveautomation) suivante.


## Exécuter un test depuis l'API REST

### Obtenir le secret pour l'API

Get the API secret for the user admin

        python3 extensiveautomation.py --apisecret admin
        API key: admin
        API secret: 6977aa6a443bd3a6033ebb52557cf90d24c79857

### Exécuter un test de base

Tests samples are available in the default tests storage <projectpath_install>/var/tests/1/

Curl command:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"project-id": 1,"test-extension": "yml", "test-name": "01_testunit",
              "test-path": "YAML_samples/Framework_Tests/"}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/tests/schedule
              
Success response:

        {"cmd": "/tests/schedule", "message": "background", 
         "task-id": 2, "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
         "tab-id": 0, "test-name": "01_testunit"}
        
### Récupérer les logs du test

Curl command:

        curl  --user admin:6977aa6a443bd3a6033ebb52557cf90d24c79857 \
              -d '{"test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", "project-id": 1}' \
              -H "Content-Type: application/json" \
              -X POST http://127.0.0.1:8081/results/details
        
Success response:

        {"cmd": "/results/details", "test-id": "e57aaa43-325d-468d-8cac-f1dea822ef3a", 
         "test-status": "complete", 
         "test-verdict": "pass", 
         "test-logs": "10:50:10.7241 task-started
         10:50:10.7243 script-started 01_testunit
         10:50:10.7309 script-stopped PASS 0.007
         10:50:10.7375 task-stopped 0.006909608840942383", 
         "test-logs-index": 156}
         
## Sécurisation

### Ajout d'un reverse proxy

Ajouter un reverse proxy devant le serveur permet d'exposer seulement un port tcp (8080) et 
d'activer le chiffrement du flux entre l'utilisateur et le serveur.

Aussi, par défaut le client lourd et les agents sont configurés pour se connecter sur le port 8080 
(port qui peut être modifié).

Merci de suivre la procédure ci-dessous pour installer le RP.

1. Un exemple de configuration apache est disponible dans les sources  `scripts\reverseproxy\extensiveautomation_api.conf`. Si votre reverse proxy est installé sur une serveur différent du serveur extensive, alors il faut remplacer l'adresse de loopback par l'adresse de votre serveur de test.

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


    L'API REST est maintenant disponible sur le port tcp/8080 en mode tls.

2. Test de l'API avec le reverse proxy

       curl -X POST https://127.0.0.1:8080/rest/session/login --insecure \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'

### Activation authentication LDAP

Par défaut, les utilisateurs sont authentifiés localement au serveur (en vérifiant un hash du mot de passe).
Ce comportement peut être modifié en utilisant un serveur d'authentification distant. 

Ne pas oublier que changer la méthode d'authentication nécessitera toujours de provisionner les utilisateurs 
dans la base locale.

Vous pouvez suivre la procédure suivante pour utiliser un serveur LDAP:

1. Installer la dépendance python suivante avec la commande `pip`:

        python -m pip install ldap3

2. Configurer le fichier de configuration `settings.ini` pour activer l'authentication ldap

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

3. Redémarrer le serveur.

        cd src/
        python extensiveautomation.py --stop
        python extensiveautomation.py --start

4. Vérifier l'authentification d'un utilisateur

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'