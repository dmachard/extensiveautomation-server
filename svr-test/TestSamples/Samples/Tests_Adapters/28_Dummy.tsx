<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>14/05/2014 08:48:48</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>dummy</type><name>AGENT1</name><value>agent-win-dummy01</value></agent><agent><description /><type>dummy</type><name>AGENT2</name><value>agent-win-dummy01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_ADAPTER_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.ADP_DUMMY = SutAdapters.Extra.Dummy.Adapter(parent=self, debug=False, shared=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_DUMMY.helloWorld(msg="hello world")
		self.step1.setPassed(actual="success")
		
class TESTCASE_AGENT_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.AGT1_DUMMY = SutAdapters.Extra.Dummy.Agent(parent=self, agent=agent('AGENT1'), debug=input('DEBUG'), shared=False)
		self.AGT2_DUMMY = SutAdapters.Extra.Dummy.Agent(parent=self, agent=agent('AGENT2'), debug=input('DEBUG'), shared=False)
	def definition(self):
		# starting initial step
		self.step1.start()

		self.info( 'Send init command to agent: %s' % agent('AGENT1') )
		self.AGT1_DUMMY.sendInitToAgent(data='init')
		self.AGT2_DUMMY.sendInitToAgent(data='init')
		self.wait(2)
		
		self.info( 'Send notify to agent: %s' % agent('AGENT1') )
		self.AGT1_DUMMY.sendNotifyToAgent(data={'cmd':'dir'} )
		self.wait(2)
		
		self.info( 'Send reset command to agent: %s' % agent('AGENT1') )
		self.AGT1_DUMMY.sendResetToAgent(data='reset')
		self.wait(2)
		
		self.step1.setPassed(actual="success")

	def cleanup(self, aborted):
		pass]]></testdefinition>
<testexecution><![CDATA[
# testcase without agent
if not input('SUPPORT_AGENT'):
	TESTCASE_ADAPTER_01(suffix=None).execute()

# testcase only in agent mode
if input('SUPPORT_AGENT'):
	TESTCASE_AGENT_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1400050128.35</testdevelopment>
</file>