<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/05/2014 11:28:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>60</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>command</type><name>AGENT_WIN</name><value>agent.win.cmd01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_WINDOWS_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.AGT1_SYS = SutAdapters.System.Windows(parent=self, agent=agent('AGENT_WIN'), 
																debug=input('DEBUG'), shared=False)
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT1_SYS.getHostname()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			items = rsp.get('WINDOWS', 'items' ) 
			item0 = items.get('item 0')
			self.warning( 'Hostname: %s' % item0.get('hostname') )
			
		self.AGT1_SYS.getOs()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			items = rsp.get('WINDOWS', 'items' ) 
			item0 = items.get('item 0')
			self.warning( 'Os: %s' % item0.get('build-number') )
			
		self.AGT1_SYS.getProcesses()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Number of processes: %s' % rsp.get('WINDOWS', 'count-processes') )
			
		self.AGT1_SYS.getUptime()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			items = rsp.get('WINDOWS', 'items' ) 
			item0 = items.get('item 0')
			self.warning( 'Uptime: %s' % item0.get('last-boot-uptime') )
			
		self.AGT1_SYS.getCpuLoad()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			items = rsp.get('WINDOWS', 'items' ) 
			item0 = items.get('item 0')
			self.warning( 'Cpu load: %s' % item0.get('load-percentage') )
			
		self.AGT1_SYS.getDisks()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			items = rsp.get('WINDOWS', 'items' ) 
			item0 = items.get('item 0')
			self.warning( 'Disks: %s' % item0.get('device-id') )
			
		self.AGT1_SYS.getSystemInfo()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			# decode("cp850").encode("utf8") 
			self.warning( 'Sys: %s' % rsp.get('WINDOWS', 'info') )
			
		self.AGT1_SYS.getMemUsage()
		rsp = self.AGT1_SYS.hasReceivedResponse(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed('no response')
		else:
			self.warning( 'Mem: %s' % rsp.get('WINDOWS', 'total-physical') )			
			
	def cleanup(self, aborted):
		pass

]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_WINDOWS_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1399541300.3</testdevelopment>
</file>