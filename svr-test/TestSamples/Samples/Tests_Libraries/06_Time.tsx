<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>23/08/2013</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TIMESTAMP_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)				
	def prepare(self):
		self.timetools = SutLibraries.Time.Timestamp(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		timestamp = self.timetools.generate()
		self.info( timestamp )
		self.step1.setPassed(actual="pass")

class TIMESTAMP_DELTA_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.timetools = SutLibraries.Time.Timestamp(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		timestamp = self.timetools.generate(deltaTime=100)
		self.info( timestamp )
		self.step1.setPassed(actual="pass")

class TIMESTAMP_FROM_DATE_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.timetools = SutLibraries.Time.Timestamp(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		timestamp = self.timetools.generate(fromDate="20/12/2014 10:00:00", dateFormat="%d/%m/%Y %H:%M:%S")
		self.info( timestamp )
		self.step1.setPassed(actual="pass")
		
class TIMESTAMP_TO_HUMAN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)			
	def prepare(self):
		self.timetools = SutLibraries.Time.Timestamp(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		timestamp = self.timetools.generate()
		self.info( timestamp )
		
		human = self.timetools.toHuman(timestamp=timestamp)
		self.info( human )
			
		self.step1.setPassed(actual="pass")]]></testdefinition>
<testexecution><![CDATA[
TIMESTAMP_01(suffix=None).execute()
TIMESTAMP_DELTA_01(suffix=None).execute()
TIMESTAMP_FROM_DATE_01(suffix=None).execute()

TIMESTAMP_TO_HUMAN_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106017.69</testdevelopment>
</file>