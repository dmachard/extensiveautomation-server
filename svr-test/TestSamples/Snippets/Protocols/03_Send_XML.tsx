<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><probes><probe><name>probe01</name><type>default</type><active>False</active><args /></probe></probes><descriptions><description><value>admin</value><key>author</key></description><description><value>23/12/2016 16:25:36</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><value>SVR</value><name>CACHE_KEY_SVR</name><type>str</type><scope>local</scope></parameter><parameter><description /><value>False</value><name>CHECK_HOST</name><type>bool</type><scope>local</scope></parameter><parameter><description /><value>False</value><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><description /><value>{ 
   "login": "[!CACHE:LOGIN:]", 
   "password": "[!CACHE:PWD_HASH:]"
}</value><name>HTTP_REQ_BODY</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>hello: world
# example of a comment</value><name>HTTP_REQ_HEADERS</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>POST</value><name>HTTP_REQ_METHOD</name><type>str</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value>/session/login</value><name>HTTP_REQ_URI</name><type>text</type><color>#D4FFAF</color><scope>local</scope></parameter><parameter><description /><value /><name>HTTP_RSP_BODY</name><type>text</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>200</value><name>HTTP_RSP_CODE</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>set-cookie: session_id=.*;expires=.*
server: .*</value><name>HTTP_RSP_HEADERS</name><type>text</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>n	aaaa</value><name>HTTP_RSP_NAMESPACES</name><type>text</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>OK</value><name>HTTP_RSP_PHRASE</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>HTTP/1.[0|1]</value><name>HTTP_RSP_VERSION</name><type>str</type><color>#FCABBD</color><scope>local</scope></parameter><parameter><description /><value>1:Common:SAMPLE_NODE:</value><name>SERVERS</name><type>global</type><color>#FDFFBD</color><scope>local</scope></parameter><parameter><description /><value>XML response received</value><name>STEP_EXPECTED</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>Send XML request</value><name>STEP_SUMMARY</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>Send XML request and wait response</value><name>TEST_PURPOSE</name><type>text</type><color>#C1EEFF</color><scope>local</scope></parameter><parameter><description /><value>10.0</value><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter><parameter><description /><value>20.0</value><name>TIMEOUT_CONNECT</name><type>float</type><color /><scope>local</scope></parameter><parameter><description /><value>True</value><name>VERBOSE</name><type>bool</type><color /><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><value>1.0</value><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></outputs-parameters><agents><agent><description /><value>agent-dummy01</value><name>AGENT</name><type>dummy</type></agent></agents></properties>
<testdefinition><![CDATA[
class SEND_XML_01(TestCase):
	def description(self, svr):
		# testcase description
		self.setPurpose(purpose=input('TEST_PURPOSE'))
		self.setRequirement(requirement=description('requirement'))
	
		Cache().set(name=input('CACHE_KEY_SVR'), data=svr, flag=False)
		
		# steps description
		self.step1 = self.addStep(expected=input('STEP_EXPECTED'), 
																				description=input('STEP_SUMMARY'), 
																				summary=input('STEP_SUMMARY'), enabled=True)
		self.msg_decodage = [  ]
	def prepare(self, svr):
		self.ADP_HTTP = None
		self.LIB_XML = None
		
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
				
			self.LIB_XML = SutLibraries.Codecs.XML(parent=self, debug=False, coding='UTF-8', name=None, shared=False)
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
			
			param_v_cache = re.findall("\[\!FROM\:CACHE\:.*\:\]", v)
			if param_v_cache :
				cache_v_key = v.split("[!FROM:CACHE:")[1].split(":]")[0]
				v = Cache().get(name=cache_v_key)
				
			param_k_cache = re.findall("\[\!FROM\:CACHE\:.*\:\]", k)
			if param_k_cache :
				cache_k_key = k.split("[!FROM:CACHE:")[1].split(":]")[0]   
				k = Cache().get(name=cache_k_key)

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

		rest_soap= self.ADP_HTTP.hasReceivedHttpResponse(httpCode=input('HTTP_RSP_CODE'), httpPhrase=input('HTTP_RSP_PHRASE'), 
																																			httpVersion=TestOperators.RegEx(needle=input('HTTP_RSP_VERSION')), timeout=input('TIMEOUT'), 
																																			httpHeaders=rspHeaders, httpBody=None)
		if rest_soap is None: self.abort("expected xml response not received")
		
		self.ADP_HTTP.disconnect()
		
		self.msg_decodage.append( "Checks of the response:<br />" )

		# capture http headers
		hdrs_rsp = rest_soap.get("HTTP", "headers").getItems()
		for (k1, v1) in hdrs_rsp:
			for hv2 in input('HTTP_RSP_HEADERS').splitlines():
				k2, v2 = hv2.split(":", 1)
				Cache().capture(data="%s:%s" % (k1.strip(), v1.strip()), regexp="%s:%s" % (k2.strip(), v2.strip()) )

		# search xml content type in response
		hdrs_rsp = rest_soap.get("HTTP", "headers").getItems()
		xml_hdr = False
		for (k1, v1) in hdrs_rsp:
			if k1.lower() == "content-type":
				if "xml" in v1.lower():
					xml_hdr = True
					break
		if not xml_hdr:
			self.msg_decodage.append("Searching xml in response: KO")
			self.abort("http response received but without xml in body")
		else:
			self.msg_decodage.append("Searching xml in response: OK")

		# checking if the xml provided is valid
		body_rsp = rest_soap.get("HTTP", "body")
		if body_rsp is None:  self.abort("the body in the http response is empty")

		# vérification du format du paramètre body
		from lxml import etree
		
		ns = {}
		for line in input('HTTP_RSP_NAMESPACES').splitlines():
			ns_expected = re.split(r'\t+', line)
			if len(ns_expected) != 2:
				self.abort("bad namespaces provided n°%s value=%s, expected <name>\\t<namespace>" % (n,line) )
			ns_name, namespace = ns_expected
			ns[ns_name] = namespace
		if self.LIB_XML .isValid(xml=body_rsp):
			self.msg_decodage.append("Decode XML from response: OK")
			xml_valid= True
		else:
			self.msg_decodage.append("Decode XML from response: KO")
			xml_valid= False
			
		# vérification du format du paramètre body
		n = 1
		for line in input('HTTP_RSP_BODY').splitlines():
			if line.startswith("#"): continue 
			xpath_expected = re.split(r'\t+', line)
			if len(xpath_expected) != 2:
				self.abort("bad expected body provided n°=%s value=%s, expected <xpath>\\t<regexp>" % (n,line) )
			xpath, xvalue = xpath_expected
	
			# full string
			xml_values = self.LIB_XML .getValues(xpath=xpath, xml=body_rsp, ns=ns)
			if not len(xml_values):
				self.msg_decodage.append( "Searching '%s' with the value '%s' : KO" % (xpath, xvalue) )
				xml_valid = False
			else:
				xml_values_valid = True
	
				# search capture regexp
				cap = re.findall("\(\?P\<.*\>.*\)", xvalue)
				param_input = re.findall("\[\!FROM\:INPUT\:.*\:\]", xvalue)
				param_cache = re.findall("\[\!FROM\:CACHE\:.*\:\]", xvalue)
				
				if cap :
					cache_key = xvalue.split("(?P<")[1].split(">.*)")[0]
					if len(xml_values) == 1:
						Cache().capture(data="%s" % xml_values[0], regexp=xvalue)
					else:
						Cache().set(name=cache_key, data=xml_values, flag=False)
					self.msg_decodage.append( "Searching and capture value of '%s' : OK" % (xpath) )
					
				else:
					if param_input :
						input_key = xvalue.split("[!FROM:INPUT:")[1].split(":]")[0]
						xvalue = input(name=input_key)
	
					if param_cache :
						cache_key = xvalue.split("[!FROM:CACHE:")[1].split(":]")[0]
						xvalue = Cache().get(name=cache_key)
						if xvalue is None: self.abort("the key %s does not exists in the cache" % cache_key)
	
					for jv in xml_values:
						jv = str(jv)
						reg = TestOperators.RegEx(needle=xvalue)
						if not reg.seekIn(haystack=jv):
							self.msg_decodage.append( "Searching '%s' with the value '%s' : KO" % (xpath, xvalue) )
							xml_values_valid = False
							self.msg_decodage.append( " > received value: %s" % jv.encode("utf8") )
	
					if xml_values_valid:
						self.msg_decodage.append( "Searching '%s' with the value '%s' : OK" % (xpath, xvalue) )
					else:
						xml_valid = False
	
			n += 1
	
		if xml_valid:
			self.step1.setPassed(actual="The response is OK. %s" % "<br />".join(self.msg_decodage) )
		else:
			self.step1.setFailed(actual="The response is KO. %s" %	"<br />".join(self.msg_decodage))

	def cleanup(self, aborted, svr):
		if aborted: self.step1.setFailed(actual="%s. %s" % (aborted, "<br />".join(self.msg_decodage) ) )
		if self.ADP_HTTP is not None:
			self.ADP_HTTP.disconnect()]]></testdefinition>
<testexecution><![CDATA[
servers = input('SERVERS')
if servers is None: AbortTestSuite("no server provided")

if servers is None: AbortTestSuite(reason="no server provided")
if not isinstance(servers, list): servers = [ input('SERVERS') ]
	
for svr in servers:
	SEND_XML_01(suffix=None).execute(svr=svr)]]></testexecution>
<testdevelopment>1482506736.49494</testdevelopment>
</file>