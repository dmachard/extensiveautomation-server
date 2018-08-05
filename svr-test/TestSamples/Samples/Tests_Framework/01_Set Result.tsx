<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value /><key>author</key></description><description><value>30/04/2012</value><key>creation date</key></description><description><value /><key>summary</key></description><description><value /><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters><inputs-parameters /></properties>
<testdefinition><![CDATA[

class PASS(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.info( 'Result set to PASSED' )
		self.step1.start()
		self.step1.setPassed(actual="pass")

class FAIL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as fail", summary="set as fail", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.info( 'Result set to FAILED' )
		self.step1.start()
		self.step1.setFailed(actual="fail")
				
class UNDEFINED(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.info( 'Result set to UNDEFINED' )
				]]></testdefinition>
<testexecution><![CDATA[
PASS().execute()
FAIL().execute()
UNDEFINED().execute()]]></testexecution>
<testdevelopment>1386106050.63</testdevelopment>
</file>