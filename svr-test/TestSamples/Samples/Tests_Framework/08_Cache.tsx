<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>02/03/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>custom</type><name>REGEXP</name><value>.*session_id=[!CAPTURE:SESSIONID:.*?:];.*</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[

class TESTCASE_CACHE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		if self.step1.isEnabled():
			self.step1.start()
			
			data = [2, 3, {"de": 1}]
			key = "my key"
			Cache().set(name=key, data=data)
			
			cache = Cache().get(name=key)
			self.info( "data from cache: %s" % cache)
	
			deleted = Cache().delete(name=key)
			if not deleted:
				self.error( "unable to delete data from cache" )
				
			cache = Cache().get(name=key)
			self.info( "data from cache: %s" % cache)
	
			Cache().reset()
			
			self.step1.setPassed(actual="success")
class TESTCASE_CACHE_CAPTURE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		if self.step1.isEnabled():
			self.step1.start()
			
			my_data="March, 25 2017 07:38:58 AM"
			Cache().capture(data=my_data, regexp=".* (?P<TIME>\d{2}:\d{2}:\d{2}) .*")
			Trace(self).info( txt=Cache().get(name="TIME") )
			
			self.step1.setPassed(actual="success")
class TESTCASE_CACHE_CAPTURE_CUSTOM(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		if self.step1.isEnabled():
			self.step1.start()
		
			h  = "Set-Cookie: session_id=Mjc5YTg1NjJjNDA3NDU5ZDliNDAwZWJiYjQxMmRjMDI5M;expires=Tue, 02-May-2017 19:43:26 GMT; path=/"
			Cache().capture(data=h, regexp=input('REGEXP'))
			
			session_id =Cache().get(name="SESSIONID")
			self.warning( "session_id: %s" % session_id)
			
			
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_CACHE(suffix=None).execute()
TESTCASE_CACHE_CAPTURE(suffix=None).execute()
TESTCASE_CACHE_CAPTURE_CUSTOM(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106104.04</testdevelopment>
</file>