<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>24/11/2016 21:28:22</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color>#DBADFF</color><value>SSH_ADP</value><name>ADP_NAME</name><description /><type>str</type><scope>local</scope></parameter><parameter><color>#DBADFF</color><value>False</value><name>ADP_SHARED</name><description /><type>bool</type><scope>local</scope></parameter><parameter><color>#DBADFF</color><value>False</value><name>ALREADY_SHARED</name><description /><type>bool</type><scope>local</scope></parameter><parameter><color>#D4FFAF</color><value># send a ping 
ping -c 3 [!CACHE:SVR:DEST_HOST:]
.*3 packets transmitted, 3 received, 0% packet loss.*mdev = [!CAPTURE:STATS:] ms.*

# clear the screen
clear
.*root@.*
</value><name>COMMANDS</name><description /><type>text</type><scope>local</scope></parameter><parameter><color>#FBFBFB</color><value>False</value><name>DEBUG</name><description /><type>bool</type><scope>local</scope></parameter><parameter><color>#FCABBD</color><value>1:Common:SAMPLE_NODE:SSH_ADMIN</value><name>SERVERS</name><description /><type>global</type><scope>local</scope></parameter><parameter><description /><name>STEP_EXPECTED</name><color>#C1EEFF</color><value>SSH command executed</value><scope>local</scope><type>text</type></parameter><parameter><description /><name>STEP_SUMMARY</name><color>#C1EEFF</color><value>Execute SSH commands</value><scope>local</scope><type>text</type></parameter><parameter><color>#C1EEFF</color><value>Send ssh commands</value><name>TEST_PURPOSE</name><description /><type>text</type><scope>local</scope></parameter><parameter><color /><value>20.0</value><name>TIMEOUT</name><description /><type>float</type><scope>local</scope></parameter><parameter><color /><value>10.0</value><name>TIMEOUT_CONNECT</name><description /><type>float</type><scope>local</scope></parameter><parameter><color /><value>True</value><name>VERBOSE</name><description /><type>bool</type><scope>local</scope></parameter></inputs-parameters><agents /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><value>1.0</value><name>TIMEOUT</name><description /><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class SEND_SSH_01(TestCase):
	def description(self, svr):
		# testcase description
		self.setPurpose(purpose=input('TEST_PURPOSE'))
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(expected="Connected to the remote host with success", 
																				description="Send ssh commands" ,
																				summary="Connect to the remote machine with ssh protocol", 
																				enabled=True)
	def prepare(self, svr):
		self.ADP_SYS = None
		if self.step1.isEnabled():
			self.step1.start()
	
			# adapters and libraries definitions
			if input('ALREADY_SHARED'):
				self.ADP_SYS = self.findAdapter( input('ADP_NAME') )
				if self.ADP_SYS is None: 
					self.step1.setFailed(actual="%s adapter not available" % input('ADP_NAME'))
					self.abort("%s adapter not available" % input('ADP_NAME'))
			else:
				
				if "SSH_DEST_HOST" not in svr: self.abort( "SSH_DEST_HOST key expected on provided server. more details\n%s" % svr  )
				if "SSH_DEST_PORT" not in svr: self.abort( "SSH_DEST_PORT expected on provided server. more details\n%s" % svr )
				if "SSH_DEST_LOGIN" not in svr: self.abort( "SSH_DEST_LOGIN expected on provided server. more details\n%s" % svr )
				if "SSH_DEST_PWD" not in svr: self.abort( "SSH_DEST_PWD expected on provided server. more details\n%s" % svr )
				if "SSH_PRIVATE_KEY" not in svr: self.abort( "SSH_PRIVATE_KEY expected on provided server. more details\n%s" % svr )
				if "SSH_PRIVATE_KEY_PATH" not in svr: self.abort( "SSH_PRIVATE_KEY_PATH expected on provided server. more details\n%s" % svr )
				if "SSH_AGENT" not in svr: self.abort( "SSH_AGENT expected on provided server. more details\n%s" % svr )
				if "SSH_AGENT_SUPPORT" not in svr: self.abort( "SSH_AGENT_SUPPORT expected on provided server. more details\n%s" % svr )
				
				self.ADP_SYS = SutAdapters.CLI.SshTerminal(parent=self, destIp=svr["SSH_DEST_HOST"],destPort=int(svr["SSH_DEST_PORT"]),
																																		login=svr["SSH_DEST_LOGIN"],password=svr["SSH_DEST_PWD"],
																																		agent=svr['SSH_AGENT'],
																																		agentSupport=svr['SSH_AGENT_SUPPORT'],
																																		debug=input('DEBUG'), shared=input('ADP_SHARED'), name=input('ADP_NAME'),
																																		verbose=input('VERBOSE'), 
																																		privateKey=svr['SSH_PRIVATE_KEY'], privateKeyPath=svr['SSH_PRIVATE_KEY_PATH'])

	def definition(self, svr):

		if not input('ALREADY_SHARED'):
			if not self.ADP_SYS.doSession(timeout=input('TIMEOUT_CONNECT')):
				self.step1.setFailed(actual="unable to connect")
				self.abort("unable to connect")
		self.step1.setPassed(actual="connected the remote host")


		i = 0
		block = 4
		stepN = None
		for sys_cmd in input('COMMANDS').splitlines():
			if not (i % block): 
				searchScreen = False
				stepN = self.addStep(expected="command executed with success", description=sys_cmd[1:], summary=sys_cmd[1:], enabled=True, thumbnail=None)
			
			if (i % block) == 1: 
				if stepN is None: continue
				stepN.start()
				self.ADP_SYS.doText(text=sys_cmd)
				
			if (i % block) == 2 and len(sys_cmd):
				if stepN is None: continue				
				searchScreen = False
				screen =  self.ADP_SYS.hasReceivedScreen(timeout=input('TIMEOUT'), text=TestOperators.RegEx(needle=sys_cmd))
				for line in screen.get("TERM", "data").splitlines():
					if input('VERBOSE'):
						self.info(line.strip())
				if screen is None:
					stepN.setFailed("unable to find %s in screen" % sys_cmd)
					self.abort("unable to find %s in screen" % sys_cmd)
				else:
					Cache().capture(data=screen.get("TERM", "data"), regexp=sys_cmd)
					stepN.setPassed("%s found in scren" % sys_cmd)

			if (i % block) == 2 and not len(sys_cmd):
				if not searchScreen:
					if stepN is None: continue
					stepN.setPassed("command executed without return")
				stepN = None	
				i += 1
			i += 1

	def cleanup(self, aborted, svr):
		if aborted:
			Trace(self).error(txt="%s" % aborted)
		if not input('ALREADY_SHARED'):
			if self.ADP_SYS is not None:
				self.ADP_SYS.doText(text="exit")
				self.ADP_SYS.doClose(timeout=input('TIMEOUT_CONNECT'))

]]></testdefinition>
<testexecution><![CDATA[
servers = input('SERVERS')
if servers is None: AbortTestSuite("no server provided")

if servers is None: AbortTestSuite(reason="no server provided")
if not isinstance(servers, list): servers = [ input('SERVERS') ]
	
for svr in servers:
	_hostname = None
	if "HOSTNAME" in svr:
		_hostname = svr["HOSTNAME"]
	_instance = None
	if "INSTANCE_NAME" in svr:
		_instance = svr["INSTANCE_NAME"]
	_suffix = _hostname
	if _instance is not None:
		_suffix = "%s_%s" % (_hostname, _instance)
	SEND_SSH_01(suffix=_suffix).execute(svr=svr)]]></testexecution>
<testdevelopment>1480019302.962758</testdevelopment>
</file>