<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>19/10/2014 22:35:30</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>alias</type><name>DEBUG</name><value>PARAM</value><scope>local</scope></parameter><parameter><description /><type>alias</type><name>PARAM_ALIAS</name><value>PARAM_ALIAS</value><scope>local</scope></parameter><parameter><description /><type>shared</type><name>PARAM_PRJ</name><value>2:Perso2:TEST:</value><scope>local</scope></parameter><parameter><description /><type>shared</type><name>PARAM_SHARED</name><value>1:Common:SERVER:IP</value><scope>local</scope></parameter><parameter><description /><type>shared</type><name>PARAM_SHARED2</name><value>1:Common:TIMEOUT:MAX</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>alias</type><name>PARAM_ALIAS</name><value>PARAM_ALIAS</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class ERR_PRO_001(TestCase):
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
		
		# introduce a bad parameter type in inputs
		inputs()[0]['type'] = 'bad'
		
		a = input('DEBUG')

class ERR_PRO_002(TestCase):
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
		
		description(name='bad')

class ERR_PRO_003(TestCase):
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
		
		agent('BAD')

class ERR_PRO_004(TestCase):
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
		
		self.info( input('UNKNOWN') )

class ERR_PRO_005(TestCase):
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
		
		self.info( input('PARAM_ALIAS') )
		
class ERR_PRO_006(TestCase):
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
		
		self.info( output('UNKNOWN') )

class ERR_PRO_007(TestCase):
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
		
		self.info( output('PARAM_ALIAS') )
class ERR_PRO_017(TestCase):
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
		
		self.info( input('PARAM_SHARED') )
		
class ERR_PRO_018(TestCase):

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
		
		self.info( input('PARAM_SHARED2')  )
class ERR_PRO_016(TestCase):

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
		
		self.info( input('PARAM_PRJ')  )]]></testdefinition>
<testexecution><![CDATA[
ERR_PRO_001(suffix=None).execute()
ERR_PRO_002(suffix=None).execute()
ERR_PRO_003(suffix=None).execute()
ERR_PRO_004(suffix=None).execute()
ERR_PRO_005(suffix=None).execute()
ERR_PRO_006(suffix=None).execute()
ERR_PRO_007(suffix=None).execute()

ERR_PRO_016(suffix=None).execute()
ERR_PRO_017(suffix=None).execute()
ERR_PRO_018(suffix=None).execute()]]></testexecution>
<testdevelopment>1413750930.88</testdevelopment>
</file>