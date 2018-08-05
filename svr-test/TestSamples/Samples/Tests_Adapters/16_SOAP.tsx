<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>denis</value><key>author</key></description><description><value>02/07/2014 16:01:57</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>self-ip</type><name>BIND_IP</name><value>0.0.0.0 (all)</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>5.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT_SOCKET</name><value>agent-win-sock01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class SOAP_WEATHER_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
			
		self.ADP_SOAP = SutAdapters.GlobalWeather.GlobalWeatherSoap(parent=self, name=None, debug=input('DEBUG'), shared=False, 
				agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'), sslSupport=False, bindIp='', bindPort=0, 
				destinationIp='www.webservicex.com', destinationPort=80, xmlns0='http://www.webserviceX.NET',
				xmlns1='http://schemas.xmlsoap.org/soap/envelope/', 
				xmlns2='http://www.w3.org/2003/05/soap-envelope', 
				xmlns3='http://www.w3.org/2001/XMLSchema-instance', 
				xmlns4='http://www.w3.org/2001/XMLSchema', destUri='/globalweather.asmx')
		self.LIB_XML = SutLibraries.Codecs.XML(parent=self, debug=input('DEBUG'), coding='UTF-8', name=None)
	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
	
	## >> called on test begin
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
	
			self.ADP_SOAP.connect()
			if self.ADP_SOAP.isConnected(timeout=1.0) is None:
				self.abort("unable to connect")
				
			self.ADP_SOAP.GetWeather(CityName="Caen", CountryName="FR", httpHeaders={})
			rsp= self.ADP_SOAP.hasReceivedSoapResponse(httpCode='200', httpPhrase='OK', timeout=input('TIMEOUT'))
			self.warning(rsp.getRaw())
			if rsp is None:
				self.error( 'no valid response received' )
			else:
				xml_rsp = rsp.get('SOAP').getRaw() 
				# prepare namespaces
				ns= {
									'n':'http://schemas.xmlsoap.org/soap/envelope/', 
									'w': 'http://www.webserviceX.NET'
							}
				self.LIB_XML.read(content=xml_rsp, ns=ns)
				ret = self.LIB_XML.getElements(xpath="n:Body/w:GetWeatherResponse/w:GetWeatherResult")
				if not len(ret):
					self.error("no GetWeatherResult found!")
				else:
					self.warning("GetWeatherResult received")
					
					text = self.LIB_XML.getText(xpath="n:Body/w:GetWeatherResponse/w:GetWeatherResult")
					self.warning(text, raw=True)
					
			self.ADP_SOAP.disconnect()
			if self.ADP_SOAP.isDisconnected(timeout=1.0) is None:
				self.abort("unable to disconnect")
class SOAP_WEATHER_02(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
			
		self.ADP_SOAP = SutAdapters.GlobalWeather.GlobalWeatherSoap(parent=self, name=None, debug=input('DEBUG'), shared=False, 
				agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'), sslSupport=False, bindIp='', bindPort=0, 
				destinationIp='www.webservicex.com', destinationPort=80, xmlns0='http://www.webserviceX.NET',
				xmlns1='http://schemas.xmlsoap.org/soap/envelope/', 
				xmlns2='http://www.w3.org/2003/05/soap-envelope', 
				xmlns3='http://www.w3.org/2001/XMLSchema-instance', 
				xmlns4='http://www.w3.org/2001/XMLSchema', destUri='/globalweather.asmx')
		self.LIB_XML = SutLibraries.Codecs.XML(parent=self, debug=input('DEBUG'), coding='UTF-8', name=None)
	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
	
	## >> called on test begin
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
	
			self.ADP_SOAP.connect()
			if self.ADP_SOAP.isConnected(timeout=1.0) is None:
				self.abort("unable to connect")
				
			self.ADP_SOAP.GetWeather(CityName="Caen", CountryName="FR", httpHeaders={})
			rsp= self.ADP_SOAP.hasReceivedSoapResponse(httpCode='200', httpPhrase='OK', timeout=input('TIMEOUT'))
			if rsp is None:
				self.error( 'no valid response received' )
			else:
				soap = rsp.get('SOAP')
				geo_rsp = soap.get('Envelope')
				geo_rsp = geo_rsp.get('Body')
				geo_rsp = geo_rsp.get('GetWeatherResponse')
				geo_rsp = geo_rsp.get('GetWeatherResult')
				
				self.warning( geo_rsp, raw=True)
				
			self.ADP_SOAP.disconnect()
			if self.ADP_SOAP.isDisconnected(timeout=1.0) is None:
				self.abort("unable to disconnect")
class SOAP_WEATHER_INVALID_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
			
		self.ADP_SOAP = SutAdapters.GlobalWeather.GlobalWeatherSoap(parent=self, name=None, debug=input('DEBUG'), shared=False, 
				agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT'), sslSupport=False, bindIp='', bindPort=0, 
				destinationIp='www.webservicex.com', destinationPort=80, xmlns0='http://www.webserviceX.NET',
				xmlns1='http://schemas.xmlsoap.org/soap/envelope/', 
				xmlns2='http://www.w3.org/2003/05/soap-envelope', 
				xmlns3='http://www.w3.org/2001/XMLSchema-instance', 
				xmlns4='http://www.w3.org/2001/XMLSchema', destUri='/globalweather.asmx')
		self.LIB_XML = SutLibraries.Codecs.XML(parent=self, debug=input('DEBUG'), coding='UTF-8', name=None)
	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
	
	## >> called on test begin
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
	
			self.ADP_SOAP.connect()
			if self.ADP_SOAP.isConnected(timeout=1.0) is None:
				self.abort("unable to connect")
				
			self.ADP_SOAP.GetWeather(CityName="Caen", CountryName=None, httpHeaders={})
			rsp= self.ADP_SOAP.hasReceivedSoapResponse(httpCode='500', httpPhrase='Internal Server Error', timeout=input('TIMEOUT'))
			if rsp is None:
				self.error( 'no valid response received' )

			self.ADP_SOAP.disconnect()
			if self.ADP_SOAP.isDisconnected(timeout=1.0) is None:
				self.abort("unable to disconnect")]]></testdefinition>
<testexecution><![CDATA[
SOAP_WEATHER_01(suffix=None).execute()
SOAP_WEATHER_02(suffix=None).execute()
SOAP_WEATHER_INVALID_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1404309717.31</testdevelopment>
</file>