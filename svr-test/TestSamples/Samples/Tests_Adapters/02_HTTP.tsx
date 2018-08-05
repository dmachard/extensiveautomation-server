<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT_SOCKET</name><type /></agent></agents><descriptions><description><value /><key>author</key></description><description><value /><key>creation date</key></description><description><value /><key>summary</key></description><description><value /><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><color /><description /><value>True</value><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>www.google.fr</value><name>DST_HOSTNAME</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>www.google.fr</value><name>DST_IP</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>80</value><name>DST_PORT</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>443</value><name>DST_PORT_SSL</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>localhost</value><name>DST_URL</name><type>text</type><scope>local</scope></parameter><parameter><color /><description /><value>fr.yahoo.com</value><name>HOST</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>54.201.125.134 </value><name>PROXY_IP_HTTP</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>141.255.166.42 </value><name>PROXY_IP_SOCKS4</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>62.255.82.98</value><name>PROXY_IP_SOCKS5</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>1080</value><name>PROXY_PORT</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>3128</value><name>PROXY_PORT_HTTP</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>False</value><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>10.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA['''
Test Definition
'''

class HTTP_CLIENT_CONTRUCT_TPL_FROM_RAW_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
		
	def prepare(self):

		# adapters
		self.ADP_HTTP =  SutAdapters.HTTP.Client( parent=self, debug=input('DEBUG'), destinationIp=input('DST_URL'),
																														destinationPort=input('DST_PORT') ,
																														agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))
		

		self.ADP_HTTP.connect()
		tcpConnected = self.ADP_HTTP.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
	def cleanup(self, aborted):
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
				self.error( 'TCP Not Disconnected' )		
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		rawHttp = [ "GET / HTTP/1.1" ]
		rawHttp.append( "Host: %s" % input('DST_URL') )
		rawHttp.append( "User-Agent: Mozilla/5.0 (Windows NT 6.3; WOW64; rv:26.0) Gecko/20100101 Firefox/26.0" )
		rawHttp.append( "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" )
		rawHttp.append( "Accept-Language: fr,fr-fr;q=0.8,en-us;q=0.5,en;q=0.3" )
		rawHttp.append( "Accept-Encoding: gzip, deflate" )
		rawHttp.append( "Cookie: sessionid=YToyOntzOjE4OiJfUFhfUGx1Zl9Vc2VyX2F1dGgiO2k6Mzt" )
		rawHttp.append( "Connection: keep-alive" )
		rawHttp.append( "" )
		
		req_tpl = self.ADP_HTTP.constructTemplateRequest(rawHttp=rawHttp)
		req = self.ADP_HTTP.sendRequest(tpl=req_tpl)
		self.info( req )

		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer( SutAdapters.IPLITE.ip( more=SutAdapters.IPLITE.received() ) )
		tpl.addLayer(  SutAdapters.TCP.tcp(more=SutAdapters.TCP.received()) )
		headers = { 'server':  TestOperators.Contains(needle='Apache', AND=True, OR=False) }
		
		tpl.addLayer( SutAdapters.HTTP.response( version="HTTP/1.1", code=TestOperators.GreaterThan(x="100"), headers=headers) )

		rsp = self.ADP_HTTP.hasReceivedResponse(expected=tpl, timeout=input('TIMEOUT'))
		if rsp is None:
			self.setFailed()
		else:
			self.info(rsp)
class HTTP_CLIENT_RAW(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client( parent=self, debug=input('DEBUG'), 
																			 destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'),
																			agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)	
	def definition(self):
		self.step1.start()
		

		# connect 
		self.ADP_HTTP.connect()
		tcpConnected = self.ADP_HTTP.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
			
		# send request
		hdrs = { "Host": input('HOST') , "User-Agent": "ExtensiveTesting" ,  "Connection": "Keep-Alive" }
		req_tpl = SutAdapters.HTTP.request(method='GET', uri="/", version="HTTP/1.1", headers=hdrs)
		req = self.ADP_HTTP.sendRequest(tpl=req_tpl)
		self.info( req )
		
		#prepare the expected template
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer( SutAdapters.IPLITE.ip( more=SutAdapters.IPLITE.received() ) )
		tpl.addLayer(  SutAdapters.TCP.tcp(more=SutAdapters.TCP.received()) )
		headers = { TestOperators.Contains(needle='date'): TestOperators.Any() }
		
		tpl.addLayer( SutAdapters.HTTP.response( version="HTTP/1.1", code=TestOperators.GreaterThan(x="100"), phrase=TestOperators.Any(), headers=headers) )
		
		# wait to match response
		rsp = self.ADP_HTTP.hasReceivedResponse(expected=tpl, timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed(actual="no reponse")	
		else:
			self.info(rsp)
			self.info( rsp.get('HTTP', 'headers').get('Set-Cookie') )
		
		# optional
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )				
		self.step1.setPassed(actual="success")	

class HTTP_CLIENT_RAW2(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(
																				parent=self, debug=input('DEBUG'), 
																				destinationIp=input('DST_IP'), destinationPort=input('DST_PORT_SSL'),
																				sslSupport = True, agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')
																			)
		
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)	
	def definition(self):
		self.step1.start()

		# connect 
		self.ADP_HTTP.connect()
		tcpConnected = self.ADP_HTTP.isConnected( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'TCP Not Connected' )
		sslConnected = self.ADP_HTTP.isConnectedSsl( timeout=input('TIMEOUT') )
		if not tcpConnected:
			self.abort( 'SSL Not Connected' )
			
		# send request
		hdrs = { "Host": input('HOST') , "User-Agent": "ExtensiveTesting" ,  "Connection": "Close", }
		req_tpl = SutAdapters.HTTP.request(method='GET', uri="/", version="HTTP/1.1", headers=hdrs, body='')
		self.ADP_HTTP.sendRequest(tpl=req_tpl)
		
		#prepare the expected template
		tpl = TestTemplates.TemplateMessage()
		tpl.addLayer( SutAdapters.IPLITE.ip( more=SutAdapters.IPLITE.received() ) )
		tpl.addLayer(  SutAdapters.TCP.tcp(more=SutAdapters.TCP.received()) )
		tpl.addLayer(  SutAdapters.SSL.ssl(more=SutAdapters.SSL.received()) )
		headers = { TestOperators.Contains(needle='date'): TestOperators.Any() }
		tpl.addLayer( SutAdapters.HTTP.response( version="HTTP/1.1", code=TestOperators.GreaterThan(x="199"), phrase=TestOperators.Any() , headers=headers) )
		
		# wait to match response
		rsp = self.ADP_HTTP.hasReceivedResponse(expected=tpl, timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed(actual="error")	
			
		# optional
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )				
		self.step1.setPassed(actual="success")			
				
class HTTP_CLIENT_GET(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'), 
																		debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	
				
class HTTP_CLIENT_GET_ADD_HEADERS(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'),
										debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		headers = { 'test': 't' }
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT'), headers=headers )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	
			
class HTTP_CLIENT_GET_OVERWRITE_HEADERS(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'), 
									debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		headers = { 'User-Agent': 'test' }
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT'), headers=headers )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	
				
class HTTP_CLIENT_GET_EXPECTED_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('HOST'), destinationPort=input('DST_PORT'), 
											debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT'),
											versionExpected=TestOperators.Endswith(needle='1.1') ,
											codeExpected=TestOperators.NotContains(needle='200') ,
											phraseExpected=TestOperators.NotContains(needle='TOTO')  )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	

class HTTP_CLIENT_GET_EXPECTED_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('HOST'), destinationPort=input('DST_PORT'), 
													debug=input('DEBUG') , agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		headersExpected = { TestOperators.Contains(needle='server'): TestOperators.Any() }
	
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT'),
											headersExpected=headersExpected
											)
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	
				
class HTTP_CLIENT_POST_BODY_UTF8(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'), 
											debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		headers = {"content-type": "text; charset=utf8"} 
		bExample = u"é"
		rsp = self.ADP_HTTP.POST( uri="/", host=input('HOST'), headers=headers, timeout=input('TIMEOUT'), body=bExample )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.step1.setPassed(actual="success")	
			
		# send GET request
#		headers = {} 
#		bExample = "é"
#		rsp = self.ADP_HTTP.POST( uri="/", host=input('HOST'), headers=headers, timeout=input('TIMEOUT'), body=bExample )
#		if rsp is None:
#			self.step1.setFailed(actual="error")	
#		else:
#			self.step1.setPassed(actual="success")	
			
class HTTP_CLIENT_POST_WITH_DATA_CONTENT_LENGTH(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client( parent=self, destinationIp=input('DST_IP'), destinationPort=input('DST_PORT'), 
																				debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		bodyHttp = "just for tes"
		# , headers={"écontent-type":  "text/html charset=utf-8"} 
		rsp = self.ADP_HTTP.POST( uri="/", host=input('HOST'), timeout=input('TIMEOUT'), body=bodyHttp,
																	 )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			self.info( rsp.get('HTTP', 'body' ) )
			self.step1.setPassed(actual="success")	
				
class HTTP_CLIENT_GET_RESOLV_HOST(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'), destinationPort=input('DST_PORT'), 
										debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
										
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host="", timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		else:
			http_headers = rsp.get('HTTP', 'headers' )
			self.info(http_headers.get('connection'))
			
			self.step1.setPassed(actual="success")	
				
class HTTP_CLIENT_GET_CLOSE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'), destinationPort=input('DST_PORT'),
																				httpConnection=SutAdapters.HTTP.CONN_CLOSE, debug=input('DEBUG'),
																			agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)	
	def definition(self):
		self.step1.start()

		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error get")	
			
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT'))
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )			
		
		# second GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")	
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )				
	
		self.step1.setPassed(actual="success")		
				
class HTTP_CLIENT_GET_KEEPALIVE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'), destinationPort=input('DST_PORT'),
																				httpConnection=SutAdapters.HTTP.CONN_KEEPALIVE, debug=input('DEBUG'),
																				agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)	
	def definition(self):
		self.step1.start()

		for i in xrange(10):
			# send GET request
			rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT') )
			if rsp is None:
				self.step1.setFailed(actual="error")	
				
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )		
		
		self.step1.setPassed(actual="success")	

class HTTP_CLIENT_MULTI_GET_CLOSE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'),
												destinationPort=input('DST_PORT'), debug=input('DEBUG') ,
												agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)
	def definition(self):
		self.step1.start()

		for i in xrange(10):
			# send GET request
			rsp = self.ADP_HTTP.GET( uri="/", host=input('HOST'), timeout=input('TIMEOUT') )
			if rsp is None:
				self.step1.setFailed(actual="error")
			# close 
			self.ADP_HTTP.disconnect()
			tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
			if not tcpDisconnected:
				self.abort( 'TCP Not Disconnected' )			
			self.step1.setPassed(actual="success")	

class HTTP_CLIENT_GET_THROUGH_SSL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)				
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'),
												destinationPort=input('DST_PORT_SSL'), sslSupport=True, debug=input('DEBUG'),
											agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host="", timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")

class HTTP_CLIENT_MULTI_GET_CLOSE_THROUGH_SSL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'),
												destinationPort=input('DST_PORT_SSL'), sslSupport=True, debug=input('DEBUG'),
											agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)
	def definition(self):
		self.step1.start()

		for i in xrange(10):
			# send GET request
			rsp = self.ADP_HTTP.GET( uri="/", host="", timeout=input('TIMEOUT') )
			if rsp is None:
				self.step1.setFailed(actual="error")
			self.ADP_HTTP.disconnect()
			tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
			if not tcpDisconnected:
				self.abort( 'TCP Not Disconnected' )						
			self.step1.setPassed(actual="success")

class HTTP_CLIENT_MULTI_GET_KEEPALIVE_THROUGH_SSL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		
		# configure adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'),
												destinationPort=input('DST_PORT_SSL'), httpConnection=SutAdapters.HTTP.CONN_KEEPALIVE, 
												sslSupport=True, debug=input('DEBUG'), agent=agent('AGENT_SOCKET'), 
												agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed("success")
	def definition(self):
		self.step1.start()

		for i in xrange(20):
			# send GET request
			rsp = self.ADP_HTTP.GET( uri="/", host="", timeout=input('TIMEOUT') )
			if rsp is None:
				self.step1.setFailed(actual="error")
		
		self.ADP_HTTP.disconnect()
		tcpDisconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not tcpDisconnected:
			self.abort( 'TCP Not Disconnected' )							
		self.step1.setPassed(actual="success")

class HTTP_CLIENT_GET_IMAGE_PNG(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
			
			# configure adapter
			self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_HOSTNAME'),
																				destinationPort=input('DST_PORT'), debug=input('DEBUG'),
																				saveContent=True, truncateBody=False,
																			agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
	def cleanup(self, aborted):
		pass
	def definition(self):
			self.step1.start()

			# send GET request
			rsp = self.ADP_HTTP.GET( uri="/images/srpr/logo11w.png", host="", timeout=input('TIMEOUT') )
			if rsp is None:
				self.step1.setFailed(actual="error")
			else:
				self.info( 'image downloaded' )
				self.step1.setPassed(actual="success")

class HTTP_CLIENT_GET_AUTHENTICATION(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationIp=input('DST_URL'), destinationPort=input('DST_PORT'), 
															debug=input('DEBUG'), supportAuthentication=True,
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
		
		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/web/index.php", host=input('DST_URL'), login='code', password='!xxxx', 
																					timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
			
		rsp = self.ADP_HTTP.TRACE( uri="/web/index.php", host=input('DST_URL'), login='code', 
																							password='!xxxx', timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")

class HTTP_CLIENT_PROXY_SOCKS4_GET(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationHost=input('HOST'), destinationPort=input('DST_PORT'), 
															debug=input('DEBUG'), supportAuthentication=False, sslSupport=False, proxyType=SutAdapters.TCP.PROXY_SOCKS4,
															proxyIp=input('PROXY_IP_SOCKS4'), proxyPort=input('PROXY_PORT'), proxyEnabled=True,
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()


		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('DST_URL'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")
		
class HTTP_CLIENT_PROXY_SOCKS5_GET(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationHost=input('HOST'), destinationPort=input('DST_PORT'), 
															debug=input('DEBUG'), supportAuthentication=False, sslSupport=False, proxyType=SutAdapters.TCP.PROXY_SOCKS5,
															proxyIp=input('PROXY_IP_SOCKS5'), proxyPort=input('PROXY_PORT'), proxyEnabled=True,
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()


		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('DST_URL'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")
		
class HTTP_CLIENT_PROXY_HTTP_GET(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)					
	def prepare(self):
		
		# prepare adapter
		self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, destinationHost=input('HOST'), destinationPort=input('DST_PORT'), 
															debug=input('DEBUG'), supportAuthentication=False, sslSupport=False, proxyType='http',
															proxyIp=input('PROXY_IP_HTTP'), proxyPort=input('PROXY_PORT_HTTP'), proxyEnabled=True,
															agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()


		# send GET request
		rsp = self.ADP_HTTP.GET( uri="/", host=input('DST_URL'), timeout=input('TIMEOUT') )
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA['''
Test Execution
'''
if not input('SUPPORT_AGENT'):
	HTTP_CLIENT_CONTRUCT_TPL_FROM_RAW_01().execute()
	HTTP_CLIENT_RAW().execute()
	HTTP_CLIENT_RAW2().execute()
	
HTTP_CLIENT_GET().execute()
HTTP_CLIENT_GET_ADD_HEADERS().execute()
HTTP_CLIENT_GET_OVERWRITE_HEADERS().execute()
HTTP_CLIENT_GET_EXPECTED_01().execute()
HTTP_CLIENT_GET_EXPECTED_02().execute()
HTTP_CLIENT_POST_BODY_UTF8().execute()
HTTP_CLIENT_POST_WITH_DATA_CONTENT_LENGTH().execute()
HTTP_CLIENT_GET_RESOLV_HOST().execute()

HTTP_CLIENT_GET_CLOSE().execute()
HTTP_CLIENT_GET_KEEPALIVE().execute()
HTTP_CLIENT_MULTI_GET_CLOSE().execute()

HTTP_CLIENT_GET_THROUGH_SSL().execute()
HTTP_CLIENT_MULTI_GET_CLOSE_THROUGH_SSL().execute()
HTTP_CLIENT_MULTI_GET_KEEPALIVE_THROUGH_SSL().execute()

HTTP_CLIENT_GET_IMAGE_PNG().execute()

#HTTP_CLIENT_GET_AUTHENTICATION().execute()

#HTTP_CLIENT_PROXY_SOCKS4_GET().execute()
#HTTP_CLIENT_PROXY_SOCKS5_GET().execute()
#HTTP_CLIENT_PROXY_HTTP_GET().execute()]]></testexecution>
<testdevelopment>1386105836.89</testdevelopment>
</file>