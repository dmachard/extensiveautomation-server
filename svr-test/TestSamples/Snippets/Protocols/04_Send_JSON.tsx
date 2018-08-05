<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>23/12/2016 16:25:36</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><probes><probe><args /><active>False</active><type>default</type><name>probe01</name></probe></probes><agents><agent><type>dummy</type><description /><value>agent-dummy01</value><name>AGENT</name></agent></agents><outputs-parameters><parameter><color /><description /><value>1.0</value><type>float</type><name>TIMEOUT</name><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><type>str</type><description /><value>SVR</value><name>CACHE_KEY_SVR</name><scope>local</scope></parameter><parameter><value>False</value><type>bool</type><name>CHECK_HOST</name><description /><scope>local</scope></parameter><parameter><color /><description /><value>False</value><type>bool</type><name>DEBUG</name><scope>local</scope></parameter><parameter><color>#D4FFAF</color><description /><value>{ 
   "login": "[!CACHE:LOGIN:]", 
   "password": "[!CACHE:PWD_HASH:]"
}</value><type>text</type><name>HTTP_REQ_BODY</name><scope>local</scope></parameter><parameter><color>#D4FFAF</color><description /><value>hello: world
# example of a comment</value><type>text</type><name>HTTP_REQ_HEADERS</name><scope>local</scope></parameter><parameter><color>#D4FFAF</color><description /><value>POST</value><type>str</type><name>HTTP_REQ_METHOD</name><scope>local</scope></parameter><parameter><color>#D4FFAF</color><description /><value>/session/login</value><type>text</type><name>HTTP_REQ_URI</name><scope>local</scope></parameter><parameter><color>#FCABBD</color><description /><value /><type>text</type><name>HTTP_RSP_BODY</name><scope>local</scope></parameter><parameter><color>#FCABBD</color><description /><value>200</value><type>str</type><name>HTTP_RSP_CODE</name><scope>local</scope></parameter><parameter><color>#FCABBD</color><description /><value>set-cookie: session_id=.*;expires=.*
server: .*</value><type>text</type><name>HTTP_RSP_HEADERS</name><scope>local</scope></parameter><parameter><color>#FCABBD</color><description /><value>OK</value><type>str</type><name>HTTP_RSP_PHRASE</name><scope>local</scope></parameter><parameter><color>#FCABBD</color><description /><value>HTTP/1.[1|0]</value><type>str</type><name>HTTP_RSP_VERSION</name><scope>local</scope></parameter><parameter><color>#FDFFBD</color><description /><value>1:Common:SAMPLE_NODE:</value><type>global</type><name>SERVERS</name><scope>local</scope></parameter><parameter><color>#C1EEFF</color><description /><value>REST response received</value><type>text</type><name>STEP_EXPECTED</name><scope>local</scope></parameter><parameter><color>#C1EEFF</color><description /><value>Send REST request</value><type>text</type><name>STEP_SUMMARY</name><scope>local</scope></parameter><parameter><color>#C1EEFF</color><description /><value>Send REST request and wait response</value><type>text</type><name>TEST_PURPOSE</name><scope>local</scope></parameter><parameter><color /><description /><value>10.0</value><type>float</type><name>TIMEOUT</name><scope>local</scope></parameter><parameter><color /><description /><value>20.0</value><type>float</type><name>TIMEOUT_CONNECT</name><scope>local</scope></parameter><parameter><color /><description /><value>True</value><type>bool</type><name>VERBOSE</name><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class SEND_REST_01(TestCase):
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
		self.LIB_JSON = None
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
				
			self.LIB_JSON = SutLibraries.Codecs.JSON(parent=self, name=None, debug=input('DEBUG'), ignoreErrors=False, shared=False)
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
			if ":" not in hv: self.abort("request headers malformed (%s)" % hv)
			k, v = hv.split(":", 1)
			rspHeaders[TestOperators.RegEx(needle=k.strip())] = TestOperators.RegEx(needle=v.strip())

		rest_rsp= self.ADP_HTTP.hasReceivedHttpResponse(httpCode=input('HTTP_RSP_CODE'), httpPhrase=input('HTTP_RSP_PHRASE'), 
																																			httpVersion=TestOperators.RegEx(needle=input('HTTP_RSP_VERSION')), timeout=input('TIMEOUT'), 
																																			httpHeaders=rspHeaders, httpBody=None)
		if rest_rsp is None: self.abort("expected rest response not received")

		self.ADP_HTTP.disconnect()

		self.msg_decodage.append( "Checks of the response:<br />" )
		
		# capture http headers
		hdrs_rsp = rest_rsp.get("HTTP", "headers").getItems()
		for (k1, v1) in hdrs_rsp:
			for hv2 in input('HTTP_RSP_HEADERS').splitlines():
				k2, v2 = hv2.split(":", 1)
				Cache().capture(data="%s:%s" % (k1.strip(), v1.strip()), regexp="%s:%s" % (k2.strip(), v2.strip()) )

		# search json content type in response
		hdrs_rsp = rest_rsp.get("HTTP", "headers").getItems()
		json_hdr = False
		for (k1, v1) in hdrs_rsp:
			if k1.lower() == "content-type":
				if "application/json" in v1.lower():
					json_hdr = True
					break
		if not json_hdr:
			self.msg_decodage.append("Searching application/json in response: KO")
			self.abort("http response received but without json in body")
		else:
			self.msg_decodage.append("Searching application/json in response: OK")

		# checking if the json provided is valid
		body_rsp = rest_rsp.get("HTTP", "body")
		if body_rsp is None:  self.abort("the body in the http response is empty")
		   
		body_json = self.LIB_JSON.decode(json_str=body_rsp)
		if body_json is None:
			self.msg_decodage.append("Decode json from response: KO")
			self.abort("unable to decode json from response")
		else:
			self.msg_decodage.append("Decode json from response: OK")
			
		# vérification du format du paramètre body
		n = 1
		json_valid= True
		for line in input('HTTP_RSP_BODY').splitlines():
			if line.startswith("#"): continue 
			jsonpath_expected = re.split(r'\t+', line)
			if len(jsonpath_expected) != 2:
				self.abort("bad expected body provided n°%s value=%s, expected <jsonpath>\\t<regexp>" % (n,line) )
	
			jpath, jvalue = jsonpath_expected
			
			# full string
			jsons_values = self.LIB_JSON.getValues(jpath=jpath, json_obj=body_json)
			if not len(jsons_values):
				self.msg_decodage.append( "Searching '%s' with the value '%s' : KO" % (jpath, jvalue) )
				json_valid = False
			else:
				json_values_valid = True
	
				# search capture regexp
				cap = re.findall("\(\?P\<.*\>.*\)", jvalue)
				param_input = re.findall("\[\!FROM\:INPUT\:.*\:\]", jvalue)
				param_cache = re.findall("\[\!FROM\:CACHE\:.*\:\]", jvalue)
	
				if cap :
					cache_key = jvalue.split("(?P<")[1].split(">.*)")[0]
					if len(jsons_values) == 1:
						Cache().capture(data="%s" % jsons_values[0], regexp=jvalue)
					else:
						Cache().set(name=cache_key, data=jsons_values, flag=False)
					self.msg_decodage.append( "Searching and capture value of '%s' : OK" % (jpath) )
					
				else:
					if param_input :
						input_key = jvalue.split("[!FROM:INPUT:")[1].split(":]")[0]
						jvalue = input(name=input_key)
	
					if param_cache :
						cache_key = jvalue.split("[!FROM:CACHE:")[1].split(":]")[0]
						jvalue = Cache().get(name=cache_key)
						if jvalue is None: self.abort("the key %s does not exists in the cache" % cache_key)
	
					for jv in jsons_values:
						jv = str(jv)
						reg = TestOperators.RegEx(needle=jvalue)
						if not reg.seekIn(haystack=jv):
							self.msg_decodage.append( "Searching '%s' with the value '%s' : KO" % (jpath, jvalue) )
							json_values_valid = False
							self.msg_decodage.append( " > received value: %s" % jv.encode("utf8") )
	
					if json_values_valid:
						self.msg_decodage.append( "Searching '%s' with the value '%s' : OK" % (jpath, jvalue) )
					else:
						json_valid = False
	
			n += 1
		
		if json_valid:
			self.step1.setPassed(actual="The response is OK. %s" % "<br />".join(self.msg_decodage) )
		else:
			self.step1.setFailed(actual="The response is KO. %s" %  "<br />".join(self.msg_decodage))

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
	SEND_REST_01(suffix=None).execute(svr=svr)]]></testexecution>
<testdevelopment>1482506736.49494</testdevelopment>
</file>