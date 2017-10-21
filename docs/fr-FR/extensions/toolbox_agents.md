---
name: Toolbox Agents
---

# Agents purpose

Agents enables to interact with a SUT when the system under test (SUT) can be reach by the test server directly.

# Supported agents 

|Name Type|Windows Support|Linux Support|Description|
|---:|:-----:|:-------:|:-------|
|dummy|✅|✅|For example only|
|socket|✅ *(1)*|✅|Communicate on network over TCP/UDP and SSL|
|ftp|✅|✅|Communicate with ftp server|
|sikulix-server|✅||Interaction with sikuli project|
|selenium3-server*(2)*|✅|✅|Interaction with web browsers|
|selenium2-server|✅|✅|Interaction with web browsers|
|soapui||✅|Interaction with soapui project|
|command|✅|✅|Execute system commands|
|file|✅|✅|Read file on system|
|adb|✅||Interaction with the android debug bridge|
|gateway-sms|✅||Send or received texto|
|database|✅|✅|Query database server|
|ssh|✅|✅|Communicate with ssh or sftp server|

**Notes:** 

- (1): raw socket not supported on windows
- (2): with the release of Selenium 3+, the minimum required version of Java is 8


