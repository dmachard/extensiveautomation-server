<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network1</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><name>DEBUG</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>DST_IP</name><value>192.168.1.1</value><type>str</type><scope>local</scope></parameter><parameter><color /><description /><name>INTERFACE</name><value>eth0</value><type>self-eth</type><scope>local</scope></parameter><parameter><color /><description /><name>SRC_IP</name><value>10.0.0.240 (eth0)</value><type>self-ip</type><scope>local</scope></parameter><parameter><color /><description /><name>SUPPORT_AGENT</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>TIMEOUT</name><value>1</value><type>float</type><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_ICMPV4_RAW_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'),
																	agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
																	
		self.step1.start()
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.sendPacket( destIp=input('DST_IP'), type=7, code=0, checksum=None, 
													identifier=None, sequenceNumber=None, data=None, destMac=None)
		self.wait(2)
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_ICMPV4_PING_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'),
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
				
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.echoQuery(destIp=input('DST_IP'))
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_PING_BROADCAST_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'),
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		mac = TestValidators.MacAddress(separator=':')
		self.icmp.echoQuery( destIp='255.255.255.255', destMac=mac.getBroadcast() )
		
		self.wait( 10 )
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_ICMPV4_TIMESTAMP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'),
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.timestampQuery(destIp=input('DST_IP'))
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_ICMPV4_INFORMATION_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'),
																agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		self.ipGen = TestValidators.IPv4Address(separator='.')
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=self.ipGen.getNull() )
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		mac = TestValidators.MacAddress(separator=':')
		self.icmp.informationQuery( destIp=self.ipGen.getNull(), destMac=mac.getBroadcast() )
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_MASK_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.ipGen = TestValidators.IPv4Address(separator='.')
		
		self.icmp.maskQuery(destIp=self.ipGen.getBroadcast())
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_REDIRECT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.redirectError(destIp=input('DST_IP'))
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_SOURCE_QUENCH_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
																agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.sourceQuenchError(destIp=input('DST_IP'), unused="0x00FF0000")
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_PARAMETER_PROBLEM_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.parameterProblemError(destIp=input('DST_IP'), pointer="0xFF")
		
		self.step1.setPassed(actual="success")

class TESTCASE_ICMPV4_TIME_EXCEEDED_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
																	agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		self.step1.start()

		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):
		
		self.icmp.timeExceededError(destIp=input('DST_IP'))
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_ICMPV4_DESTINATION_UNREACHABLE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.icmp = SutAdapters.ICMP.SnifferV4(parent=self, debug=input('DEBUG'), 
								agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		self.step1.start()
		
		self.icmp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		ipSniffing = self.icmp.isSniffing( timeout=input('TIMEOUT') )
		if not ipSniffing:
			self.abort()
			
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.icmp.stopListening()
	def definition(self):

		self.icmp.destinationUnreachableError(destIp=input('DST_IP'))
		self.icmp.destinationUnreachableError(destIp=input('DST_IP'))
		
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_ICMPV4_RAW_01(suffix=None).execute()
TESTCASE_ICMPV4_PING_01(suffix=None).execute()
TESTCASE_ICMPV4_PING_BROADCAST_01(suffix=None).execute()
TESTCASE_ICMPV4_TIMESTAMP_01(suffix=None).execute()
TESTCASE_ICMPV4_INFORMATION_01(suffix=None).execute()
TESTCASE_ICMPV4_MASK_01(suffix=None).execute()
TESTCASE_ICMPV4_REDIRECT_01(suffix=None).execute()
TESTCASE_ICMPV4_SOURCE_QUENCH_01(suffix=None).execute()
TESTCASE_ICMPV4_PARAMETER_PROBLEM_01(suffix=None).execute()
TESTCASE_ICMPV4_TIME_EXCEEDED_01(suffix=None).execute()
TESTCASE_ICMPV4_DESTINATION_UNREACHABLE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105879.33</testdevelopment>
</file>