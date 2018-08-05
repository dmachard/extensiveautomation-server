<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>eth0</value><description /><name>INTERFACE</name><type>self-eth</type><color /><scope>local</scope></parameter><parameter><value>10.0.0.1</value><description /><name>IP</name><type>str</type><color /><scope>local</scope></parameter><parameter><value>10.0.0.2</value><description /><name>IP_1</name><type>str</type><color /><scope>local</scope></parameter><parameter><value>10.0.0.240 (eth0)</value><description /><name>PARAM</name><type>self-ip</type><color /><scope>local</scope></parameter><parameter><value>False</value><description /><name>SUPPORT_AGENT</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>20.0</value><description /><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_ARP_RAW_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'),
																								agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()
		
		self.arp.sendPacket( hardwareType=SutAdapters.ARP.HARDWARE_TYPE, protocolType=SutAdapters.Ethernet.IPv4, 
											op=SutAdapters.ARP.OP_REQUEST, hardwareLen=SutAdapters.ARP.HARDWARE_LEN,
											protocolLen=SutAdapters.ARP.PROTOCOL_LEN,
											senderIp='0.0.0.1', senderMac='00:00:00:00:00:00',
											targetIp='0.0.0.0', targetMac='00:00:00:00:00:00' )
		self.wait(10)
		self.step1.setPassed(actual="success")

class TESTCASE_ARP_RAW_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'),
																										agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()

		pkt = self.arp.hasReceivedPacket( timeout=input('TIMEOUT'), op=SutAdapters.ARP.OP_REQUEST )
		if pkt is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")

class TESTCASE_ARP_WHO_HAS_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'), senderIp=input('PARAM'),
																									agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()

		pkt = self.arp.whoHas( targetIp=input('IP'), timeout=input('TIMEOUT') )
		if pkt is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")

class TESTCASE_ARP_WHO_HAS_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'), senderIp=input('PARAM'),
																								agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()

		pkt = self.arp.whoHas( targetIp=input('IP_1'), timeout=input('TIMEOUT') )
		self.wait( 5 )
		
		self.step1.setPassed(actual="success")
			
class TESTCASE_ARP_GRATUITOUS_ARP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'), senderIp=input('PARAM'), 
																				agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()

		pkt = self.arp.gratuitousArp( )
		
		self.step1.setPassed(actual="success")

class TESTCASE_ARP_GET_CACHE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'), senderIp=input('PARAM'),
																			agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'))
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()
		self.wait( 5 )
		
		cache = self.arp.getCache()
		self.info( "cache in live: %s" % str(cache) )
		
		self.step1.setPassed(actual="success")
		

class TESTCASE_ARP_BROADCAST_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.arp = SutAdapters.ARP.Sniffer(parent=self, debug=input('DEBUG'), 
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.arp.startListening(eth=input('INTERFACE'), srcMac='FF:FF:FF:FF:FF:FF' )
		arpSniffing = self.arp.isSniffing( timeout=input('TIMEOUT') )
		if not arpSniffing:
			self.abort()
	def cleanup(self, aborted):
		self.arp.stopListening()
	def definition(self):
		self.step1.start()
		
		self.arp.sendPacket( hardwareType=SutAdapters.ARP.HARDWARE_TYPE, protocolType=SutAdapters.Ethernet.IPv4, 
											op=SutAdapters.ARP.OP_REQUEST, hardwareLen=SutAdapters.ARP.HARDWARE_LEN,
											protocolLen=SutAdapters.ARP.PROTOCOL_LEN,
											senderIp='255.255.255.255', senderMac='FF:FF:FF:FF:FF:FF',
											targetIp='255.255.255.255', targetMac='FF:FF:FF:FF:FF:FF', ethernetDstMac='FF:FF:FF:FF:FF:FF' )
		self.wait(60)
		
		cache = self.arp.getCache()
		self.info( "cache in live: %s" % str(cache) )
		
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_ARP_RAW_01(suffix=None).execute()
TESTCASE_ARP_RAW_02(suffix=None).execute()

TESTCASE_ARP_WHO_HAS_01(suffix=None).execute()
TESTCASE_ARP_WHO_HAS_02(suffix=None).execute()
TESTCASE_ARP_GRATUITOUS_ARP_01(suffix=None).execute()

TESTCASE_ARP_GET_CACHE_01(suffix=None).execute()

TESTCASE_ARP_BROADCAST_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105877.73</testdevelopment>
</file>