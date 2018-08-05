<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>test&#233;</value><key>author</key></description><description><value /><key>creation date</key></description><description><value>special character are supported: &#232;#~&amp;|`
test with return carrier</value><key>summary</key></description><description><value>special character are supported: &#232;#~&amp;|`
test with return carrier</value><key>prerequisites</key></description><description><value><comments><comment><author>admin</author><post>c3BlY2lhbCBjaGFyYWN0ZXIgYXJlIHN1cHBvcnRlZDogw6gjfiZ8YAp0ZXN0IHdpdGggcmV0dXJuIGNhcnJpZXI=</post><datetime>1379260165.49</datetime></comment></comments></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description>&#233;valuation</description><type>str</type><name>PARAM0</name><value>&#233;#?!:;(-|_&#232;~</value><scope>local</scope></parameter><parameter><description /><type>list</type><name>PARAM1</name><value>&#224;,&#233;</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>PARAM2</name><value>aaa</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
#
# special characters: é*µà@°1é&
#
class SPECIAL_CHARACTERS_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected é", description="step description é", summary="step sample é", enabled=True)		
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		a = "é*µà@°1é&"
		self.info( a )
		
		self.step1.setPassed(actual="success é")

class SPECIAL_CHARACTERS_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		a = input('PARAM0')
		self.info( a )
		
		self.step1.setPassed(actual="success")

class SPECIAL_CHARACTERS_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		a = input('PARAM1')
		for v in a:
			self.info( v )
		self.step1.setPassed(actual="success")
]]></testdefinition>
<testexecution><![CDATA[# special characters: é*µà@°1é&
SPECIAL_CHARACTERS_01().execute()
SPECIAL_CHARACTERS_02().execute()
SPECIAL_CHARACTERS_03().execute()]]></testexecution>
<testdevelopment>1386106073.91</testdevelopment>
</file>