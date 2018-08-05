<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>True</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value /><key>author</key></description><description><value>03/03/2012</value><key>creation date</key></description><description><value /><key>summary</key></description><description><value /><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters /></properties>
<testdefinition><![CDATA[

class TESTCASE_01(TestCase):
	def description(self):
		self.setPurpose(purpose=description('summary'))
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(
																				expected="result expected", 
																				description="step description", 
																				summary="step sample", 
																				enabled=True
																			)
	def prepare(self):
		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106162.95</testdevelopment>
</file>