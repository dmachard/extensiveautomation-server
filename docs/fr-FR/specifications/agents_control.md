---
name: Agents control
---

# Agents control

## Remote control of an agent

Agent can exchange data between a test and the agent throught the test server.
Some functions are available to do that.

* From Agent -> To Test:

|Messages|Agent|Adapter|
|:-----:|:-----:|:-----:|
|Send a `error` message|def sendError(self, request, data):|def receivedErrorFromAgent(self, data):|
|Send a `notify` message|def sendNotify(self, request, data):|def receivedNotifyFromAgent(self, data):|
|Send a `data` message|def sendData(self, request, data):|def receivedDataFromAgent(self, data):|

* From Test -> To Agent:

|Messages|Agent|Adapter|
|:-----:|:-----:|:-----:|
|Receive a `init` message|def onAgentInit(self, client, tid, request):|def initAgent(self, data):|
|Receive a `notify` message|def onAgentNotify(self, client, tid, request):|def sendNotifyToAgent(self, data):|
|Receive a `reset` message|def onAgentReset(self, client, tid, request):|def resetAgent(self):|

