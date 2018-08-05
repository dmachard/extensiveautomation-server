<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>13/06/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>127.0.0.1</value><description /><name>DST_IP</name><type>str</type><scope>local</scope></parameter><parameter><value>10.0.0.1</value><description /><name>DST_IP_1</name><type>str</type><scope>local</scope></parameter><parameter><value>2049</value><description /><name>DST_PORT</name><type>int</type><scope>local</scope></parameter><parameter><value>eth0</value><description /><name>INTERFACE</name><type>self-eth</type><scope>local</scope></parameter><parameter><value>10.0.0.240 (eth0)</value><description /><name>SRC_IP</name><type>self-ip</type><scope>local</scope></parameter><parameter><value>50000</value><description /><name>SRC_PORT</name><type>int</type><scope>local</scope></parameter><parameter><value>False</value><description /><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><value>3.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
# client
class TESTCASE_UDP_CLIENT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual="error")
	def definition(self):
		self.step1.start()
		
		udp = None
		udp = SutAdapters.UDP.Client(parent=self, bindIp=input('SRC_IP'), bindPort=input('SRC_PORT'),
																destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'),
																separatorDisabled = True,
																debug=input('DEBUG'), 
																agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') 	)
		
		udp.startListening()
		udpListening = udp.isListening( timeout=input('TIMEOUT') )
		if not udpListening:
			self.abort( 'UDP not listening' )
		self.info(udpListening.get() ) 
		
		data = "data test"
		udp.sendData( data=data)

#		dataReceived = udp.hasReceivedData( timeout=input('TIMEOUT') )
#		if dataReceived is None:
#			self.abort( 'not data received' )
#		self.info( dataReceived )
#		
		udp.stopListening()		
		udpStopped = udp.isStopped( timeout=input('TIMEOUT') )
		if not udpStopped:
			self.abort( 'UDP not stopped' )
		self.info(udpStopped.get() ) 	

		self.step1.setPassed(actual="success")		

class TESTCASE_UDP_CLIENT_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual="error")
	def definition(self):
		self.step1.start()
		
		udp = None
		udp = SutAdapters.UDP.Client(parent=self, bindIp=input('SRC_IP'), bindPort=input('SRC_PORT'),
																destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'),
																separatorDisabled = False, separatorIn='a', separatorOut='\n',
																debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') 	)
		
		udp.startListening()
		udpListening = udp.isListening( timeout=input('TIMEOUT') )
		if not udpListening:
			self.abort( 'UDP not listening' )
		
		self.wait( 10 )
		
		udp.stopListening()		
		udpStopped = udp.isStopped( timeout=input('TIMEOUT') )
		if not udpStopped:
			self.abort( 'UDP not stopped' )			
				
		self.step1.setPassed(actual="success")

# sniffer
class TESTCASE_UDP_SNIFFER_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.udp = SutAdapters.UDP.Sniffer(parent=self, debug=input('DEBUG'), 
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
														
		self.step1.start()
		self.udp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		udpSniffing = self.udp.isSniffing( timeout=input('TIMEOUT') )
		if not udpSniffing:
			self.abort()
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.udp.stopListening()
	def definition(self):

		self.udp.sendData(destIp=input('DST_IP_1'), destPort=11, data='\xff'*90, srcPort=0 )
		
		rsp = self.udp.hasReceivedData(timeout=input('TIMEOUT'))
		
		self.step1.setPassed(actual="success")

class TESTCASE_UDP_SNIFFER_SEPARATOR_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.udp = SutAdapters.UDP.Sniffer(parent=self, debug=input('DEBUG'), separatorDisabled=False, separatorIn='ver',
																agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
																
		self.step1.start()

		self.udp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		udpSniffing = self.udp.isSniffing( timeout=input('TIMEOUT') )
		if not udpSniffing:
			self.abort()
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.udp.stopListening()
	def definition(self):

		self.udp.sendData(destIp=input('DST_IP_1'), destPort=11, data='\xff'*90, srcPort=0 )
		
		rsp = self.udp.hasReceivedData(timeout=input('TIMEOUT'))
		
		self.step1.setPassed(actual="success")

# server

class TESTCASE_UDP_CLIENT_SERVER_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):

		# adapters 
		self.ADP_CLT = SutAdapters.UDP.Client(parent=self, bindIp='', bindPort=0, destinationIp='', 
										destinationPort=600, destinationHost='', socketFamily=4, inactivityTimeout=0.0, 
										separatorIn='\x00', separatorOut='\x00', separatorDisabled=True, debug=False,
										logEventSent=True, logEventReceived=True, parentName=None, 
										agentSupport=False, agent=None)
		self.ADP_SRV = SutAdapters.UDP.Server(parent=self, bindIp='', bindPort=600, socketFamily=4,
										separatorIn='\x00', separatorOut='\x00', separatorDisabled=True, debug=False, 
										logEventSent=True, logEventReceived=True, parentName=None)

	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_SRV.startListening()
		if not self.ADP_SRV.isListening(timeout=1.0):
			self.abort( 'fail to start server' )
		
		self.ADP_CLT.startListening()
		if not self.ADP_CLT.isListening(timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'fails to start client' )
		
		self.ADP_CLT.sendData(data='hello world', to=None)
		if not self.ADP_SRV.hasClientData(timeout=1.0, clientId=None, data=None, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'no data received from client' )
			
		self.ADP_CLT.stopListening()
		if not self.ADP_CLT.isStopped(timeout=1.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'fails to stop client' )
		
		self.ADP_SRV.stopListening()
		if not self.ADP_SRV.isStopped(timeout=1.0):
			self.abort( 'fail to stop properly server' )
			
		self.step1.setPassed(actual="success")
		]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_UDP_CLIENT_01(suffix=None).execute()
TESTCASE_UDP_CLIENT_02(suffix=None).execute()

TESTCASE_UDP_SNIFFER_01(suffix=None).execute()
TESTCASE_UDP_SNIFFER_SEPARATOR_01(suffix=None).execute()

if not input('SUPPORT_AGENT'):
	TESTCASE_UDP_CLIENT_SERVER_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105845.81</testdevelopment>
</file>