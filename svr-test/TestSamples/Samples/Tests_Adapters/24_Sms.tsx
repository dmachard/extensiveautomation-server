<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>06/09/2015 21:34:33</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>GW_IP</name><value>192.168.1.28</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>15</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>smsgateway</type><name>AGENT</name><value>agent-win-sms01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_SMS_AGENT_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		pass

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

	## >> called on test begin
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
			
			self.ADP_SMS = SutAdapters.SMS.Gateway(parent=self,  debug=input('DEBUG'), agent=agent('AGENT'), 
																																				agentSupport=True, gwIp=input('GW_IP'), gwPort=9090)
																																				
			actId = self.ADP_SMS.sendSms(phone="0607153891", msg="hello é :)")
			if self.ADP_SMS.isSmsSent(timeout=input('TIMEOUT'), actionId=actId) is None:
				self.abort()
			
			texto = self.ADP_SMS.hasReceivedSms(timeout=input('TIMEOUT'))
			if texto is None:
				self.abort("no message received")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_SMS_AGENT_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1441568073.660126</testdevelopment>
</file>