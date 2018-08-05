<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value /><key>author</key></description><description><value /><key>creation date</key></description><description><value /><key>summary</key></description><description><value /><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>str</type><name>PARAM0</name><value>0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class CMP_OP_REGEX_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "^t"
		self.info( "search \"%s\" in \"%s\"" % (needle,haystack) )
		if TestOperators.RegEx(needle=needle).seekIn(haystack=haystack):
			self.info( "search successful" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_REGEX_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "^a"
		self.info( "search \"%s\" in \"%s\"" % (needle,haystack) )
		if TestOperators.RegEx(needle=needle).seekIn(haystack=haystack):
			self.info( "search successful" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setPassed(actual="success")


class CMP_OP_NOTREGEX_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "^a"
		self.info( "search if \"%s\" is not in \"%s\"" % (needle,haystack) )
		if TestOperators.NotRegEx(needle=needle).seekIn(haystack=haystack):
			self.info( "not found" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "found" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_NOTREGEX_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "^test"
		self.info( "search if \"%s\" is not in \"%s\"" % (needle,haystack) )
		if TestOperators.NotRegEx(needle=needle).seekIn(haystack=haystack):
			self.info( "not found" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "found" )
			self.step1.setPassed(actual="success")

class CMP_OP_CONTAINS_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "for"
		self.info( "search \"%s\" in \"%s\"" % (needle,haystack) )
		if TestOperators.Contains(needle=needle).seekIn(haystack=haystack):
			self.info( "search successful" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_CONTAINS_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "for2"
		self.info( "search \"%s\" in \"%s\"" % (needle,haystack) )
		if TestOperators.Contains(needle=needle).seekIn(haystack=haystack):
			self.info( "search successful" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setPassed(actual="success")


class CMP_OP_NOTCONTAINS_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "for2"
		self.info( "search if \"%s\" is not in \"%s\"" % (needle,haystack) )
		if TestOperators.NotContains(needle=needle).seekIn(haystack=haystack):
			self.info( "not found" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "found" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_NOTCONTAINS_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "for"
		self.info( "search if \"%s\" is not in \"%s\"" % (needle,haystack) )
		if TestOperators.NotContains(needle=needle).seekIn(haystack=haystack):
			self.info( "not found" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "found" )
			self.step1.setPassed(actual="success")


class CMP_OP_STARTSWITH_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "test"
		self.info( "search if \"%s\" starts with \"%s\"" % (haystack,needle) )
		if TestOperators.Startswith(needle=needle).seekIn(haystack=haystack):
			self.info( "found" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setFailed(actual="success")

class CMP_OP_STARTSWITH_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "test2"
		self.info( "search if \"%s\" starts with \"%s\"" % (haystack,needle) )
		if TestOperators.Startswith(needle=needle).seekIn(haystack=haystack):
			self.info( "found" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setPassed(actual="success")


class CMP_OP_ENDSWITH_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "framework"
		self.info( "search if \"%s\" endswith \"%s\"" % (haystack,needle) )
		if TestOperators.Endswith(needle=needle).seekIn(haystack=haystack):
			self.info( "found" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_ENDSWITH_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		haystack = "test for framework"
		needle = "framework2"
		self.info( "search if \"%s\" endswith \"%s\"" % (haystack,needle) )
		if TestOperators.Endswith(needle=needle).seekIn(haystack=haystack):
			self.info( "found" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "not found" )
			self.step1.setPassed(actual="success")


class CMP_OP_GREATERTHAN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		x = 20
		y = 40
		self.info( "check if %s > %s" % (y,x) )
		if TestOperators.GreaterThan(x=x).comp(y=y):
			self.info( "is greater" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "is not greater" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_GREATERTHAN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		x = 20
		y = -10
		self.info( "check if %s > %s" % (y,x) )
		if TestOperators.GreaterThan(x=x).comp(y=y):
			self.info( "is greater" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "is not greater" )
			self.step1.setPassed(actual="success")


class CMP_OP_LOWERTHAN_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		x = 20
		y = 10
		self.info( "check if %s < %s" % (y,x) )
		if TestOperators.LowerThan(x=x).comp(y=y):
			self.info( "is lower" )
			self.step1.setPassed(actual="success")
		else:
			self.info( "is not lower" )
			self.step1.setFailed(actual="success")
			
class CMP_OP_LOWERTHAN_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)			
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass		
	def definition(self):
		self.step1.start()
		
		x = -20
		y = -10
		self.info( "check if %s < %s" % (y,x) )
		if TestOperators.LowerThan(x=x).comp(y=y):
			self.info( "is lower" )
			self.step1.setFailed(actual="success")
		else:
			self.info( "is not lower" )
			self.step1.setPassed(actual="success")]]></testdefinition>
<testexecution><![CDATA[
CMP_OP_REGEX_01().execute()
CMP_OP_REGEX_02().execute()

CMP_OP_NOTREGEX_01().execute()
CMP_OP_NOTREGEX_02().execute()

CMP_OP_CONTAINS_01().execute()
CMP_OP_CONTAINS_02().execute()

CMP_OP_NOTCONTAINS_01().execute()
CMP_OP_NOTCONTAINS_02().execute()

CMP_OP_STARTSWITH_01().execute()
CMP_OP_STARTSWITH_02().execute()

CMP_OP_ENDSWITH_01().execute()
CMP_OP_ENDSWITH_02().execute()

CMP_OP_GREATERTHAN_01().execute()
CMP_OP_GREATERTHAN_02().execute()

CMP_OP_LOWERTHAN_01().execute()
CMP_OP_LOWERTHAN_02().execute()]]></testexecution>
<testdevelopment>1386106076.68</testdevelopment>
</file>