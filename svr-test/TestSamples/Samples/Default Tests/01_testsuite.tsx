<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>22/11/2015 12:11:57</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>dummy</type><name>AGENT</name><value>agent-dummy01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)

	def prepare(self):
		# adapters and libraries
		pass

	def cleanup(self, aborted):
		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1448190717.236711</testdevelopment>
</file>