<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><key>author</key><value>admin</value></description><description><key>creation date</key><value>03/02/2018 07:10:59</value></description><description><key>summary</key><value>Just a basic sample.</value></description><description><key>prerequisites</key><value>None.</value></description><description><key>comments</key><value><comments /></value></description><description><key>libraries</key><value>myplugins</value></description><description><key>adapters</key><value>myplugins</value></description><description><key>state</key><value>Writing</value></description><description><key>requirement</key><value>REQ_01</value></description></descriptions><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><inputs-parameters><parameter><type>bool</type><name>DEBUG</name><description /><value>False</value><color /><scope>local</scope></parameter><parameter><type>float</type><name>TIMEOUT</name><description /><value>10.0</value><color /><scope>local</scope></parameter><parameter><type>bool</type><name>VERBOSE</name><description /><value>True</value><color /><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><type>float</type><name>TIMEOUT</name><description /><value>60.0</value><color /><scope>local</scope></parameter></outputs-parameters><agents><agent><name>AGENT</name><description /><value>agent-dummy01</value><type>dummy</type></agent></agents></properties>
<testdefinition><![CDATA[
class DIG_01(TestCase):
	def description(self):
		self.setPurpose(purpose=description('summary'))
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		self.DIG = SutAdapters.DNS.Dig(parent=self, name=None, debug=input('DEBUG'), shared=False, agentSupport=False, agent=None)

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			self.DIG.execute(cmd="www.extensivetesting.org")
			event = self.DIG.hasReceivedEvent(expected=TestOperators.Contains(needle="ANSWER SECTION"), timeout=input('TIMEOUT'))
			self.info( event.get("DIG", "output") )
			
			self.step1.setPassed(actual="success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
DIG_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517638259.1205974</testdevelopment>
</file>