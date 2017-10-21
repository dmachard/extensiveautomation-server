---
name: Sut Adapters
---

## Sut Adapters

* [Introduction](adapters#introduction)
* [Select adapters to use in your test](adapters#select-adapters-to-use-in-your-test)
* [Make set of adapters as default](adapters#make-set-of-adapters-as-default)
* [List of available adapters](adapters#list-of-available-adapters)
* [Verbose mode](adapters#verbose-mode)
* [Debug mode](adapters#debug-mode)

## Introduction

Adapters must be used in a test to interact with the **SUT (System Under Test)**. Adapters are regrouped in one package (tar.gz). 
You can have several packages of adapters in your test server.

Usage mode:

- Direct mode: the test server can interact with the SUT (no network constraints)
- Agent mode: the SUT is only accessible where the agent is deployed

## Select adapters to use in your test

You can select the set of adapters to use in your test. This feature can be useful to have a branch for developement and a stable adapters.

1. From the client, create a new test and go to the test properties part 

2. Click on the `Test Design` tabulation and locate the `Adapters` option

3. Double click on it and select the version to use

## Make set of adapters as default

When you have several set of adapters, you can define one as default for testers. Follow the procedure below. 
 
1. From the client, go to the part `Module Listing > Adapters`

2. Select your set of adapters to put as default

3. Right click on it and click on the option `Set as default`

4. Repackage the adapters to save your change

## List of available adapters

List of available adapters:

|Family|Name|Direct Mode|Agent Mode|Description|
|:---|---:|:---------:|:---------:|:---------|
|**Misc**|||||
||Dummy|✅|✅ (dummy)|Adapter just for example|
|**Raw Network Testing**|||||
||ARP|✅|✅ (socket)|Arping module and sniffer to receive and send network packet|
||ICMP|✅|✅ (socket)|Ping module and sniffer to receive and send network packet|
||Ethernet|✅|✅ (socket)|Sniffer to receive and send frame|
||IP|✅|✅ (socket)|Sniffer for IPv4|
|**Network Testing**|||||
||Pinger|✅||Pinger for host throught ICMP, TCP or URL|
||UDP|✅|✅ (socket)|Client, server and sniffer|
||TCP|✅|✅ (socket)|Client, server and sniffer|
||NTP|✅|✅ (socket)|Client to query a server |
||DNS|✅||Client to resolv host|
||SNMP|✅|✅ (socket)|Trap receiver|
||HTTP|✅|✅ (socket)|Client and server with tls, proxy support|
||SOAP|✅|✅ (socket)|Client with tls, proxy support|
||SoapUI||✅ (soapui)|Client to run soapui campaign|
||REST|✅|✅ (socket)|Client with tls, proxy support|
||WebSocket|✅|✅ (socket)|Client|
|**User Interface Testing**|||||
||Adb||✅ (adb)|Android automator throught ADB (Android debug bridge)|
||Selenium||✅ (selenium)|Selenium for web testing|
||Sikuli||✅ (sikuli)|Sikuli for app testing|
|**Databases Testing**|||||
||Microsoft SQL|✅|✅ (database)|Query microsoft database|
||MySQL|✅|✅ (database)|Query MySQL database|
||PostgreSQL|✅|✅ (database)|Query PostgreSQL database|
|**System Testing**|||||
||SSH|✅|✅ (ssh)|Client, console and terminal|
||TELNET|✅|✅ (socket)|Client|
||SFTP|✅|✅ (ssh)|Client|
||FTP|✅|✅ (ftp)|Client with tls support|
||System File||✅ (file)|Interact with file in system|
||System Linux||✅ (command)|Interact with Linux system|
||System Windows||✅ (command)|Interact with Windows system throught wmic|
||Cisco Catalyst|✅||Interact with catalyst switch cisco throught telnet|
|**Telecom Testing**|||||
||SMS Gateway||✅ (gateway-sms)|Receive or send SMS through a gateway on device mobile|
||SIP|✅|✅ (socket)|Client and phone|
||RTP|✅|✅ (socket)|Send or receive real-time data, such as audio, video or more.|

## Verbose mode

The verbose mode is activated by default on all adapters.
This option can used to reduced the number of events generated during the execution of a test.

## Debug mode

The debug mode is not enabled by default. 
This mode can be used to make troubleshooting in the conception phase.
