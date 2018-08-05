<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>14/05/2014 08:48:21</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.LIB_DUMMY = SutLibraries.Extra.Dummy.Library(parent=self, debug=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.LIB_DUMMY.helloWorld(msg="hello world")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1400050101.33</testdevelopment>
</file>