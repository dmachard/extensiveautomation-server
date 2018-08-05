<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>eth0</value><description /><name>INTERFACE</name><type>self-eth</type><color /><scope>local</scope></parameter><parameter><value>False</value><description /><name>SUPPORT_AGENT</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>1</value><description /><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.ether = SutAdapters.Ethernet.Sniffer(parent=self, debug=input('DEBUG'),
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.ether.startListening(eth=input('INTERFACE'), srcMac='01:01:01:01:02:02')
		ethSniffing = self.ether.isSniffing( timeout=input('TIMEOUT') )
		if not ethSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.ether.stopListening()
	def definition(self):
		self.step1.start()
		
		self.ether.sendFrame(data='\xFF'*40, dstMac='01:01:01:01:02:01', protocolType=SutAdapters.Ethernet.IPv6)
		self.wait(5)
		
		self.step1.setPassed(actual="success")

class TESTCASE_BAD_DEVICE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.ether = SutAdapters.Ethernet.Sniffer(parent=self, debug=input('DEBUG'), 
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		self.ether.stopListening()
	def definition(self):
		self.step1.start()
		
		self.ether.startListening(eth='test')
		ethSniffing = self.ether.isSniffing( timeout=input('TIMEOUT') )
		if ethSniffing:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()
TESTCASE_BAD_DEVICE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105876.86</testdevelopment>
</file>