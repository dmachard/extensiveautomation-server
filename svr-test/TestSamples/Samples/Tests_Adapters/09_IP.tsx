<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><name>DEBUG</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>INTERFACE</name><value>eth0</value><type>self-eth</type><scope>local</scope></parameter><parameter><color /><description /><name>PARAM_1</name><value>10.0.0.240 (eth0)</value><type>self-ip</type><scope>local</scope></parameter><parameter><color /><description /><name>SUPPORT_AGENT</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>TIMEOUT</name><value>2</value><type>float</type><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_IPV4_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.ip = SutAdapters.IP.SnifferV4(parent=self, debug=input('DEBUG'), protocol2sniff=-1,
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.step1.start()

		self.ip.startListening(eth=input('INTERFACE'), srcIp=input('PARAM_1'))
		ipSniffing = self.ip.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort("unable to sniff")
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.ip.stopListening()
	def definition(self):

		self.ip.sendDatagram( dstIp='1.2.3.4', data='\x02'*30, identification=234 )	
		self.wait(1)
		
		self.ip.hasReceivedDatagram( timeout=input('TIMEOUT'), dstIp='test' )
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_BAD_DEVICE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.ip = SutAdapters.IP.SnifferV4(parent=self, debug=input('DEBUG'), 
												agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.ip.stopListening()
	def definition(self):

		self.ip.startListening(eth='test', srcIp="fdsqfds")
		ipSniffing = self.ip.isSniffing( timeout=input('TIMEOUT') )
		if ipSniffing:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_IPV4_01(suffix=None).execute()
TESTCASE_BAD_DEVICE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105878.54</testdevelopment>
</file>