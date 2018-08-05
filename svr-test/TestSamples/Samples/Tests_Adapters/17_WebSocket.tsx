<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>03/09/2014 22:18:58</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><type>bool</type><value>False</value><name>DEBUG</name><description /><scope>local</scope></parameter><parameter><value>False</value><description /><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><color /><type>float</type><value>1.0</value><name>TIMEOUT</name><description /><scope>local</scope></parameter><parameter><value>443</value><description /><name>WSS_PORT</name><type>int</type><scope>local</scope></parameter><parameter><value>echo.websocket.org</value><description /><name>WS_ADDR</name><type>str</type><scope>local</scope></parameter><parameter><value>www.websocket.org</value><description /><name>WS_ORIGIN</name><type>str</type><scope>local</scope></parameter><parameter><value>80</value><description /><name>WS_PORT</name><type>int</type><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>probe-network01</name><type>network</type></probe></probes><outputs-parameters><parameter><color /><type>float</type><value>1.0</value><name>TIMEOUT</name><description /><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class WS_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.ADP_WS = SutAdapters.WebSocket.Client(parent=self, bindIp='', bindPort=0, name=None, destinationIp=input('WS_ADDR'), 
														destinationPort=input('WS_PORT'), destinationHost='', debug=input('DEBUG'),
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))


	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		self.ADP_WS.disconnect()

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.ADP_WS.connect()
		if self.ADP_WS.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('unable to connect')
			
		self.ADP_WS.handshake(resource="/?encoding=text", origin=input('WS_ORIGIN'))
		if self.ADP_WS.isHandshakeSuccessful(timeout=input('TIMEOUT')) is None:
			self.abort('handshake failed')
			
		self.ADP_WS.sendText(text='test')
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
		
		self.ADP_WS.sendPing(data="1")
		if self.ADP_WS.hasReceivedPong(timeout=input('TIMEOUT')) is None:
			self.abort('no pong received')
		
		self.ADP_WS.sendBinary(data='\x00\x11')
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
		
		self.ADP_WS.sendClose()
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')		
					
class WSS_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.ADP_WS = SutAdapters.WebSocket.Client(parent=self, bindIp='', bindPort=0, name=None, destinationIp=input('WS_ADDR'), 
														destinationPort=input('WSS_PORT'), sslSupport=True, 
														destinationHost='', debug=input('DEBUG'),
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))


	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		self.ADP_WS.disconnect()

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.ADP_WS.connect()
		if self.ADP_WS.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('unable to connect')
			
		self.ADP_WS.handshake(resource="/?encoding=text", origin=input('WS_ORIGIN'))
		if self.ADP_WS.isHandshakeSuccessful(timeout=input('TIMEOUT')) is None:
			self.abort('handshake failed')
			
		self.ADP_WS.sendText(text='test')
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
		
		self.ADP_WS.sendPing(data="1")
		if self.ADP_WS.hasReceivedPong(timeout=input('TIMEOUT')) is None:
			self.abort('no pong received')
		
		self.ADP_WS.sendBinary(data='\x00\x11')
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
		
		self.ADP_WS.sendClose()
		if self.ADP_WS.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')		]]></testdefinition>
<testexecution><![CDATA[
WS_01(suffix=None).execute()
WSS_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1409775538.01</testdevelopment>
</file>