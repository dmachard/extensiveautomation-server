<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>05/08/2015 08:08:19</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>dummy</type><name>AGENT</name><value>agent-dummy01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_TEMPLATE_COMPARE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
			
			# message
			msg_layer = TestTemplates.TemplateLayer(name="test")
			msg_layer.addKey("toto", "test")
	
			# tpl expected
			tpl_layer = TestTemplates.TemplateLayer(name="test")
			tpl_layer.addKey(TestOperators.Contains(needle="toto"), TestOperators.Any())
			
			tpl2 = TestTemplates.Template(parent=self)
			ret =tpl2.compare(template=msg_layer, expected=tpl_layer)
			
			self.info( "%s" % str(ret) )
			
			self.step1.setPassed(actual="success")
class TESTCASE_TEMPLATE_COMPARE_INVALID_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
			
			# message
			msg_layer = TestTemplates.TemplateLayer(name="test")
			msg_layer.addKey("toto", "test")
	
			# tpl expected
			tpl_layer = TestTemplates.TemplateLayer(name="test")
			tpl_layer.addKey(TestOperators.Contains(needle="toto2"), TestOperators.Any())
			
			tpl2 = TestTemplates.Template(parent=self)
			ret =tpl2.compare(template=msg_layer, expected=tpl_layer)
			
			self.info( "%s" % str(ret) )
			
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_TEMPLATE_COMPARE_01(suffix=None).execute()
TESTCASE_TEMPLATE_COMPARE_INVALID_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1438754899.961562</testdevelopment>
</file>