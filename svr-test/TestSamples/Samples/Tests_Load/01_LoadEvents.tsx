<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/04/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>NB_EVENTS</name><value>500</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		
		for i in xrange(input('NB_EVENTS')):
			self.info('test')
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[# Resut
#		          nb/min/avg/max
# TESTSUITE 	1/0.947/0.947/0.947
# TESTCASE 	  500/0.879/0.879/0.879

#9s to load testresult in 32 bits
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105821.87</testdevelopment>
</file>