<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>20/10/2014 20:58:56</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class ERR_TMR_001(TestCase):

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
		
		adp =  SutAdapter.Adapter(parent=self, name='test', realname=None, debug=False)
		timer = SutAdapter.Timer(parent=self, duration=12, name='test', callback=None, logEvent=True)

class ERR_TMR_002(TestCase):

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
		
		adp =  SutAdapter.Adapter(parent=self, name='test', realname=None, debug=False)
		timer = SutAdapter.Timer(parent=adp, duration="a", name='test', callback=None, logEvent=True)]]></testdefinition>
<testexecution><![CDATA[
ERR_TMR_001(suffix=None).execute()
ERR_TMR_002(suffix=None).execute()]]></testexecution>
<testdevelopment>1413831536.94</testdevelopment>
</file>