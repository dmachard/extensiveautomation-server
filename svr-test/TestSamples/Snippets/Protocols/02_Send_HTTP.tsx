<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><probes><probe><name>probe01</name><type>default</type><active>False</active><args /></probe></probes><descriptions><description><value>admin</value><key>author</key></description><description><value>23/12/2016 16:25:36</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><value>SVR</value><name>CACHE_KEY_SVR</name><type>str</type><scope>local</scope></parameter><parameter><description /><value>False</value><name>CHECK_HOST</name><type>bool</type><scope>local</scope></parameter><parameter><description /><value>False</value><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><description /><value>{ 
   "login": "[!CACHE:LOGIN:]", 
   "password": "[!CACHE:PWD_HASH:]"
}</value><name>HTTP_REQ_BODY</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>hello: world
# example of a comment</value><name>HTTP_REQ_HEADERS</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>POST</value><name>HTTP_REQ_METHOD</name><type>str</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>/session/login</value><name>HTTP_REQ_URI</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value /><name>HTTP_RSP_BODY</name><type>text</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>200</value><name>HTTP_RSP_CODE</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>set-cookie: session_id=.*;expires=.*
server: .*</value><name>HTTP_RSP_HEADERS</name><type>text</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>OK</value><name>HTTP_RSP_PHRASE</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>HTTP/1.[0|1]</value><name>HTTP_RSP_VERSION</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>1:Common:SAMPLE_NODE:</value><name>SERVERS</name><type>global</type><color>#FDFFBD</color><scope>local</scope></parameter><parameter><description /><value>Http response received</value><name>STEP_EXPECTED</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>Send http request</value><name>STEP_SUMMARY</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>Send http request and wait response</value><name>TEST_PURPOSE</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>10.0</value><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter><parameter><description /><value>20.0</value><name>TIMEOUT_CONNECT</name><type>float</type><color /><scope>local</scope></parameter><parameter><description /><value>True</value><name>VERBOSE</name><type>bool</type><color /><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><value>1.0</value><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></outputs-parameters><agents><agent><description /><value>agent-dummy01</value><name>AGENT</name><type>dummy</type></agent></agents></properties>
<testdefinition><![CDATA[
class SEND_HTTP_01(TestCase):
	def description(self, svr):
		# testcase description
		self.setPurpose(purpose=input('TEST_PURPOSE'))
		self.setRequirement(requirement=description('requirement'))
	
		Cache().set(name=input('CACHE_KEY_SVR'), data=svr, flag=False)
		
		# steps description
		self.step1 = self.addStep(expected=input('STEP_EXPECTED'), 
																				description=input('STEP_SUMMARY'), 
																				summary=input('STEP_SUMMARY'), enabled=True)
	def prepare(self, svr):
		self.ADP_HTTP = None
		
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
		
			if "HTTP_DEST_HOST" not in svr: self.abort( "HTTP_DEST_HOST key expected on provided server. more details\n%s" % svr  )
			if "HTTP_DEST_PORT" not in svr: self.abort( "HTTP_DEST_PORT key expected on provided server. more details\n%s" % svr  )
			if "HTTP_DEST_SSL" not in svr: self.abort( "HTTP_DEST_SSL key expected on provided server. more details\n%s" % svr  )
			if "HTTP_AGENT_SUPPORT" not in svr: self.abort( "HTTP_AGENT_SUPPORT key expected on provided server. more details\n%s" % svr  )
			if "HTTP_AGENT" not in svr: self.abort( "HTTP_AGENT key expected on provided server. more details\n%s" % svr  )
			
			_hostname = None
			if "HTTP_HOSTNAME" in svr:
				_hostname = svr["HTTP_HOSTNAME"]
				
			self.ADP_HTTP = SutAdapters.HTTP.Client(parent=self, name=None, bindIp='', bindPort=0, 
																																	destinationIp=svr['HTTP_DEST_HOST'],  destinationPort=int(svr['HTTP_DEST_PORT']), 
																																	debug=input('DEBUG'), logEventSent=True, sslSupport=svr['HTTP_DEST_SSL'],
																																	logEventReceived=True, httpAgent='ExtensiveTesting',  
																																	hostCn=_hostname, checkHost=input('CHECK_HOST'),
																																	agentSupport=svr['HTTP_AGENT_SUPPORT'], agent=svr['HTTP_AGENT'], 
																																	shared=False, verbose=input('VERBOSE'))
																																
	
	def definition(self, svr):
		# send request
		reqHeaders = {}
		for hv in input('HTTP_REQ_HEADERS').splitlines():
			if hv.startswith("#"): continue 
			if ":" not in hv: self.abort("request headers malformed (%s)" % hv)
			k, v = hv.split(":", 1)
			reqHeaders[k.strip()] = v.strip()

		self.ADP_HTTP.sendHttp(uri=input('HTTP_REQ_URI'), host=svr['HTTP_DEST_HOST'], 
																			 method=input('HTTP_REQ_METHOD'), headers=reqHeaders, 
																			 body=input('HTTP_REQ_BODY'), timeout=input('TIMEOUT_CONNECT'))
		
		# handle response
		rspHeaders = {}
		for hv in input('HTTP_RSP_HEADERS').splitlines():
			if hv.startswith("#"): continue 
			if ":" not in hv: self.abort("response headers malformed (%s)" % hv)
			k, v = hv.split(":", 1)
			rspHeaders[TestOperators.RegEx(needle=k.strip())] = TestOperators.RegEx(needle=v.strip())

		if not len(input('HTTP_RSP_BODY')):
			httpBody = None
			bodyRegexp = ""
		else:
			bodyRegexp = ".*".join(input('HTTP_RSP_BODY').splitlines())
			httpBody = TestOperators.RegEx(needle=".*%s.*" % bodyRegexp)
		rsp= self.ADP_HTTP.hasReceivedHttpResponse(httpCode=input('HTTP_RSP_CODE'), httpPhrase=input('HTTP_RSP_PHRASE'), 
																																			httpVersion=TestOperators.RegEx(needle=input('HTTP_RSP_VERSION')),
																																			timeout=input('TIMEOUT'), 
																																			httpHeaders=rspHeaders, httpBody=httpBody)
		if rsp is None: self.abort("expected http response not received")

		# capture http headers
		rspHdrs = rsp.get("HTTP", "headers").getItems()
		for (k1, v1) in rspHdrs:
			for hv2 in input('HTTP_RSP_HEADERS').splitlines():
				k2, v2 = hv2.split(":", 1)
				Cache().capture(data="%s:%s" % (k1.strip(), v1.strip()), regexp="%s:%s" % (k2.strip(), v2.strip()) )
		
		# capture http body
		rspBody = rsp.get("HTTP", "body")
		if rspBody is not None:
			Cache().capture(data=rspBody, regexp=bodyRegexp)
		
		self.step1.setPassed(actual="success")
	def cleanup(self, aborted, svr):
		if aborted: self.step1.setFailed(actual="%s" % aborted)
		if self.ADP_HTTP is not None:
			self.ADP_HTTP.disconnect()]]></testdefinition>
<testexecution><![CDATA[
servers = input('SERVERS')
if servers is None: AbortTestSuite("no server provided")

if servers is None: AbortTestSuite(reason="no server provided")
if not isinstance(servers, list): servers = [ input('SERVERS') ]
	
for svr in servers:
	SEND_HTTP_01(suffix=None).execute(svr=svr)]]></testexecution>
<testdevelopment>1482506736.49494</testdevelopment>
</file>