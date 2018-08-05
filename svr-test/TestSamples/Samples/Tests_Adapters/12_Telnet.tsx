<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>probe-network01</name><type>network</type></probe></probes><agents><agent><description /><type /><name>AGENT_SOCKET</name><value>agent-socket01</value></agent></agents><descriptions><description><value>denis</value><key>author</key></description><description><value>26/07/2013</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>PROXY_IP</name><value>141.255.166.42 </value><scope>local</scope></parameter><parameter><description /><type>int</type><name>PROXY_PORT</name><value>1080</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>TELNET_PORT</name><value>24</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>5.0</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>URL_TELNET</name><value>vert.synchro.net</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_TELNET_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.T = SutAdapters.Telnet.Client(parent=self, bindIp='', bindPort=0, destIp=input('URL_TELNET'), 
									destPort=input('TELNET_PORT'),debug=input('DEBUG'), saveContent=True,
									agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))
		self.T.connect()
		tcpConnected = self.T.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
	def cleanup(self, aborted):
		self.T.disconnect()
		tcpDisconnected = self.T.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )
	def definition(self):	
		self.step1.start()
		
		# prompt
		rsp = self.T.hasReceivedData( timeout=input('TIMEOUT'), dataExpected=TestOperators.Contains(needle='Synchronet BBS') )
		if rsp is None:
			self.abort( 'Prompt login not found' )
		self.info( 'prompt detected', bold=True )
	
		Time(self).wait(timeout=5)
		
		self.step1.setPassed(actual="success")

class TESTCASE_TELNET_PROXY_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		self.T = SutAdapters.Telnet.Client(parent=self, bindIp='', bindPort=0, destHost=input('URL_TELNET'), 
									destPort=input('TELNET_PORT'),debug=input('DEBUG'),
									proxyType=SutAdapters.TCP.PROXY_SOCKS4, proxyUserID='xtc', proxyIp=input('PROXY_IP'),
									proxyPort=input('PROXY_PORT'), proxyHost='', proxyEnabled=True,
								agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		self.T.connect()
		tcpConnected = self.T.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
		proxyOk = self.T.isAcceptedProxy(timeout=input('TIMEOUT') )
		if proxyOk is None:
			self.abort( 'proxy failed' )
			
	def cleanup(self, aborted):
		self.T.disconnect()
		tcpDisconnected = self.T.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )
	def definition(self):	
		self.step1.start()
		
		# prompt
		rsp = self.T.hasReceivedData( timeout=input('TIMEOUT'), dataExpected=TestOperators.Contains(needle='Synchronet BBS') )
		if rsp is None:
			self.abort( 'Prompt login not found' )
		self.info( 'prompt detected', bold=True )
	
		self.step1.setPassed(actual="success")
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_TELNET_01(suffix=None).execute()
#TESTCASE_TELNET_PROXY_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105880.92</testdevelopment>
</file>