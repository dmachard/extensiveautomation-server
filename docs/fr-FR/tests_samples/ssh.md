---
name: SSH example
---

# SSH example

* [Introduction](ssh#introduction)
* [Adapter configuration](ssh#adapter-configuration)
* [Make connection and disconnection](ssh#make-connection-and-disconnection)
* [Execute basic commands](ssh#execute-basic-commands)

## Introduction

This sample show how to use the SSH client adapter. 
This adapter enables to connect to server through the SSH v2 protocol with support of:

- authentication by login/password
- authentication key

The following explanations are based on the sample available on `/Samples/Tests_Adapters/05_SSH.tsx`

**Please use [ssh snippets](http://documentations.extensivetesting.org/docs/generic_use/send_ssh) for more efficiency**

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_SSH = SutAdapters.SSH.Client(
                                            parent=self, 
                                            login=input('LOGIN'), 
                                            password=input('PWD'),
                                            destIp=input('DEST_IP'), 
                                            destPort=input('DEST_PORT'), 
                                            debug=input('DEBUG'),
                                            agentSupport=input('SUPPORT_AGENT')
                                        )
    ```
    
    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |DEBUG|boolean|False|
    |LOGIN|string|admin|
    |PWD|string|admin|
    |DEST_IP|string|192.168.1.1|
    |DEST_PORT|integer|22|
    |SUPPORT_AGENT|boolean|False|

## Make connection and disconnection

1. In the definition part, copy/paste the following lines to make connection with authentification. You need to provide the prompt of your remote machine, the default prompt expected is `~]#`

    ```python
    connected = self.ADP_SSH.doConnect(
                                        timeout=input('TIMEOUT'), 
                                        prompt='~]#'
                                      )
    if not connected: self.abort("ssh connect failed")
    
    self.info("SSH connection OK" )
    ```
    
2. Copy/paste the following line to make a disconnection from your machine

    ```python
    disconnected = self.ADP.doDisconnect(timeout=input('TIMEOUT'))
    if not disconnected: self.abort("disconnect failed")
    
    self.info("SSH disconnection OK" )
    ```
    
## Execute basic commands 

1. Copy/paste the following lines to execute a command in your system. The example below shows how to execute the command date on the remote machine and retrieve the value.

    ```python
    rsp = self.ADP_SSH. doSendCommand(
                                        command='date', 
                                        timeout=input('TIMEOUT'), 
                                        expectedData=None, 
                                        prompt='~]#'
                                    )
    if rsp is None: self.abort("run command failed")
    
    self.warning( rsp )
    ```

    
**Notes:**

- Ssh responses can be splitted in severals events, so you new to retrieve properly all events to create the complete response. 
- Please to use the `Console` adapter if this behaviour is problematic for you or prefer to use the `Terminal` adapter