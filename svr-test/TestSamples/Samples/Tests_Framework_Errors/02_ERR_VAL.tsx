<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>20/10/2014 18:42:47</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class ERR_VAL_001(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")


	def prepare(self):
		# adapters and libraries
		pass


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		a = TestValidators.String()
		ret = a.containsDigits(strVal=23)
class ERR_VAL_003(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")


	def prepare(self):
		# adapters and libraries
		pass


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		a = TestValidators.String()
		ret = a.containsLowerCase(strVal=2323)
class ERR_VAL_005(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")


	def prepare(self):
		# adapters and libraries
		pass


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		a = TestValidators.String()
		ret = a.containsPunctuations(strVal=2333)
class ERR_VAL_002(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")


	def prepare(self):
		# adapters and libraries
		pass


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		a = TestValidators.String()
		ret = a.containsUpperCase(strVal=222)
class ERR_VAL_004(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")


	def prepare(self):
		# adapters and libraries
		pass


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		a = TestValidators.String()
		ret = a.containsWhitespaces(strVal=123)]]></testdefinition>
<testexecution><![CDATA[
ERR_VAL_001(suffix=None).execute()
ERR_VAL_002(suffix=None).execute()
ERR_VAL_003(suffix=None).execute()
ERR_VAL_004(suffix=None).execute()
ERR_VAL_005(suffix=None).execute()

]]></testexecution>
<testdevelopment>1413823367.05</testdevelopment>
</file>