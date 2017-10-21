---
name: TELNET example
---

# TELNET example

* [Introduction](telnet#introduction)
* [Adapter configuration](telnet#adapter-configuration)
* [Make connection and disconnection](telnet#make-connection-and-disconnection)
* [Use operators to detect specific data](telnet#use-operators-to-detect-specific-data)

## Introduction

This sample show how to use the TELNET client adapter. This adapter enables to connect to server through the TELNET protocol.

The following explanations are based on the sample available on `/Samples/Tests_Adapters/12_Telnet.tsx`

## Adapter configuration


1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_TELNET = SutAdapters.Telnet.Client(
                                                parent=self, 
                                                destIp=input('TELNET_IP'), 
                                                destPort=input('TELNET_PORT'),
                                                debug=input('DEBUG'),
                                                agentSupport=input('SUPPORT_AGENT')
                                                )
    ```
    
    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |DEBUG|boolean|False|
    |TELNET_IP|string|192.168.1.1|
    |TELNET_PORT|integer|22|
    |SUPPORT_AGENT|boolean|False|
    
## Make connection and disconnection
  
1. In the definition part, copy/paste the following lines to make connection

    ```python
    self.ADP_TELNET.connect()
    connected = self.ADP_TELNET.isConnected( timeout=input('TIMEOUT') )
    if not connected: self.abort( 'unable to connect' )
    ```
    
2. Copy/paste the following line to make a disconnection from your machine

    ```python
    self.ADP_TELNET.disconnect()
    disconnected = self.ADP_TELNET.isDisconnected( timeout=input('TIMEOUT') )
    if not disconnected: self.abort( 'unable to disconnect' )
    ```

## Use operators to detect specific data

1. Copy/paste the following line to wait specific data

    ```python
    rsp = self.ADP_TELNET.hasReceivedData( 
                                            timeout=input('TIMEOUT'), 
                                            dataExpected=TestOperators.Contains(needle='Password:') )
                                        )
    if rsp is None: self.abort( 'Password prompt not found' )
    ```
    
**Notes:**

- Telnet responses can be splitted in severals events, so you new to retrieve properly all events to create the complete response. 
- Please to use the make your own adapter with a codec if this behaviour is problematic for you.