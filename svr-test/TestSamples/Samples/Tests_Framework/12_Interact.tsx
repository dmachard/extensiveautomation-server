<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>22/01/2013</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class INTERACT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)							
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		rsp  = self.interact(ask="Name ?")
		self.info( str(rsp) )
		
		rsp  = self.interact(ask="Last name ?")
		self.info( str(rsp) )

		self.step1.setPassed(actual="success")
		
class INTERACT_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)							
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		rsp  = self.interact(ask="Name ?", timeout=5)
		self.info( str(rsp) )
		
		self.step1.setPassed(actual="success")
class INTERACT_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)							
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		rsp = self.interact(ask="hello", timeout=5.0, default="world é")
		self.warning("rsp: %s" % rsp)
		
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
INTERACT_01(suffix=None).execute()
INTERACT_02(suffix=None).execute()
INTERACT_03(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106129.89</testdevelopment>
</file>