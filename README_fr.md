# ExtensiveAutomation

![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Python%20Package/badge.svg)
![](https://github.com/ExtensiveAutomation/extensiveautomation-server/workflows/Docker%20Image/badge.svg)

| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2019  Denis Machard <d.machard@gmail.com> |
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
* [Installation](#installation)
	* [PyPI](#pypi)
	* [Image Docker](#docker-image)
	* [Code source](#source-code)
* [Test du serveur](#test-du-serveur)
* [Plugins](#ajouter-des-plugins)
* [Ajout ReverseProxy](#reverse-proxy)
* [Authentication utilisateurs via LDAP](#authentication-utilisateurs-via-ldap)

## Introduction

**ExtensiveAutomation** est un framework générique pour automatiser les tâches de tests, d'exploitation et de déploiment.
Le serveur peut s'exécuter avec Python 2 et Python 3, ainsi que sur Windows et Linux.

## Installation

### PyPI

1. Exécuter la commande pip pour installer le serveur

        python -m pip install extensiveautomation_server

2. Après l'installation il est possible de démarrer le serveur avec la commande suivante

        extensiveautomation --start

3. Enfin vérifier le [bon fonctionnement du serveur](#test-du-serveur).

### Docker image

1. Téléchargement de l'image depuis docker hub

        docker pull extensiveautomation/extensiveautomation-server:latest

2. Démarrer le container sans persistance des données de tests

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name=extensive extensiveautomation

3. Enfin vérifier le [bon fonctionnement du serveur](#test-du-serveur).

### Source code
 
1. Cloner le projet avec git sur votre serveur linux

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
  
2. Installer les dépendances python suivantes avec la commande `pip`:
   
    * Environnement Python3
    
            python -m pip install wrapt pycnic lxml jsonpath_ng
          
    * Environnement Python2, il est nécessaire d'installer la librarie `libxslt` et modifier le fichier settings.ini:
    
            python -m pip install wrapt scandir pycnic lxml jsonpath_ng
            
            vim src/ea/settings.ini
            [Bin]
            python=/usr/bin/python2.7
        
3. Démarrer le serveur. Sur Linux, le serveur est exécuté en tant que daemon.

        cd src
        python extensiveautomation.py --start
        
4. Enfin vérifier le [bon fonctionnement du serveur](#test-du-serveur).

## Test du serveur


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

## Ajouter des plugins

Les plugins permettent au serveur d'intéragir avec le système à controller.
Par défaut le serveur est fournit sans aucun plugin, il est donc nécessaire de les installer
un par un en fonction de vos besoins.

* [Plugin CLI (ssh)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-cli)
* [Plugin WEB (http/https)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-web)
* [Plugin GUI (selenium, sikulix and adb)](https://github.com/ExtensiveAutomation/extensiveautomation-plugin-gui)
* [Et d'autres encore...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)

## Ajout d'un reverse proxy

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

## Activation authentication LDAP

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