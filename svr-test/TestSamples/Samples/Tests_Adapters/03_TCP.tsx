<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>13/06/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><name>DEBUG</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>DST_HOST</name><value>www.verisign.com</value><type>str</type><scope>local</scope></parameter><parameter><color /><description /><name>DST_PORT</name><value>80</value><type>int</type><scope>local</scope></parameter><parameter><color /><description /><name>DST_PORT_SSL</name><value>443</value><type>int</type><scope>local</scope></parameter><parameter><color /><description /><name>INTERFACE</name><value>eth0</value><type>self-eth</type><scope>local</scope></parameter><parameter><color /><description /><name>SRC_IP</name><value>10.0.0.240 (eth0)</value><type>self-ip</type><scope>local</scope></parameter><parameter><color /><description /><name>SRC_PORT</name><value>34000</value><type>int</type><scope>local</scope></parameter><parameter><color /><description /><name>SUPPORT_AGENT</name><value>False</value><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><name>TIMEOUT</name><value>2.0</value><type>float</type><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
# client
class TESTCASE_TCP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		tcp = SutAdapters.TCP.Client(parent=self, destinationHost=input('DST_HOST'), destinationPort=input('DST_PORT'), debug=input('DEBUG'),
													 separatorDisabled=True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
		tcp.connect()
		tcpConnected = tcp.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
				raise Exception( 'TCP Not Connected' )
		self.info(tcpConnected.get() ) 
		
		data = """GET / HTTP/1.1\r\nHost: www.google.fr\r\nUser-Agent: ExtensiveTesting\r\nConnection: keep-alive\r\n\r\n"""
		tcp.sendData(data=data)
		
		dataReceived = tcp.hasReceivedData( timeout=input('TIMEOUT'), data=TestOperators.Contains('301') )
		if dataReceived is None:
			raise Exception( '200 OK not found' )
		self.info( dataReceived )
	
		tcp.disconnect()
		tcpDisconnected = tcp.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )
		self.info( tcpDisconnected )
		
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_TIMEOUT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		tcp = None
		tcp = SutAdapters.TCP.Client(parent=self, destinationHost='192.0.0.1', destinationPort=799, debug=input('DEBUG'),
												 separatorDisabled=True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
		tcp.connect()
		tcpTimeout = tcp.isConnectionTimeout( timeout=5 )
		if tcpTimeout is  None:
			self.error( 'TCP connected' )
		
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_FAILED_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		tcp = None
		tcp = SutAdapters.TCP.Client(parent=self, destinationHost='227.0.0.1', destinationPort=799, debug=input('DEBUG'),
										 separatorDisabled=True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
		tcp.connect()
		tcpFailed = tcp.isConnectionFailed( timeout=5 )
		if tcpFailed is None:
			self.error( 'TCP connected' )
			
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_REFUSED_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		tcp = None
		tcp = SutAdapters.TCP.Client(parent=self, destinationHost='127.0.0.1', destinationPort=455, debug=input('DEBUG'),
													 separatorDisabled=True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
		tcp.connect()
		tcpRefused = tcp.isConnectionRefused( timeout=5 )
		if tcpRefused is None:
			self.error( 'TCP connected' )
			
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_SSL_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual="error")
		
	def definition(self):
		self.step1.start()
		
		tcp = SutAdapters.TCP.Client(parent=self, destinationHost=input('DST_HOST'), destinationPort=input('DST_PORT_SSL'), debug=input('DEBUG'),
														 separatorDisabled=True, sslSupport=True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
		tcp.connect()
		tcpConnected = tcp.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
		self.info( tcpConnected )
		
		data = """GET / HTTP/1.1\r\nHost: www.google.fr\r\nUser-Agent: ExtensiveTesting\r\nConnection: keep-alive\r\n\r\n"""
		tcp.sendData(data=data)
		
		dataReceived = tcp.hasReceivedData( timeout=input('TIMEOUT'), data=TestOperators.Contains('301 Moved') )
		if dataReceived is None:
			self.abort( '200 OK not found' )
		self.info( dataReceived.get('SSL').get('ssl-data-decoded') )
		self.info( dataReceived.get('SSL', 'ssl-data-decoded') )
	
		tcp.disconnect()
		tcpDisconnected = tcp.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )
				
		self.step1.setPassed(actual="success")
class TESTCASE_TCP_SSL_CHECK_PEER_CERTIFICATE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		self.TCP_ADP= SutAdapters.TCP.Client(parent=self, bindIp='', bindPort=0, name=None, destinationIp='www.google.fr', 
																						destinationPort=443, destinationHost='', proxyType='socks4', proxyUserID='xtc', 
																						proxyIp='', proxyPort=3128, proxyHost='', proxyEnabled=False, 
																						socketTimeout=30, socketFamily=4, inactivityTimeout=30.0,
																						tcpKeepAlive=False, tcpKeepAliveInterval=30.0, 
																						separatorIn='\x00', separatorOut='\x00', 
																						separatorDisabled=True, sslSupport=True, sslVersion='TLSv1',
																						checkCert=SutAdapters.SSL.CHECK_CERT_REQUIRED, debug=input('DEBUG'), 
																						logEventSent=True,  caCerts="/etc/ssl/certs/ca-bundle.crt",
																						logEventReceived=True, parentName=None, 
																						agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'), shared=False)
																						
		self.TCP_ADP.connect()
		c = self.TCP_ADP.isConnected(timeout=5.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None)
		
		rsp = self.TCP_ADP.sendData(data='TRACE / HTTP/1.1\n\n')
		rsp = self.TCP_ADP.hasReceivedData(timeout=10.0, data=None, versionIp=None, sourceIp=None, destinationIp=None,
																																	sourcePort=None, destinationPort=None, sslVersion=None, sslCipher=None)
		
		self.TCP_ADP.disconnect()
		c = self.TCP_ADP.isDisconnected(timeout=5.0, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None)
		
		self.step1.setPassed(actual="success")
		
# sniffer
class TESTCASE_TCP_SNIFFER_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.tcp = SutAdapters.TCP.Sniffer(parent=self, debug=input('DEBUG'))
		
		self.step1.start()
		self.tcp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		tcpSniffing = self.tcp.isSniffing( timeout=input('TIMEOUT') )
		if not tcpSniffing:
			self.abort("unable to start to sniff")
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.tcp.stopListening()
	def definition(self):
		self.wait( 10 )
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_SNIFFER_CONN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.tcp = SutAdapters.TCP.Sniffer(parent=self, debug=input('DEBUG'), port2sniff=input('SRC_PORT') )
		
		self.step1.start()
		self.tcp.startListening(eth=input('INTERFACE'), srcIp=input('SRC_IP'))
		tcpSniffing = self.tcp.isSniffing( timeout=input('TIMEOUT') )
		if not tcpSniffing:
			self.abort()
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
		self.tcp.stopListening()
	def definition(self):
	
		self.tcp.SYN( destIp='173.194.69.103', srcPort=input('SRC_PORT'), destPort=input('DST_PORT_SSL'), 
									options='\x01\x00', optSegMax=300, optSackPermitted='supported' )
		if self.tcp.hasReceivedPacket( timeout=input('TIMEOUT'), srcPort=input('DST_PORT_SSL'), dstPort= input('SRC_PORT') ):
			self.tcp.ACK( destIp='173.194.69.103', srcPort=input('SRC_PORT'), destPort=input('DST_PORT_SSL'))
			self.wait(1)
			
		self.tcp.FIN( destIp='173.194.69.103', srcPort=input('SRC_PORT'), destPort=input('DST_PORT_SSL') )
		if self.tcp.hasReceivedPacket(timeout=input('TIMEOUT'), srcPort=input('DST_PORT_SSL'), dstPort= input('SRC_PORT')):
			self.wait( 5 )
			
		self.step1.setPassed(actual="success")


class TESTCASE_TCP_STACK_PASSIVE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.tcpStack = SutAdapters.TCP.Stack( parent=self, debug=input('DEBUG'), bindInterface=input('INTERFACE') )
		self.step1.start()
		
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
	def definition(self):

		connId = self.tcpStack.OPEN( localPort=(input('SRC_IP'),444), mode=SutAdapters.TCP.CONNECTION_PASSIVE)
		
		self.wait( 10 )
		
		self.tcpStack.CLOSE(connId=connId)
		
		self.step1.setPassed(actual="success")

class TESTCASE_TCP_STACK_ACTIVE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		self.tcpStack = SutAdapters.TCP.Stack( parent=self, debug=input('DEBUG'),
																						bindInterface=input('INTERFACE'))
		self.step1.start()
		
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
	def definition(self):

		connId = self.tcpStack.OPEN( localPort=(input('SRC_IP'), 333), remotePort=("127.0.0.1",80), mode=SutAdapters.TCP.CONNECTION_ACTIVE)
		
		self.wait( 2 )
		
		self.tcpStack.CLOSE(connId=connId)
		self.wait( 2 )
		
		self.step1.setPassed(actual="success")
# server
class TESTCASE_TCP_CLIENT_SERVER_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	
	def prepare(self):

		# adapters and libraries definitions
		self.ADP_CLIENT = SutAdapters.TCP.Client(parent=self, bindIp='', bindPort=0, destinationIp='127.0.0.1',
											destinationPort=500, destinationHost='', proxyIp='', proxyPort=3128, proxyHost='',
											proxyEnabled=False, socketTimeout=1, socketFamily=4, inactivityTimeout=30.0,
											tcpKeepAlive=False, tcpKeepAliveInterval=30.0, separatorIn='\x00',
											separatorOut='\x00', separatorDisabled=True, sslSupport=False, sslVersion='TLSv1', 
											checkCert='No', debug=input('DEBUG'), logEventSent=True, logEventReceived=True,
											parentName=None, agentSupport=False, agent=None, name='CLT_TCP')
		self.ADP_SERVER = SutAdapters.TCP.Server(parent=self, bindIp='', bindPort=500, socketTimeout=1, socketFamily=4,
											inactivityTimeout=30.0, tcpKeepAlive=False, tcpKeepAliveInterval=30.0, separatorIn='\x00',
											separatorOut='\x00', separatorDisabled=True, sslSupport=False, sslVersion='TLSv1', 
											checkCert='No', debug=input('DEBUG'), logEventSent=True, logEventReceived=True,
											name='SVR_TCP')
		

	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
	
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_SERVER.startListening()
		if not self.ADP_SERVER.isListening(timeout=input('TIMEOUT')):
			self.abort('fail to start tcp server')
		
		self.ADP_CLIENT.connect()
		if not self.ADP_CLIENT.isConnected(timeout=input('TIMEOUT'), versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'fail to connect to the server' )
			
		if not self.ADP_SERVER.hasClientConnection(timeout=input('TIMEOUT'), clientId=None):
			self.error( 'no connection detected from client' )
		else:
			self.info( 'new connection' )
		
		self.ADP_CLIENT.sendData(data='hello world')
		if not self.ADP_SERVER.hasClientData(timeout=1.0, clientId=None, data=None, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'no data received from client' )
		
		self.ADP_CLIENT.disconnect()
		if not self.ADP_CLIENT.isDisconnected(timeout=input('TIMEOUT'), byServer=False, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error('fail to disconnect properly from tcp server ')

		if not self.ADP_SERVER.hasClientDisconnection(timeout=input('TIMEOUT'), clientId='1'):
			self.error( 'no disconnection detected from client' )

		self.ADP_SERVER.stopListening()
		if not self.ADP_SERVER.isStopped(timeout=input('TIMEOUT')):
			self.abort('fail to stop tcp server properly')
		
		self.step1.setPassed(actual="success")
		
class TESTCASE_TCP_CLIENT_SERVER_SSL_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	
	def prepare(self):

		# adapters and libraries definitions
		self.ADP_CLIENT = SutAdapters.TCP.Client(parent=self, bindIp='', bindPort=0, destinationIp='127.0.0.1',
											destinationPort=500, destinationHost='', proxyIp='', proxyPort=3128, proxyHost='',
											proxyEnabled=False, socketTimeout=1, socketFamily=4, inactivityTimeout=30.0,
											tcpKeepAlive=False, tcpKeepAliveInterval=30.0, separatorIn='\x00',
											separatorOut='\x00', separatorDisabled=True, sslSupport=True, sslVersion='TLSv1', 
											checkCert='No', debug=False, logEventSent=True, logEventReceived=True,
											parentName=None, agentSupport=False, agent=None)
		self.ADP_SERVER = SutAdapters.TCP.Server(parent=self, bindIp='', bindPort=500, socketTimeout=1, socketFamily=4,
											inactivityTimeout=30.0, tcpKeepAlive=False, tcpKeepAliveInterval=30.0, separatorIn='\x00',
											separatorOut='\x00', separatorDisabled=True, sslSupport=True, sslVersion='TLSv1', 
											checkCert='No', debug=False, logEventSent=True, logEventReceived=True, parentName=None)
		

	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)

	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_SERVER.startListening()
		if not self.ADP_SERVER.isListening(timeout=input('TIMEOUT')):
			self.abort('fail to start tcp server')
		
		self.ADP_CLIENT.connect()
		if not self.ADP_CLIENT.isConnected(timeout=input('TIMEOUT'), versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'fail to connect to the server' )
			
		if not self.ADP_SERVER.hasClientConnection(timeout=input('TIMEOUT'), clientId=None):
			self.error( 'no connection detected from client' )
		else:
			self.info( 'new connection' )
		
		self.ADP_CLIENT.sendData(data='hello world')
		if not self.ADP_SERVER.hasClientData(timeout=1.0, clientId=None, data=None, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error( 'no data received from client' )
		
		self.ADP_CLIENT.disconnect()
		if not self.ADP_CLIENT.isDisconnected(timeout=input('TIMEOUT'), byServer=False, versionIp=None, sourceIp=None, destinationIp=None, sourcePort=None, destinationPort=None):
			self.error('fail to disconnect properly from tcp server ')

		if not self.ADP_SERVER.hasClientDisconnection(timeout=input('TIMEOUT'), clientId='1'):
			self.error( 'no disconnection detected from client' )

		self.ADP_SERVER.stopListening()
		if not self.ADP_SERVER.isStopped(timeout=input('TIMEOUT')):
			self.abort('fail to stop tcp server properly')		
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_TCP_01(suffix=None).execute()
TESTCASE_TCP_SSL_01(suffix=None).execute()

if not input('SUPPORT_AGENT'):
	TESTCASE_TCP_TIMEOUT_01(suffix=None).execute()
	TESTCASE_TCP_FAILED_01(suffix=None).execute()
	TESTCASE_TCP_REFUSED_01(suffix=None).execute()
	TESTCASE_TCP_SSL_CHECK_PEER_CERTIFICATE_01(suffix=None).execute()

	TESTCASE_TCP_SNIFFER_01(suffix=None).execute()
	TESTCASE_TCP_SNIFFER_CONN_01(suffix=None).execute()

	TESTCASE_TCP_STACK_PASSIVE_01(suffix=None).execute()
	TESTCASE_TCP_STACK_ACTIVE_01(suffix=None).execute()

	TESTCASE_TCP_CLIENT_SERVER_01(suffix=None).execute()
	TESTCASE_TCP_CLIENT_SERVER_SSL_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105844.99</testdevelopment>
</file>