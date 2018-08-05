<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>14/05/2014 08:42:04</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
class TESTCASE_02(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()
TESTCASE_02(suffix="test").execute()]]></testexecution>
<testdevelopment>1400049724.79</testdevelopment>
</file>