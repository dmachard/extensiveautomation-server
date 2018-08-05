<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>17/04/2017 11:33:48</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter><parameter><color /><description /><type>bool</type><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>dummy</type><name>AGENT</name><value>agent-dummy01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class DATE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose=description('summary'))
		self.setRequirement(requirement=description('requirement'))
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		pass
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			self.LIB_TODAY = SutLibraries.Date.Today(parent=self, name=None, debug=False, shared=False)
			
			day = self.LIB_TODAY.getDayNumber()
			self.warning( "day=%s" % day)
			
			day = self.LIB_TODAY.getDayName()
			self.warning( "day=%s" % day)
			
			month =  self.LIB_TODAY.getMonthNumber()
			self.warning( "month=%s" % month)
			
			month =  self.LIB_TODAY.getMonthName()
			self.warning( "month=%s" % month)
			
			year = self.LIB_TODAY.getYearNumber()
			self.warning( "year=%s" % year)
			
			week = self.LIB_TODAY.getWeekNumber()
			self.warning( "week=%s" % week)
			
			self.step1.setPassed(actual="success")
	def cleanup(self, aborted):
		pass]]></testdefinition>
<testexecution><![CDATA[
DATE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1492421628.986448</testdevelopment>
</file>