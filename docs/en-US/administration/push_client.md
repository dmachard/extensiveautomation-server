---
name: Push a new client
---

# Push a new client

Use this feature can be useful to dispatch to all testers a new version of the client.

* [Deploy a new client version for Windows](push_client#deploy-a-new-client-version-for-windows)
* [Deploy a new client version for Linux](push_client#deploy-a-new-client-version-for-linux)

## Deploy a new client version for Windows

1.	Go to the folder `<INSTALL_PATH>/current/Packages/Client`

2.	Upload the new Windows version in the folder `/win32/` or `/win64/` 

    ```
    [ win32]# ls
    ExtensiveTesting_Client_X.X.X_Setup.exe
    ```

3.	No restart needed, just re-deploy the new client as below:

    ```
    # xtctl deploy
    Deploying clients.(ExtensiveTestingClient_X.X.X_Setup.exe)
    Deploying tools.(ExtensiveTestingToolbox_X.X.X_Setup.exe)
    Deploying portable clients... (No client)
    Deploying portable tools... (No client)
    ```
    
## Deploy a new client version for Linux

1.	Go to the folder `<INSTALL_PATH>/current/Packages/Client`

2.	Upload the new version in the folder `/linux2/` 

    ```
    [ linux2]# ls
    ExtensiveTesting_Client_X.X.X_Setup.tar.gz
    ```

3.	No restart needed, just re-deploy the new client as below:

    ```
    # xtctl deploy
    Deploying clients.(ExtensiveTestingClient_X.X.X_Setup.exe)
    Deploying tools.(ExtensiveTestingToolbox_X.X.X_Setup.exe)
    Deploying portable clients... (No client)
    Deploying portable tools... (No client)
    ```