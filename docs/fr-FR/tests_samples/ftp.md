---
name: FTP example
---

# FTP example

* [Introduction](ftp#introduction)
* [Adapter configuration](ftp#adapter-configuration)
* [Make connection and disconnection](ftp#make-connection-and-disconnection)
* [List the content of a specific folder](ftp#list-the-content-of-a-specific-folder)
* [Detect a file in a specific folder with regular expression](ftp#detect-a-file-in-a-specific-folder-with-regular-expression)

## Introduction

This sample show how to use the FTP client adapter. This adapter enables to connect to server through the FTP protocol with support of:

- Secure channel with TLS
- Download/upload files or folders
- Add/rename/delete files or folders
- List the content of a folder
- Detect file or folder with regular expression support

The following explanations are based on the sample available on `/Samples/Tests_Adapters/21_Ftp.tsx`

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_FTP = SutAdapters.FTP.Client(
                                            parent=self,
                                            debug=input('DEBUG'),
                                            destinationIp=input('FTP_HOST'),
                                            user=input('FTP_USER'), 
                                            password=input('FTP_PWD') ,
                                            agentSupport=input('SUPPORT_AGENT')
                                            )
    ```

    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |DEBUG|boolean|False|
    |FTP_USER|string|admin|
    |FTP_PWD|string|admin|
    |FTP_HOST|string|192.168.1.1|
    |SUPPORT_AGENT|boolean|False|

## Make connection and disconnection

1. In the definition part, copy/paste the following lines to make connection with authentification.

    ```python
    self.ADP_FTP.connect(passiveMode=True)
    if self.ADP_FTP.isConnected(timeout=input('TIMEOUT')) is None:
        self.abort("unable to connect")

    self.ADP_FTP.login()
    if self.ADP_FTP.isLogged(timeout=input('TIMEOUT')) is None:
        self.abort("unable to login")

    self.info("SFTP connection OK" )
    ```
    
2. Copy/paste the following line to make a disconnection from your machine

    ```python
    self.ADP_FTP.disconnect()
    if self.ADP_FTP.isDisconnected(timeout=input('TIMEOUT')) is not None:
        self.abort("disconnect failed")
    
    self.info("FTP disconnection OK" )
    ```
    
## List the content of a specific folder

1. In the definition part, copy/paste the following lines

    ```python
    self.ADP_FTP.listingFolder()
    if self.ADP_FTP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
        self.error("unable to get listing folder")
    ```
    
    
## Detect a file in a specific folder with regular expression

1. In the definition part, copy/paste the following lines

    ```python
    self.ADP_FTP.waitForFile(
                            path='/var/log/', 
                            filename='^messages-.*$', 
                            timeout=input('TIMEOUT')
                        )
    
    found = self.ADP_FTP.hasDetectedFile(
                                        path=None, 
                                        filename=None, 
                                        timeout=input('TIMEOUT')
                                    )
    if found is None: self.error("file not found")
    ```