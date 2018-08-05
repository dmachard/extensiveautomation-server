<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>13/09/2014 13:38:15</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>DEST</name><value>www.yahoo.fr</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>PROXY_IP_SOCKS4</name><value>141.255.166.42 </value><scope>local</scope></parameter><parameter><description /><type>str</type><name>PROXY_IP_SOCKS5</name><value>62.255.82.98</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>PROXY_PORT</name><value>1080</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>5</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>probe-network01</name><type>network</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_SOCKS4_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.ADP_TCP = SutAdapters.TCP.Client(parent=self, bindIp='', bindPort=0, name=None, destinationIp=input('DEST'),
																	destinationPort=80, destinationHost='', proxyType=SutAdapters.TCP.PROXY_SOCKS4,
																	proxyUserID='extensive testing', proxyIp=input('PROXY_IP_SOCKS4'),
																	proxyPort=input('PROXY_PORT'), proxyHost='', proxyEnabled=True, socketTimeout=1, socketFamily=4, 
																	inactivityTimeout=30.0, tcpKeepAlive=False, tcpKeepAliveInterval=30.0, 
																	separatorIn='\x00', separatorOut='\x00', separatorDisabled=True,
																	sslSupport=False, sslVersion='TLSv1', checkCert='No', debug=input('DEBUG'), 
																	logEventSent=True, logEventReceived=True, parentName=None, agentSupport=input('SUPPORT_AGENT'),
																	agent=agent('AGENT'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.ADP_TCP.connect()
		if self.ADP_TCP.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('failed to connect')
		if self.ADP_TCP.isAcceptedProxy(timeout=input('TIMEOUT')) is None:
			self.abort('failed to connect on proxy')
			
		self.ADP_TCP.sendData(data="""GET / HTTP/1.1\r\nAccept: text/html, application/xhtml+xml, */*\r\nAccept-Language: fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko\r\nAccept-Encoding: gzip, deflate\r\nHost: 50.87.193.219\r\nConnection: Keep-Alive\r\n\r\n""")
		if self.ADP_TCP.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
			
		self.ADP_TCP.disconnect()
		if self.ADP_TCP.isDisconnected(timeout=1.0) is None:
			self.abort('failed to disconnect')	


class TESTCASE_SOCKS5_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.ADP_TCP = SutAdapters.TCP.Client(parent=self, bindIp='', bindPort=0, name=None, destinationIp='',
																	destinationPort=80, destinationHost=input('DEST'), proxyType=SutAdapters.TCP.PROXY_SOCKS5,
																	proxyUserID='extensive testing', proxyIp=input('PROXY_IP_SOCKS5'),
																	proxyPort=input('PROXY_PORT'), proxyHost='', proxyEnabled=True, socketTimeout=1, socketFamily=4, 
																	inactivityTimeout=30.0, tcpKeepAlive=False, tcpKeepAliveInterval=30.0, 
																	separatorIn='\x00', separatorOut='\x00', separatorDisabled=True,
																	sslSupport=False, sslVersion='TLSv1', checkCert='No', debug=input('DEBUG'), 
																	logEventSent=True, logEventReceived=True, parentName=None, agentSupport=input('SUPPORT_AGENT'),
																	agent=agent('AGENT'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.ADP_TCP.connect()
		if self.ADP_TCP.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('failed to connect')
		if self.ADP_TCP.isAcceptedProxy(timeout=input('TIMEOUT')) is None:
			self.abort('failed to connect on proxy')
			
		self.ADP_TCP.sendData(data="""GET / HTTP/1.1\r\nAccept: text/html, application/xhtml+xml, */*\r\nAccept-Language: fr-FR,fr;q=0.8,en-US;q=0.5,en;q=0.3\r\nUser-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko\r\nAccept-Encoding: gzip, deflate\r\nHost: 50.87.193.219\r\nConnection: Keep-Alive\r\n\r\n""")
		if self.ADP_TCP.hasReceivedData(timeout=input('TIMEOUT')) is None:
			self.abort('no data received')
			
		self.ADP_TCP.disconnect()
		if self.ADP_TCP.isDisconnected(timeout=1.0) is None:
			self.abort('failed to disconnect')	


]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_SOCKS4_01(suffix=None).execute()
TESTCASE_SOCKS5_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1410608295.04</testdevelopment>
</file>