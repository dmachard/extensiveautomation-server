---
name: SNMP example
---

# SNMP example

* [Introduction](snmp#introduction)
* [Adapter configuration](snmp#adapter-configuration)
* [Checking snmp trap](snmp#check-snmp-trap)

## Introduction

This sample show how to use the SNMP client adapter. 
This adapter enables to receive SNMP trap v1 or v2:

The following explanations are based on the sample available on `/Samples/Tests_Adapters/18_SNMP.tsx`

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_SNMP = SutAdapters.SNMP.TrapReceiver(
                                                    parent=self, 
                                                    bindIp=get('SRC_IP'), 
                                                    bindPort=get('SRC_PORT'), 
                                                    debug=get('DEBUG'),
                                                    agent=agent('AGENT_SOCKET'), 
                                                    agentSupport=input('SUPPORT_AGENT')
                                                )
    ```
    
    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |DEBUG|boolean|False|
    |SRC_IP|string|0.0.0.0|
    |SRC_PORT|integer|162|
    |SUPPORT_AGENT|boolean|False|

## Checking snmp trap

1. In the definition part, copy/paste the following lines to start to listen

    ```python
    self.ADP_SNMP.startListening()
    listening = self.ADP_SNMP.udp().isListening( timeout=get('TIMEOUT') )
    if not listening: self.abort( 'UDP not listening' )
    ```
    
2. Copy/paste the following line to check the reception of one specific trap

    ```python
    trap = self.UDP_ADP.hasReceivedTrap(
                                            timeout=input('TIMEOUT'), 
                                            version=SutAdapters.SNMP.TRAP_V1, 
                                            community=None, 
                                            agentAddr=None, 
                                            enterprise=None,
                                            genericTrap=None, 
                                            specificTrap="17", 
                                            uptime=None, 
                                            requestId=None, 
                                            errorStatus=None, 
                                            errorIndex=None
                                        )
    if trap is None:  self.abort("trap expected not received")
    ```