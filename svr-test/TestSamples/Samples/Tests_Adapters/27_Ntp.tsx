<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>13/03/2016 18:13:49</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><value>False</value><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>123</value><description /><name>NTP_SVR_PORT</name><type>int</type><scope>local</scope></parameter><parameter><value>0.fr.pool.ntp.org</value><description /><name>NTP_SVR_SERVER</name><type>str</type><scope>local</scope></parameter><parameter><value>3</value><description /><name>NTP_SVR_VERSION</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>5.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter><parameter><color /><description /><value>True</value><name>VERBOSE</name><type>bool</type><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent-dummy01</value><description /><name>AGENT</name><type>dummy</type></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><value>1.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)

	def prepare(self):
		# adapters and libraries
		self.ADP_NTP = SutAdapters.NTP.Client(parent=self, name=None, debug=False, shared=False, agentSupport=False, agent=None,
																														bindIp = '', bindPort=0)
	def cleanup(self, aborted):
		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			self.ADP_NTP.startListening()
			if self.ADP_NTP.isListening(timeout=input('TIMEOUT')) is None:
				self.abort("unable to listen")
			
			self.ADP_NTP.queryServer(serverIp=input('NTP_SVR_SERVER'), serverPort=input('NTP_SVR_PORT'), ntpVersion=input('NTP_SVR_VERSION'))
			if self.ADP_NTP.hasReceivedResponse(timeout=input('TIMEOUT')) is None:
				self.error("bad response")
			
			self.ADP_NTP.stopListening()
			if self.ADP_NTP.isStopped(timeout=input('TIMEOUT')) is None:
				self.abort("unable to stop")
			
			
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1457889229.955113</testdevelopment>
</file>