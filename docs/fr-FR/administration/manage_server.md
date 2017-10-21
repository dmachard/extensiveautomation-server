---
name: Manage server
---

# Manage server

* [Start the server](manage_server#start-the-server)
* [Stop the server](manage_server#stop-the-server)
* [Status of the server](manage_server#status-of-the-server)
* [Show the current version of the server](manage_server#show-the-current-version-of-the-server)

## Start the server

Starting the server can be done only from SSH as root. 
The start can take some time because of the procedure of deployment (uncompressing agents and probes). 

1. From SSH as root, execute the following command to start the server

    ```
    # xtctl start
    Checking database                                          [  OK  ]
    Saving current adapters                                    [  OK  ]
    Saving current libraries                                   [  OK  ]
    Starting Extensive Testing                                 [  OK  ]
    ```

2. Checking in logs if the server is started successfully


    ```
    # tailf /opt/xtc/current/Var/Log/output.log
    2014-12-06 11:00:54,092 - INFO - All local probes are started
    2014-12-06 11:00:54,092 - INFO – Extensive Testing successfully started (in 14 sec.)
    ```

## Stop the server

Stopping the server can be done only from SSH as root.

1. From SSH as root, execute the following command to stop-it

    ```
    # xtctl stop
    Saving current adapters                                    [  OK  ]
    Saving current libraries                                   [  OK  ]
    Stopping Extensive Testing                                 [  OK  ]
    ```

2. Checking in logs if the server is stopped successfully

    ```
    # tailf /opt/xtc/current/Var/Log/output.log
    2014-12-06 10:58:51,810 - INFO - Stopping server
    2014-12-06 10:58:51,911 - INFO – Extensive Testing successfully stopped!
    ```

## Status of the server

### From command line

1. From SSH as root, execute the following command

    ```
    # xtctl status
    Extensive Testing is running
    ```
    
### From the web interface

1. From the web, connect in your online test center and navigate in the menu to `System > General status`

    ![](/docs/images/server_web_status.png)

    
## Show the current version of the server

1. From SSH as root, execute the following command to run one test

    ```
    # xtctl version
    Server version: X.X.X
    ```
