<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2014 22:20:07</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>str</type><name>APP-ONLY AUTHENTICATION</name><value>https://api.twitter.com/oauth2/token</value><scope>local</scope></parameter><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>HOST</name><value>api.twitter.com</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>PORT</name><value>443</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>USE_SSL</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT_SOCKET</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class REST_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.ADP_REST= SutAdapters.REST.Client(parent=self, name=None, bindIp='', bindPort=0, destinationIp=input('HOST'),
																														destinationPort=input('PORT'),
																														debug=input('DEBUG'), logEventSent=True, logEventReceived=True, httpAgent='Extensive Testing',
																														sslSupport=input('USE_SSL'),
																														agentSupport=input('SUPPORT_AGENT'), agent=agent('AGENT_SOCKET'), shared=False)
		self.ADP_REST.connect()
		if self.ADP_REST.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('unable to connect')

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		self.ADP_REST.sendRest(uri=input('APP-ONLY AUTHENTICATION'), host=input('HOST'))
		rsp = self.ADP_REST.hasReceivedRestResponse(timeout=input('TIMEOUT'), httpCode="403", httpPhrase="Forbidden")
		if rsp is None:
			self.abort('no response')
	
		rest_rsp = rsp.get('REST')
		access_token = rest_rsp.get('access_token')]]></testdefinition>
<testexecution><![CDATA[
REST_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1413318007.24</testdevelopment>
</file>