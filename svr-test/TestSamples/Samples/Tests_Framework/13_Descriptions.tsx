<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>denis</value><key>author</key></description><description><value>29/07/2013</value><key>creation date</key></description><description><value>Just a basic sample.
Just a basic sample.</value><key>summary</key></description><description><value>Just a basic sample. </value><key>prerequisites</key></description><description><value><comments><comment><author>admin</author><post>Y3d4</post><datetime>1375128209.83</datetime></comment><comment><author>admin</author><post>Y3c=</post><datetime>1375128210.89</datetime></comment></comments></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description>Just a list of integer
and another new line</description><type>list</type><name>VAR_1</name><value>4,1,4,3,5,6</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>VAR_2</name><value>example</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>VAR_3</name><value>2</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>VAR_4</name><value>True</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>VAR_5</name><value>-3.0</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>VAR_6</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>date</type><name>VAR_7</name><value>03/06/2012</value><scope>local</scope></parameter><parameter><description /><type>time</type><name>VAR_8</name><value>18:09:41</value><scope>local</scope></parameter><parameter><description /><type>date-time</type><name>VAR_9</name><value>03/06/2012 18:09:44</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class GET_DESCRIPTION_AUTHOR(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)								
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		self.info( description('Author') )
		
		self.step1.setPassed(actual="success")

class GET_DESCRIPTION_DATE(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)								
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		self.info( description('creation date') )
		
		self.step1.setPassed(actual="success")
		
class GET_DESCRIPTION_SUMMARY(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)								
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		self.info( description('summary') )
		
		self.step1.setPassed(actual="success")
		
class GET_DESCRIPTION_PREREQUISITES(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)								
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		self.info( description('prerequisites') )
		
		self.step1.setPassed(actual="success")

class GET_DESCRIPTION_COMMENTS(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)								
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		self.info( description('comments') )
		
		self.step1.setPassed(actual="success")
]]></testdefinition>
<testexecution><![CDATA[
GET_DESCRIPTION_AUTHOR().execute()
GET_DESCRIPTION_DATE().execute()
GET_DESCRIPTION_SUMMARY().execute()
GET_DESCRIPTION_PREREQUISITES().execute()
GET_DESCRIPTION_COMMENTS().execute()
]]></testexecution>
<testdevelopment>1386106132.28</testdevelopment>
</file>