<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><key>author</key><value>admin</value></description><description><key>creation date</key><value>18/06/2018 17:42:07</value></description><description><key>summary</key><value>Just a basic sample.</value></description><description><key>prerequisites</key><value>None.</value></description><description><key>comments</key><value><comments /></value></description><description><key>libraries</key><value>myplugins</value></description><description><key>adapters</key><value>myplugins</value></description><description><key>state</key><value>Writing</value></description><description><key>requirement</key><value>REQ_01</value></description></descriptions><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><inputs-parameters><parameter><name>AGENT_CURL</name><type>json</type><description /><value>{"name": "example", "type": "curl"}</value><scope>local</scope><color /></parameter><parameter><name>AGENT_MODE</name><type>bool</type><description /><value>False</value><scope>local</scope><color /></parameter><parameter><type>bool</type><name>DEBUG</name><description /><value>False</value><color /><scope>local</scope></parameter><parameter><name>HTTP_REQ_BODY</name><type>none</type><description /><value /><scope>local</scope><color>#D4FFAF</color></parameter><parameter><name>HTTP_REQ_HEADERS</name><type>none</type><description>Host: hostname</description><value /><scope>local</scope><color>#D4FFAF</color></parameter><parameter><name>HTTP_REQ_HOST</name><type>text</type><description>https://hostname:443</description><value>http://10.0.0.1</value><scope>local</scope><color>#D4FFAF</color></parameter><parameter><name>HTTP_REQ_HTTPPROXY_HOST</name><type>none</type><description>http://proxy:8080</description><value /><scope>local</scope><color>#D4FFAF</color></parameter><parameter><name>HTTP_REQ_METHOD</name><type>none</type><description>GET, POST, etc.</description><value /><scope>local</scope><color>#D4FFAF</color></parameter><parameter><name>HTTP_REQ_MORE</name><type>none</type><description /><value /><color>#D4FFAF</color><scope>local</scope></parameter><parameter><name>HTTP_RSP_BODY_JSON</name><type>none</type><description>error &lt;tab&gt; .*</description><value /><scope>local</scope><color>#FCABBD</color></parameter><parameter><name>HTTP_RSP_BODY_RAW</name><type>none</type><description>&lt;title&gt;Extensive.*&lt;/title&gt;</description><value /><scope>local</scope><color>#FCABBD</color></parameter><parameter><name>HTTP_RSP_BODY_XML</name><type>none</type><description>//s:Body &lt;tab&gt; .*</description><value /><scope>local</scope><color>#FCABBD</color></parameter><parameter><name>HTTP_RSP_BODY_XML_NS</name><type>none</type><description>s	http://www.w3.org/2003/05/soap-envelope
r	http://www.holidaywebservice.com/HolidayService_v2/</description><value /><scope>local</scope><color>#FCABBD</color></parameter><parameter><description>200</description><name>HTTP_RSP_CODE</name><color>#FCABBD</color><value /><scope>local</scope><type>none</type></parameter><parameter><color>#FCABBD</color><description>[S|s]erver:.*</description><value /><type>none</type><name>HTTP_RSP_HEADERS</name><scope>local</scope></parameter><parameter><description>OK</description><name>HTTP_RSP_PHRASE</name><color>#FCABBD</color><value /><scope>local</scope><type>none</type></parameter><parameter><description>HTTP/1.[1|0]</description><name>HTTP_RSP_VERSION</name><color>#FCABBD</color><value /><scope>local</scope><type>none</type></parameter><parameter><description /><name>STEP_EXPECTED</name><color>#C1EEFF</color><value>HTTP response received</value><scope>local</scope><type>text</type></parameter><parameter><description /><name>STEP_SUMMARY</name><color>#C1EEFF</color><value>Send HTTP request</value><scope>local</scope><type>text</type></parameter><parameter><description /><name>TEST_PURPOSE</name><color>#C1EEFF</color><value>Send HTTP request and wait response</value><scope>local</scope><type>text</type></parameter><parameter><name>TIMEOUT</name><type>int</type><description /><value>3</value><scope>local</scope><color /></parameter><parameter><name>TIMEOUT_CONNECT</name><type>int</type><description /><value>3</value><scope>local</scope><color>#FBFBFB</color></parameter><parameter><type>bool</type><name>VERBOSE</name><description /><value>True</value><color /><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><type>float</type><name>TIMEOUT</name><description /><value>60.0</value><color /><scope>local</scope></parameter></outputs-parameters><agents><agent><name>AGENT</name><description /><value>agent.win.curl</value><type>curl</type></agent></agents></properties>
<testdefinition><![CDATA[
class SEND_HTTP(TestCase):
	def description(self, host):
		# testcase description
		self.setPurpose(purpose=input('TEST_PURPOSE'))
		self.setRequirement(requirement=description('requirement'))
	
		# steps description
		self.step1 = self.addStep(expected=input('STEP_EXPECTED'), 
																				description=input('STEP_SUMMARY'), 
																				summary=input('STEP_SUMMARY'), 
																				enabled=True)
	def prepare(self, host):
		self.ADP_CURL = SutAdapters.WEB.Curl(parent=self, name=None, debug=input('DEBUG'), 
																															shared=False, agentSupport=input('AGENT_MODE'),  
																															agent=input('AGENT_CURL'), 
																															logEventSent=input('VERBOSE'), logEventReceived=input('VERBOSE'))

	def definition(self, host):	
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			# import python libraries
			import re
			
			import json
			try:
				from jsonpath_ng.ext import parse
			except ImportError:
				self.error("please to install the jsonpath library")
				self.abort("jsonpath python library is missing")
				
			try:
				import lxml
				from lxml import etree 
			except ImportError:
				self.error("please to install the lxml library")
				self.abort("lxml python library is missing")
			
			step_details = []
			
			# prepare headers and ignore commented headers
			req_headers = None
			if input('HTTP_REQ_HEADERS') is not None:
				req_headers = []
				for req_hdr in input('HTTP_REQ_HEADERS').splitlines():
					if req_hdr.startswith("#"): continue
					if ":" not in req_hdr: self.abort("request headers malformed (%s)" % req_hdr)
					req_headers.append(req_hdr)
				req_headers = "\n".join(req_headers)
				
			# send the request
			body_req = input('HTTP_REQ_BODY')
			for inp in  inputs() :
				if inp["name"] == "HTTP_REQ_BODY":
					if inp["type"] == "json":
						try:
							body_req = json.loads(body_req)
						except:
							body_req = None
						break

			if input('HTTP_REQ_HTTPPROXY_HOST') is not None:
				self.info("using proxy %s"%input('HTTP_REQ_HTTPPROXY_HOST'))

			self.ADP_CURL.sendHttp(host=host, 
																				method=input('HTTP_REQ_METHOD'),
																				headers=req_headers,
																				body=body_req,
																				proxy_host=input('HTTP_REQ_HTTPPROXY_HOST'),
																				timeout_connect=input('TIMEOUT_CONNECT'),
																				timeout_max = input('TIMEOUT') ,
																				more=input('HTTP_REQ_MORE'))
	
			# try to match a generic response
			evt = self.ADP_CURL.hasReceivedHttpResponse(timeout=input('TIMEOUT'))
			if evt is None: self.abort("no http response received")
			# check the http code of the response
			if input('HTTP_RSP_CODE') is not None:
				rsp_code = evt.get("CURL_HTTP_RESPONSE", "code")
				if not TestOperators.RegEx(needle=input('HTTP_RSP_CODE')).seekIn(haystack=rsp_code):
					msg_error = "- checking http code: KO (%s received, %s expected)" % (rsp_code, input('HTTP_RSP_CODE')) 
					self.abort(msg_error)
				step_details.append( "- checking http code: OK" )
				
			# check the http phrase of the response
			if input('HTTP_RSP_PHRASE') is not None:
				rsp_phrase = evt.get("CURL_HTTP_RESPONSE", "phrase")
				if not TestOperators.RegEx(needle=input('HTTP_RSP_PHRASE')).seekIn(haystack=rsp_phrase):
					msg_error = "- checking http phrase: KO (%s expected, %s received)" % (rsp_phrase, input('HTTP_RSP_PHRASE'))
					self.abort( msg_error )
				step_details.append( "- checking http phrase: OK" )
				
			# check the http version
			if input('HTTP_RSP_VERSION') is not None:
				rsp_version = evt.get("CURL_HTTP_RESPONSE", "version")
				if not TestOperators.RegEx(needle=input('HTTP_RSP_VERSION')).seekIn(haystack=rsp_version):
					msg_error = "- checking http version: KO (%s expected, %s received)" % (rsp_phrase, input('HTTP_RSP_VERSION'))
					self.abort( msg_error )
				step_details.append("- checking http version: OK")
				
			# check headers in response
			if input('HTTP_RSP_HEADERS') is not None:
				rsp_headers = evt.get("CURL_HTTP_RESPONSE", "headers")
				for hv in input('HTTP_RSP_HEADERS').splitlines():
					# ignore commented header
					if hv.startswith("#"): continue 
					if ":" not in hv: self.abort("expected headers in response malformed (%s)" % req_hdr)
					hdr_found = False
					for rsp_hdr in rsp_headers.splitlines():	
						# check if the header provided exists on headers of the response
						if TestOperators.RegEx(needle=hv).seekIn(haystack=rsp_hdr):
							hdr_found = True
							step_details.append("- checking http header (%s): OK " % hv)
							# capture header value and save it in the cache
							Cache().capture(data=rsp_hdr, regexp=hv )
						
					if not hdr_found: 
						self.abort( "- checking http header (%s): KO " % hv)
			
			# checking body raw ?
			if input('HTTP_RSP_BODY_RAW') is not None:
				body_regexp = ".*".join(input('HTTP_RSP_BODY_RAW').splitlines())
				if not TestOperators.RegEx(needle=".*%s.*" % body_regexp).seekIn(haystack=evt.get("CURL_HTTP_RESPONSE", "body")):
					msg_error = "- checking http body: KO (%s expected)" % (body_regexp)
					self.abort( msg_error )
					
				# capture header value and save it in the cache
				Cache().capture(data=evt.get("CURL_HTTP_RESPONSE", "body"), regexp=body_regexp )
	
				step_details.append("- checking http body: OK")
				
			# checking body json ?
			if input('HTTP_RSP_BODY_JSON') is not None:
				try:
					body_json = json.loads(evt.get("CURL_HTTP_RESPONSE", "body"))
				except:
					body_json = None
				if body_json is None: self.abort("- checking http body format: KO (json expected)")
				step_details.append( "- checking http body format: OK (valid json)"  )
				
				for line in input('HTTP_RSP_BODY_JSON').splitlines():
					if line.startswith("#"): continue 
	
					if len(re.split(r'\t+', line)) != 2:
						self.abort("bad expected body provided value=%s, expected <jsonpath>\\t<regexp>" % (line) )
						
					jpath, jvalue = re.split(r'\t+', line)
					try:
						json_values =  [match.value for match in parse(jpath).find(body_json)]
					except Exception as e:
						self.error('bad jsonpath (%s) provided ? more details:\n\n %s' % (jpath, str(e)) )
						json_values = []
					if not len(json_values):
						self.abort( "- searching '%s' with the value '%s' : KO" % (jpath, jvalue) )
	
					#  search capture regexp
					capture_detected = re.findall("\(\?P\<.*\>.*\)", jvalue)
					if capture_detected:
						cache_key = jvalue.split("(?P<")[1].split(">.*)")[0]
						if len(json_values) == 1:
							Cache().capture(data="%s" % json_values[0], regexp=jvalue)
						else:
							Cache().set(name=cache_key, data=json_values, flag=False)
						step_details.append( "- searching and capture value of '%s'" % (jpath) )
						
					else:
						values_detected = False
						for jv in json_values:
							if TestOperators.RegEx(needle=jvalue).seekIn(haystack="%s" % jv):
								values_detected = True
								
						if not values_detected:
							self.abort( "- searching '%s' with the value '%s' : KO" % (jpath, jvalue) )
						else:
							step_details.append( "- searching '%s' with the value '%s' : OK" % (jpath, jvalue)  )
						
			# checking body xml ?
			if input('HTTP_RSP_BODY_XML') is not None:
				body_xml  = evt.get("CURL_HTTP_RESPONSE", "body")
				valid = True
				try:
					etree.XML( bytes(body_xml, "utf8") )
				except Exception as e:
					self.error( "invalid xml %s" % e)
					valid = False
				if not valid: self.abort("- checking http body format: KO (xml expected)")
				step_details.append( "- checking http body format: OK (valid xml)"  )
				
				ns = {}
				if input('HTTP_RSP_BODY_XML_NS') is not None:
					for line in input('HTTP_RSP_BODY_XML_NS').splitlines():
						if len(re.split(r'\t+', line)) != 2: 	self.abort("bad namespaces provided value=%s, expected <name>\\t<namespace>" % (line) )
						ns_name, namespace = re.split(r'\t+', line)
						ns[ns_name] = namespace
				
				for line in input('HTTP_RSP_BODY_XML').splitlines():
					if line.startswith("#"): continue 
	
					if len(re.split(r'\t+', line)) != 2:
						self.abort("bad expected body provided value=%s, expected <xpath>\\t<regexp>" % (line) )
					xpath, xvalue = re.split(r'\t+', line)

					# search data with xpath in xml
					xml_values = []
					try:
						rootXML = etree.XML( bytes(body_xml, "utf8") )
						findXML= etree.XPath(xpath, namespaces=ns)
						retXML =  findXML(rootXML)
						
						for el in retXML:
							if isinstance(el, etree._Element ):
								xml_values.append( "%s" % el.text)
							else:
								xml_values.append( "%s" % el )
					except Exception as e:
						self.error('unable to get all xml values: %s' % str(e) )
						xml_values = []
					if not len(xml_values):
						self.abort( "- searching '%s' with the value '%s' : KO" % (xpath, xvalue) )
					
					#  search capture regexp
					capture_detected = re.findall("\(\?P\<.*\>.*\)", xvalue)
					if capture_detected:
						cache_key = xvalue.split("(?P<")[1].split(">.*)")[0]
						if len(xml_values) == 1:
							Cache().capture(data="%s" % xml_values[0], regexp=xvalue)
						else:
							Cache().set(name=cache_key, data=xml_values, flag=False)
						step_details.append( "- searching and capture value of '%s'" % (xpath) )
						
					else:
						values_detected = False
						for jv in xml_values: 
								if TestOperators.RegEx(needle=xvalue).seekIn(haystack="%s" % jv):
									values_detected = True
						if not values_detected:
							self.abort( "- searching '%s' with the value '%s' : KO" % (xpath, xvalue) )
						else:
							step_details.append( "- searching '%s' with the value '%s' : OK" % (xpath, xvalue) )
					
			# log all details
			for msg in step_details:
				self.info(msg)
				
			self.step1.setPassed(actual="success")

	def cleanup(self, aborted, host):
		if aborted:
			self.error("test aborted: %s" % aborted)
			self.step1.setFailed(actual=aborted)
]]></testdefinition>
<testexecution><![CDATA[
hosts = input('HTTP_REQ_HOST')
if hosts is None: AbortTestSuite("no host provided")

if hosts is None: AbortTestSuite(reason="no host provided")
if not isinstance(hosts, list): hosts = [ input('HTTP_REQ_HOST') ]
	
for host in hosts:
	SEND_HTTP(suffix=None).execute(host=host)]]></testexecution>
<testdevelopment>1529336527.5451608</testdevelopment>
</file>