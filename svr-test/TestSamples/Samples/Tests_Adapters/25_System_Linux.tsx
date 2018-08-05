<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/05/2014 11:28:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>20</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>command</type><name>AGENT_LINUX</name><value>agent-win-selenium01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT1_SYS = SutAdapters.System.Linux(parent=self, agent=agent('AGENT_LINUX'), 
																debug=input('DEBUG'), shared=False)

	## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT1_SYS.getHostname()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Hostname: %s' % rsp.get('LINUX', 'hostname') )
			
		self.AGT1_SYS.getCpuInfo()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Cpu number: %s' % rsp.get('LINUX', 'cpu-count') )
			
		self.AGT1_SYS.getMemUsage()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Mem usage: %s' % rsp.get('LINUX', 'total-physical') )
			

		self.AGT1_SYS.getOs()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Os: %s' % rsp.get('LINUX', 'os') )
		
		self.AGT1_SYS.getKernel()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Kernel: %s' % rsp.get('LINUX', 'kernel') )
			
	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass

]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_LINUX_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1399541300.3</testdevelopment>
</file>