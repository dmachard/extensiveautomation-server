<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value /><key>author</key></description><description><value /><key>creation date</key></description><description><value /><key>summary</key></description><description><value /><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>int</type><name>TIMER</name><value>1</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMER_FLOAT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class INFO(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		self.info( 'simple message' )
		self.info( 'message in bold', bold = True )
		self.info( 'message in italic', bold = False, italic=True )
		self.info( 'test\r\ntesté2', multiline=True )
		self.info( '<html>test</html>', raw=True )
		self.step1.setPassed(actual="pass")

class WARNING(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		self.warning( 'simple message' )
		self.warning( 'message in bold', bold = True )
		self.step1.setPassed(actual="pass")

class ERROR(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		self.error( 'simple message' )
		self.error( 'message in bold', bold = True )
		self.step1.setPassed(actual="pass")

class WAIT(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		self.info( 'wait during 1 second' )
		self.wait( input('TIMER') ) # in seconde
		self.step1.setPassed(actual="pass")

class WAIT_FLOAT(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		self.info( 'wait during 1 second' )
		
		Timer(self).wait( input('TIMER_FLOAT')  ) # in second
		
		self.step1.setPassed(actual="pass")
				
class WAIT_STR_VAL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as undef", summary="set as undef", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		
		self.info( 'wait during 2 seconds' )
		Timer(self).wait( "2" ) # in second
		
		self.step1.setPassed(actual="pass")


class WAIT_UNTIL(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="wait until", summary="wait until", enabled=True)	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass	
	def definition(self):
		self.step1.start()
		Timer(self).waitUntil(dt='2100-01-01 00:00:00', fmt='%Y-%m-%d %H:%M:%S', delta=0)
		self.step1.setPassed(actual="pass")
]]></testdefinition>
<testexecution><![CDATA[
INFO().execute()
WARNING().execute()
#ERROR().execute()
WAIT().execute()
WAIT_FLOAT().execute()
WAIT_STR_VAL().execute()
#WAIT_UNTIL().execute()]]></testexecution>
<testdevelopment>1386106056.13</testdevelopment>
</file>