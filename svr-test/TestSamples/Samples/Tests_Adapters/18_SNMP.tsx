<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/09/2014 19:12:42</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><value>False</value><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>10.0.0.240</value><name>DEST_TRAP</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>10.0.0.240 (eth0)</value><name>IP_SSH</name><type>self-ip</type><scope>local</scope></parameter><parameter><color /><description /><value>root</value><name>LOGIN</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>xxxxxxx</value><name>PWD</name><type>pwd</type><scope>local</scope></parameter><parameter><value>0.0.0.0 (all)</value><description /><name>SRC_IP</name><type>self-ip</type><scope>local</scope></parameter><parameter><value>162</value><description /><name>SRC_PORT</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>False</value><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>20.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent-win-socket01</value><description /><name>AGENT_SOCKET</name><type>socket</type></agent><agent><value>agent-win-ssh01</value><description /><name>AGENT_SSH</name><type>ssh</type></agent></agents><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>probe-network01</name><type>network</type></probe></probes><outputs-parameters><parameter><color /><description /><value>1.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
# snmptrap -v 3 -n "" -a SHA -A mypassword -x AES -X mypassword -l authPriv -u traptest -e 0x8000000001020304 localhost 0 linkUp.0

class TESTCASE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.ADP_SSH = SutAdapters.SSH.Client(parent=self, login=input('LOGIN'), password=input('PWD'), destIp=input('IP_SSH'), destPort=22,
															bindIp='0.0.0.0', bindPort=0, destHost='', socketTimeout=10.0, socketFamily=4, name=None, 
															tcpKeepAlive=False, tcpKeepAliveInterval=30.0, debug=input('DEBUG'), logEventSent=True, logEventReceived=True, 
															parentName=None, shared=False, agent=agent('AGENT_SSH'), agentSupport=input('SUPPORT_AGENT'))
		self.ADP_SNMP = SutAdapters.SNMP.TrapReceiver(parent=self, bindIp=input('SRC_IP'), bindPort=input('SRC_PORT'), debug=input('DEBUG'),
																agent=agent('AGENT_SOCKET'), agentSupport=input('SUPPORT_AGENT')	)
		self.ADP_SNMP.startListening()
		udpListening = self.ADP_SNMP.udp().isListening( timeout=input('TIMEOUT') )
		if not udpListening:
			self.abort( 'UDP not listening' )
			
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual="error")
		self.ADP_SNMP.stopListening()
	def definition(self):
		# starting initial step
		self.step1.start()

		trapv1 = 'snmptrap -v 1 -c public %s 1.2.3 "" 6 17 "" 1.2.3.4.5.6 b 8' % input('DEST_TRAP')
		rsp= self.ADP_SSH.doSendCommand(command=trapv1, timeout=input('TIMEOUT'), expectedData=None, prompt='~]#')

		trap = self.ADP_SNMP.hasReceivedTrap(timeout=input('TIMEOUT'), version=SutAdapters.SNMP.TRAP_V1 , community=None, agentAddr=None, enterprise=None,
					genericTrap=None, specificTrap="17", uptime=None, requestId=None, errorStatus=None, errorIndex=None)
		if trap is None:
			self.abort("no trap received")

		trapv1 = 'snmptrap -v 2c -c public %s 111 1.2.3.4.5.6 1.2.3.4.5.6 i 8' % input('DEST_TRAP')
		rsp= self.ADP_SSH.doSendCommand(command=trapv1, timeout=input('TIMEOUT'), expectedData=None, prompt='~]#')

		trap = self.ADP_SNMP.hasReceivedTrap(timeout=input('TIMEOUT'), version=SutAdapters.SNMP.TRAP_V2C , community=None, agentAddr=None, enterprise=None,
					genericTrap=None, specificTrap=None, uptime=None, requestId=None, errorStatus=None, errorIndex=None)
		if trap is None:
			self.abort("no trap received")
			
			
		self.step1.setPassed(actual="success")
		]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1410196362.54</testdevelopment>
</file>