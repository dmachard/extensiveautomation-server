---
name: SFTP example
---

# SFTP example

* [Introduction](sftp#introduction)
* [Adapter configuration](sftp#adapter-configuration)
* [Make connection and disconnection](sftp#make-connection-and-disconnection)
* [List the content of a specific folder](sftp#list-the-content-of-a-specific-folder)
* [Detect a file in a specific folder with regular expression](sftp#detect-a-file-in-a-specific-folder-with-regular-expression)

## Introduction

This sample show how to use the SFTP client adapter. This adapter enables to manipulate files system in a remote system throught the SFTP procotol (Secure File Transfer Protocol).
Features supported:

- Download/upload files or folders
- Add/rename/delete files or folders
- List the content of a folder
- Detect file or folder with regular expression support

The following explanations are based on the sample available on `/Samples/Tests_Adapters/22_Sftp.tsx`

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_SFTP = SutAdapters.SFTP.Client(
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

1. In the definition part, copy/paste the following lines to make connection with authentification.

    ```python
    connected = self.ADP_SFTP.doConnect(timeout=input('TIMEOUT'))
    if not connected: self.abort("sftp connect failed")
    
    self.info("SFTP connection OK" )
    ```
    
2. Copy/paste the following line to make a disconnection from your machine

    ```python
    disconnected = self.ADP_SFTP.doDisconnect(timeout=input('TIMEOUT'))
    if not disconnected: self.abort("disconnect failed")
    
    self.info("SFTP disconnection OK" )
    ```
    
## List the content of a specific folder

1. In the definition part, copy/paste the following lines

    ```python
    self.ADP_SFTP.listingFolder(
                            path="/var/log/", 
                            extended=False
                            )
    
    rsp = self.ADP_SFTP.hasFolderListing(timeout=input('TIMEOUT'))
    if rsp is None: self.error("unable to get listing folder")
    
    self.warning( rsp.get("SFTP", "result") )
    ```
    
## Detect a file in a specific folder with regular expression

1. In the definition part, copy/paste the following lines

    ```python
    self.ADP_SFTP.waitForFile(
                            path='/var/log/', 
                            filename='^messages-.*$', 
                            timeout=input('TIMEOUT')
                        )
    
    found = self.ADP_SFTP.hasDetectedFile(
                                        path=None, 
                                        filename=None, 
                                        timeout=input('TIMEOUT')
                                    )
    if found is None: self.error("file not found")
    ```