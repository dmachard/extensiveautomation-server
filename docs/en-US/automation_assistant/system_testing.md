---
name: System testing
---

# System testing

* [Introduction](system_testing#introduction)
* [Execute system commands](system_testing#execute-system-commands)
* [Use the shell recorder plugin](system_testing#use-the-shell-recorder-plugin)

## Introduction

This part enables to execute system actions in a remote machine through the protocol ssh.
Follow the next chapter to execute the system command `ps` and try to detect a specific process in the ouput of the command.

|Action Name|Description|
|-----:|:-----|
|OPEN SSH SESSION|Open a ssh session|
|CLOSE SESSION|Close the ssh session|
|CLEAR SCREEN|Clear the screen|
|SEND TEXT|Send text|
|SEND SHORTCUT|Send shortcut|
|CHECKING IF SCREEN|Expect text in screen|

## Execute system commands

1. Connect the remote test server and from the welcome page of the client, click on the `New System Test` link 

2. Select the `OPEN SSH SESSION` and configure the destination IP, login and password of the remote server, click on the Add Action to register this step

    ![](/docs/images/aa_system_open.png)

3. Select the `SEND TEXT` action and configure-it with the following command `ps faxu`

4. Checks if the following agent is running (agent-linux-dummy01) on the output of the previous command

    ![](/docs/images/aa_system_check.png)

4. Choose the `CLOSE SESSION` and add-it in your test

5. Finally click on the button `Create test` to generate your test


## Use the shell recorder plugin

Install and use the plugin `SSH-Recorder` to import from a session and generate automatically the test for the automation assistant.
Go the [Shell Recorder](http://documentations.extensivetesting.org/docs/client_plugin_deployment/shell_recorder) page for the complete documentation