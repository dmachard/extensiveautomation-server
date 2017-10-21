---
name: Logs
---

# Logs

* [Manage logs server](logs#server)
* [Manage client logs](logs#client)
* [Manage toolbox logs](logs#toolbox)
* [Logs to provide](logs#package-logs)

## Server

All logs are located and centralized in the following folder `/opt/xtc/current/Var/Logs/`

|Filename|Description|
|:-------------:|:-----:|
|access_rp.log|apache log of the reverse proxy.log|
|access_ssl_rp.log|apache log of the reverse proxy for the ssl access.log|
|access_web.log|apache log of the web interface .log|
|error_rp.log|apache error log of the reverse proxy|
|error_ssl_rp.log|apache error log of the reverse proxy for the ssl part|
|error_web.log|apache error log for the web interface|
|output.log|server automation logs|
|tests.out|test logs for development only|

Server logs are in `INFO` level by default.

Debug mode activation:

1. Go to the folder `/opt/xtc/current/` and edit the file `setting.ini`

2. Locate the section `[Trace]` and change the key `level`

    ```
    level=DEBUG
    ```

3. Save the file and reload the configuration to take the change in account.

    ```
    xtctl reload
    ```

## Client

Logs are located in the following folder `<Program Files>/Extensive Testing Client/Logs/`
Client logs are in `INFO` level by default.

Debug mode activation:

1. Open the client **Extensive Testing Client** and go the menu `File > Preferences > Application`

2. Locate the group Logging Application. Click on the combobox `Level` and choose the value `DEBUG`.
    ![](/docs/images/preferences_application_logs.png)
    
3. Click on the button `OK` to save the change.
    ![](/docs/images/client_logs.png)
    
## Toolbox

Logs are located in the following folder `<Program Files>/Extensive Testing Toolbox/Logs/`
Toolbox logs are in `INFO` level by default.

Debug mode activation:

1. Go the folder `<Program Files>/Extensive Testing Toolbox/` and edit the file `setting.ini`


2. Locate the section `[Trace]` and change the key `level`

    ```
    level=DEBUG
    ```

3. Save the file and restart the Toolbox
    ![](/docs/images/toolbox_logs.png)
    

## Package logs

When you have a issue with the solution please to provide the following logs (minimals logs to retrieve):
 - Server part
    * <UNTAR_DIR>/install.log
    * <INSTALL_DIR>/Var/Logs/output.log
 - Client
    * <INSTALL_DIR>/Logs/output.log
    * <INSTALL_DIR>/Logs/output_stderr.log
 - Toolbox
    * <INSTALL_DIR>/Logs/output.log
    * <INSTALL_DIR>/Logs/output_stderr.log