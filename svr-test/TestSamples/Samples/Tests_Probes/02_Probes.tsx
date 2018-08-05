<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>True</active><args>{'files': ['/var/log/messages']}</args><name>probe-file01</name><type>file</type></probe><probe><active>True</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>probe-network01</name><type>network</type></probe><probe><active>True</active><args>{'files': ['/var/log/messages']}</args><name>probe-textual01</name><type>textual</type></probe><probe><active>False</active><args /><name>textual01</name><type>textual</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>25/02/2012</value><key>creation date</key></description><description><value>Just a basic sample.&#233;</value><key>summary</key></description><description><value>&#233;&#233;&#233;
m
kl</value><key>prerequisites</key></description><description><value><comments><comment><author>tester</author><post>MQ==</post><datetime>1362938028.91</datetime></comment></comments></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters /></properties>
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
			Time(self).wait(timeout=2)
			self.step1.setPassed(actual="success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106162.19</testdevelopment>
</file>