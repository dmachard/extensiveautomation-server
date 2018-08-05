<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>28/12/2013 19:03:16</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class SESSIONID_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):

		self.ADP_SESSSIONID = SutLibraries.Identifiers.SessionID(parent=self, debug=False)

	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		sessionid = self.ADP_SESSSIONID.generate()
		self.info( sessionid )

class UUID_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):

		self.ADP_UUIDS = SutLibraries.Identifiers.UUIDS(parent=self, debug=False)

	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		sessionid = self.ADP_UUIDS.generate()
		self.info( sessionid )]]></testdefinition>
<testexecution><![CDATA[
SESSIONID_01(suffix=None).execute()
UUID_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1388253796.56</testdevelopment>
</file>