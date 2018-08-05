<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>20/01/2013</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>dataset</type><name>DATASET_LOCAL</name><value>remote-tests(Common):/Samples/Tests_Data/1_Dataset.tdx</value><scope>local</scope></parameter><parameter><description /><type>dataset</type><name>DATASET_REMOTE</name><value>remote-tests(Common):/Samples/Tests_Data/1_Dataset.tdx</value><scope>local</scope></parameter><parameter><description /><type>dataset</type><name>DATASET_UNDEF</name><value>remote-tests(Common):/Sandbox/Noname1.tdx</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>PARAM</name><value /><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_DATASET_REMOTE01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		for d in input('DATASET_REMOTE').splitlines():
			self.info( d ) 
			
		self.step1.setPassed(actual="success")

class TESTCASE_DATASET_UNDEF01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		for d in input('DATASET_UNDEF').splitlines():
			self.info( d ) 
			
		self.step1.setPassed(actual="success")

class TESTCASE_DATASET_LOCAL01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)						
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		for d in input('DATASET_LOCAL').splitlines():
			self.info( d ) 
		
		self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_DATASET_REMOTE01(suffix=None).execute()
TESTCASE_DATASET_UNDEF01(suffix=None).execute()
for d in get('DATASET_UNDEF').splitlines():
	TESTCASE_DATASET_LOCAL01(suffix=None).execute()
]]></testexecution>
<testdevelopment>1386106130.71</testdevelopment>
</file>