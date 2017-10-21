---
name: Installation Guide
---

# Installation Guide

## Installation

1.	Upload the tar.gz package on your target and uncompressed-it. Before to untar, please to check if you have enough disk space.
Go inside the new folder `./ExtensiveTesting.X.X.X`

    ```
    # tar xf ExtensiveTesting-X.X.X.tar.gz
    # cd ExtensiveTesting-X.X.X
    ```
    
2.	Go inside the folder and execute the script `./install.sh`: 

        ./install.sh
        Are you sure to install the product? (yes or no) yes
        ======================================================
        =  - Installation of the ExtensiveTesting product -  =
        =                    Denis Machard                   =
        =               www.extensivetesting.org             =
        ======================================================
        * Detecting the operating system (centos 7)                [  OK  ]
        * Detecting the system architecture (x86_64)               [  OK  ]
        * Detecting Perl, Python                                   [  OK  ]
        * Detecting primary network address (XXX.XXX.XXX.XXX)      [  OK  ]
        * Adding external libraries .................              [  OK  ]
        * Adding external libraries .......                        [  OK  ]
        * Adding interop libraries .......                         [  OK  ]
        * Detecting Apache                                         [  OK  ]
        * Detecting MySQL/MariaDB                                  [  OK  ]
        * Detecting Postfix                                        [  OK  ]
        * Detecting Openssl                                        [  OK  ]
        * Detecting Php                                            [  OK  ]
        * Copying source files                                     [  OK  ]
        * Adding startup service                                   [  OK  ]
        * Updating configuration files                             [  OK  ]
        * Creating extensivetesting user                           [  OK  ]
        * Updating folders rights                                  [  OK  ]
        * Updating php configuration                               [  OK  ]
        * Updating httpd configuration                             [  OK  ]
        * Adding virtual host                                      [  OK  ]
        * Restarting httpd                                         [  OK  ]
        * Restarting MySQL/MariaDB                                 [  OK  ]
        * Restarting postfix                                       [  OK  ]
        * Adding the ExtensiveTesting database                     [  OK  ]
        * Starting ExtensiveTesting X.X.X                          [  OK  ]
        =========================================================================
        - Installation terminated!
        - Continue and go to the web interface (https://XXX.XXX.XXX.XXX/web/index.php)
        =========================================================================

3.	Check the status of server, perform until to have the "running" message.

    ```
    # xtctl status
    Extensive Testing is starting...
    
    ...
    
    # xtctl status
    Extensive Testing is running
    ```

4. This step is optionnal, follow this page if you want to add the **[additionals](additionals)** packages.

## Custom Installation

This part is only for *advanced user*! If you use the recommanded system (centOS), the custom installation is not needed.

1. Prepare the table before to start the custom install


    |Key|Value|
    |:-----:|:-----:|
    |EXTERNAL_IP||
    |EXTERNAL_FQDN||
    |MYSQL_IP||
    |MYSQL_LOGIN||
    |MYSQL_PASSWORD||
    
2. Upload the tar.gz package on your target and uncompressed-it. Go inside the new folder `ExtensiveTesting.X.X.X`

    ```
    # tar xf ExtensiveTesting-X.X.X.tar.gz
    # cd ExtensiveTesting-X.X.X
    ```

3.	Execute the script `./custom.sh` and respond to each questions

        ./custom.sh
        ======================================================
        =  - Installation of the ExtensiveTesting product -  =
        =                    Denis Machard                   =
        =               www.extensivetesting.org             =
        ======================================================
        * Detecting the operating system (XXXXXXXX)                [  OK  ]
        * Detecting the system architecture (XXXXXX)               [  OK  ]
        * Detecting Perl, Python                                   [  OK  ]
        * Detecting primary network address (XX.XX.XX.XX)          [  OK  ]
        * Download automatically all missing packages? [Yes] 
        * In which directory do you want to install the ExtensiveTesting product? [/opt/xtc/]
        * What is the directory that contains the init scripts? [/etc/init.d/]
        * What is the external ip of your server? [XX.XX.XX.XX] <EXTERNAL_IP>
        * What is the FQDN associated to the external ip of your server? [XX.XX.XX.XX] <EXTERNAL_FQDN>
        * What is the database name? [xtcXXX]
        * What is the table prefix? [xtc]
        * What is the ip of your mysql/mariadb server? [127.0.0.1] <MYSQL_IP>
        * What is the login to connect to your mysql/mariadb server? [root] <MYSQL_LOGIN>
        * What is the password of previous user to connect to your mysql/mariadb server? [] <MYSQL_PASSWORD>
        * What is the sock file of your mysql/mariadb server? [/var/lib/mysql/mysql.sock]
        * Do you want to configure iptables automatically? [Yes]?
        * Do you want to configure php automatically? [Yes]?
        * Where is your php conf file? [/etc/php.ini]
        * Do you want to configure apache automatically? [Yes]?
        * What is the directory that contains the httpd conf file? [/etc/httpd/conf/]
        * What is the directory that contains the httpd virtual host conf files? [/etc/httpd/conf.d/]
        * What is the directory that contains the virtual host? [/var/www/]
        * Do you want to configure selinux automatically? [No]?
        * What is the path of the openssl binary? [/usr/bin/openssl]

4.	Wait during the process of installation

        * Adding external libraries ......................         [  OK  ]
        * Adding external libraries ..........                     [  OK  ]
        * Adding interop libraries .......                         [  OK  ]
        * Detecting Apache                                         [  OK  ]
        * Detecting MySQL/MariaDB                                  [  OK  ]
        * Detecting Postfix                                        [  OK  ]
        * Detecting Openssl                                        [  OK  ]
        * Detecting Php                                            [  OK  ]
        * Copying source files                                     [  OK  ]
        * Adding startup service                                   [  OK  ]
        * Updating configuration files                             [  OK  ]
        * Creating extensivetesting user                           [  OK  ]
        * Updating folders rights                                  [  OK  ]
        * Updating iptables                                        [  OK  ]
        * Updating php configuration                               [  OK  ]
        * Updating httpd configuration                             [  OK  ]
        * Adding wstunnel module                                   [  OK  ]
        * Adding virtual host                                      [  OK  ]
        * Restarting httpd                                         [  OK  ]
        * Restarting firewall                                      [  OK  ]
        * Restarting Mysql/MariaDB                                 [  OK  ]
        * Restarting postfix                                       [  OK  ]
        * Adding the ExtensiveTesting database                     [  OK  ]
        * Starting ExtensiveTesting X.X.X server                   [  OK  ]
        ==================================================================
        - Installation terminated!
        - Continue and go to the web interface (https://XXX.XXX.XXX.XXX/web/index.php)
        ==================================================================

5.	Check the status of server, perform until to have the "running" message.

    ```
    # xtctl status
    Extensive Testing is starting...
    
    ...
    
    # xtctl status
    Extensive Testing is running
    ```

6.	You can access to the web interface of the server with `https://<EXTERNAL_FQDN>/`
Several default accounts exists after the installation without password:

    - Admin
    - Tester
    - Developer
    - Leader
    - Automaton

**Notes:**

- Don’t forget to change all default passwords!
