ExtensiveAutomation
===================

Introduction
------------

<a href="https://www.extensiveautomation.org/" target="_blank"><img width="100" src="https://www.extensiveautomation.org/img/logo_extensive_testing.png" alt="ExtensiveAutomation logo"></a>

ExtensiveAutomation est un framework générique pour automatiser les tâches de tests, d'exploitation et de déploiment.


Installation depuis les sources
------------------------------

1. Cloner le projet avec git sur votre serveur linux

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
  
2. Installer les dépendances python suivantes. Attention, les libraries `pip` et `libxslt` doivent être disponibles sur votre système avant l'exécution de la commande suivante:

        pip install wrapt scandir lxml pycnic    

3. Démarrer le serveur

        cd extensiveautomation
        python extensiveautomation --start

   Une API REST est disponible sur le port tcp/8081.
   
   3 comptes utilisateurs sont disponibles par défaut:
    - admin
    - tester
    - monitor
    
   Le mot de passe par défaut est `password`.
   
   Enfin si vous avez un parefeu d'activé, il faut autoriser les ports suivants:
    - tcp/8081
    - tcp/8082
    - tcp/8083
    
4. Vérifier le status du serveur

        cd extensiveautomation
        python extensiveautomation --status
        Extensive Automation is running
        
5. Vérifier si l'api REST est disponible avec la commande curl.

        curl -X POST http://127.0.0.1:8081/session/login -H "Content-Type: application/json" -d '{"login": "admin", "password": "password"}'
        
Installation depuis dockerhub
-----------------------------

1. Téléchargement de l'image depuis docker hub

        docker pull extensiveautomation/extensiveautomation-server:20.0.0

2. Démarrer le container sans persistance des données de tests

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name=extensive extensiveautomation

           
   Si vous avez un parefeu d'activé, il faut autoriser les ports suivants:
   
    - tcp/8081
    - tcp/8082
    - tcp/8083
    
3. Vous pouvez maintenant utiliser le client lourd ou l'API REST directement pour piloter le serveur
   - Le port tcp/8081 permet d'utiliser l'api REST du serveur
   - Le port tcp/8082 est utilisé par le client lourd pour avoir un lien bidirectionnel de type  websocket entre le serveur et le client.
   - Le port tcp/8083 est utilisé par les agents pour communiquer avec le serveur en mode bidirectionnel.

Installation depuis dockerhub avec persistence des données
----------------------------------------------------------

La persistence des données va permettre de garder la même structure de tests peut importe le serveur.

1. Pour cela, il faut créer la structure suivante dans un répertoire spécifique: 

        ├── extensiveautomation-data
        │   ├── Dockerfile
        │   └── var/
        │        ├── data.db
        │        ├── documentations.dat
        │        ├── __init__.py
        │        └── tests/
        │          └── 1/ (default tests)
        │        └── templates/

2. Créer le répertoire principal

        mkdir extensiveautomation-data
        cd extensiveautomation-data

3. Récupérer les sources du serveur pour récupérer le répertoire `Var`.
Ce répertoire contient les données qui peuvent être modifiées par les utilisateurs.

        git clone https://github.com/ExtensiveAutomation/extensiveautomation-server.git
        cp -rf extensiveautomation-server/Var .
        rm -rf extensiveautomation-server
    
4. Ajouter le fichier Dockerfile pour le `data volume` basée sur une image `Alpine`.


        FROM alpine:3.10
        
        WORKDIR /home/extensive
        
        COPY . /home/extensive/Var/
        
        RUN adduser -D extensive && \
            cd /home/extensive && \
            chown -R extensive:extensive /home/extensive
        
        VOLUME /home/extensive/Var
        
        USER extensive
        CMD ["echo", "Data volume for ExtensiveAutomation"]

5. Maintenant il est pssible de construire l'image, créer le container et le démarrer.

        docker build -t extensiveautomation-data .
        docker run --name=extensive-data extensiveautomation-data

6.  Enfin démarrer le serveur en précisant le volume de données à utiliser:

        docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083  --volumes-from=extensive-data --name=extensive-server extensiveautomation/extensiveautomation-server:20.0.0

Installation d'un reverse proxy
-------------------------------

L'installation d'un reverse proxy devant le serveur est obligatoire pour l'utilisation du client lourd et des agents. 

1. Un exemple de configuration apache est disponible dans les sources  `Build\reverseproxy\extensiveautomation_api.conf`. Si votre reverse proxy est installé sur une serveur différent du serveur extensive, alors il faut remplacer l'adresse de loopback par l'adresse de votre serveur de test.

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

        curl -X POST https://127.0.0.1:8080/session/login --insecure -H "Content-Type: application/json" -d '{"login": "admin", "password": "password"}'

Documentations
--------------

Une documentation détaillée sur les fonctionnalités est disponible sur http://extensiveautomation.readthedocs.io/fr/latest/
 
     
Auteur
-------

Logiciel crée par *Denis MACHARD*
 