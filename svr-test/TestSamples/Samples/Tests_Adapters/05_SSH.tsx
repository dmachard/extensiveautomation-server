<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'any', 'filter': ''}]}</args><name>network01</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>13/06/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><color /><description /><value>dsqdsq</value><name>BAD_PWD</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>date</value><name>CMD_SSH</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>False</value><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>10.0.0.240 (eth0)</value><name>DEST_IP</name><type>self-ip</type><scope>local</scope></parameter><parameter><color /><description /><value>22</value><name>DEST_PORT</name><type>int</type><scope>local</scope></parameter><parameter><color /><description /><value>root</value><name>LOGIN</name><type>str</type><scope>local</scope></parameter><parameter><color /><description>-----BEGIN RSA PRIVATE KEY-----
xxxx
-----END RSA PRIVATE KEY-----</description><value>-----BEGIN RSA PRIVATE KEY-----
xxxx
-----END RSA PRIVATE KEY-----</value><name>PRIVATE_KEY</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>root</value><name>PROMPT_SSH</name><type>str</type><scope>local</scope></parameter><parameter><color /><description /><value>!xtc2016</value><name>PWD</name><type>pwd</type><scope>local</scope></parameter><parameter><color /><description /><value>False</value><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><color /><description /><value>5.0</value><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter><parameter><color /><description /><value>False</value><name>VERBOSE</name><type>bool</type><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
# use for ssh cli (deprecated)
class TESTCASE_SSH_CLI_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host=input('DEST_IP'), username=input('LOGIN'), password=input('PWD'), 
				timeout=10, debug=input('DEBUG'), prompt='~]#')
		
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual="error")
	def definition(self):
		self.step1.start()

		self.ADP_SSH.login()
		if not self.ADP_SSH.isConnected(timeout=input('TIMEOUT')):
			self.abort('login failed')

		self.ADP_SSH.sendData(data='uname -a\r\n')

		rsp = self.ADP_SSH.hasReceivedData(timeout=input('TIMEOUT'))
		if rsp is None:
			self.step1.setFailed(actual="error")
		else:
			self.info( rsp.get('SSH', 'data') )
			
		self.ADP_SSH.logout()
		if not self.ADP_SSH.isDisconnected(timeout=input('TIMEOUT')):
			self.abort('logout failed')
			
		self.step1.setPassed(actual="success")


class TESTCASE_SSH_CLI_WRONG_PASSWORD_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host=input('DEST_IP'), username=input('LOGIN'), password=input('BAD_PWD'), 
				timeout=input('TIMEOUT'), debug=input('DEBUG'), prompt='~]\$')
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		self.ADP_SSH.login()
		if not self.ADP_SSH.isLoginFailed(timeout=input('TIMEOUT')):
			self.step1.setFailed(actual="error")
		else:	
			self.ADP_SSH.logout()
			self.step1.setPassed(actual="success")

class TESTCASE_SSH_CLI_WRONG_HOST_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host='227.0.0.2', username=input('LOGIN'), password=input('BAD_PWD'), 
				timeout=input('TIMEOUT'), debug=input('DEBUG'), prompt='~]\$')
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		self.ADP_SSH.login()
		if not self.ADP_SSH.isError(timeout=input('TIMEOUT')):
			self.step1.setFailed(actual="error")
		else:
			self.ADP_SSH.logout()
			self.step1.setPassed(actual="success")

class TESTCASE_SSH_CLI_WRONG_PORT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host='127.0.0.2', port=34, username=input('LOGIN'), password=input('BAD_PWD'), 
				timeout=input('TIMEOUT'), debug=input('DEBUG'), prompt='~]\$')
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		self.ADP_SSH.login()
		if not self.ADP_SSH.isError(timeout=input('TIMEOUT'), errReason=TestOperators.Contains(needle='refused')):
			self.step1.setFailed(actual="error")
		else:	
			self.ADP_SSH.logout()
			self.step1.setPassed(actual="success")

class TESTCASE_SSH_CLI_WRONG_PORT_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		pass
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host='127.0.0.2', port='a34', username=input('LOGIN'), password=input('BAD_PWD'), 
				timeout=input('TIMEOUT'), debug=input('DEBUG'), prompt='~]\$')
		
		self.ADP_SSH.login()
		
		self.ADP_SSH.logout()
		self.step1.setPassed(actual="success")
			
class TESTCASE_SSH_CLI_TIMEOUT_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)		
	def prepare(self):
		
		self.ADP_SSH = SutAdapters.SSH.Cli(parent=self, host='127.0.0.1', port='22', username=input('LOGIN'), password=input('PWD'), 
				timeout=input('TIMEOUT'), debug=input('DEBUG'), prompt='r~]\$')
		
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()

		self.ADP_SSH.login()
		
		self.ADP_SSH.logout()
		self.step1.setPassed(actual="success")
		
# ssh client
class TESTCASE_SSH_CLIENT_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		
		# steps description
		self.step1 = self.addStep(expected="successfully authenticated", description="connect to the machine through ssh", summary="connect to the machine through ssh")
		self.step2 = self.addStep(expected="ssh prompt found", description="find the prompt of the server root@", summary="find the prompt of the server %s" % input('PROMPT_SSH'))
		self.step3 = self.addStep(expected="date result", description="input the date of the server", summary="input the date of the server")
		self.step4 = self.addStep(expected="disconnected", description="tcp disconnection from the server", summary="tcp disconnection from the server")
	def prepare(self):
		# adapters and libraries

		self.ADP_SSH = SutAdapters.SSH.Client(parent=self, login=input('LOGIN'), password=input('PWD'), bindIp='', bindPort=0, 
																			destIp=input('DEST_IP'), destPort=input('DEST_PORT'), 
																			destHost='', socketTimeout=10.0, socketFamily=4, name=None, debug=input('DEBUG'),
																	logEventSent=True, logEventReceived=True, parentName=None, shared=False,
																	agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT'))
																	
	def cleanup(self, aborted):
		
		self.step4.start()
		self.ADP_SSH.disconnect()
		if not self.ADP_SSH.isDisconnected(timeout=input('TIMEOUT')):
			self.step4.setFailed('unable to disconnect from ssh properly')
		else:
			self.step4.setPassed('disconnected')
			
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_SSH.connect()
		if self.ADP_SSH.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort('unable to connect through tcp')
		
		if self.ADP_SSH.isNegotiated(timeout=input('TIMEOUT')) is None:
			self.step1.setFailed('unable to negotiate ssh')
			self.abort('unable to negotiate ssh')
	
		if self.ADP_SSH.isAuthenticated(timeout=input('TIMEOUT')) is None:
			self.step1.setFailed('unable to authenticate through ssh')
			self.abort('unable to authenticate through ssh')

		if self.ADP_SSH.isChannelOpened(timeout=input('TIMEOUT')) is None:
			self.step1.setFailed('unable to open channel through ssh')
			self.abort('unable to open channel through ssh')

		self.step1.setPassed('ssh authenticated and channel opened')
		
		self.step2.start()
		data = self.ADP_SSH.hasReceivedData(dataExpected=TestOperators.Contains(needle=input('PROMPT_SSH'), AND=True, OR=False), timeout=input('TIMEOUT'))
		if data is None:
			self.step1.setFailed('prompt ssh not found')
			self.abort('no data received through ssh')
		self.step2.setPassed('ssh prompt detected')
		
		self.step3.start()
		self.ADP_SSH.sendData( dataRaw="%s\n" % input('CMD_SSH') )
		data = self.ADP_SSH.hasReceivedData(dataExpected=TestOperators.Contains(needle=[ input('PROMPT_SSH') ] , AND=True, OR=False), timeout=input('TIMEOUT'))
		if data is None:
			self.step3.setFailed('no date returned by the server')
			self.abort('no date received from the server')
		
		rsp_date = data.get('SSH', 'data') 
		if input('CMD_SSH') in rsp_date:
			date = rsp_date.split(input('CMD_SSH'))[1].split(input('PROMPT_SSH'))[0]
		else:
			date = rsp_date.split(input('PROMPT_SSH'))[0]
			
		self.info( "Date on server: %s" % date.strip() )
		self.step3.setPassed('date returned')
class TESTCASE_SSH_CLIENT_02(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		
		# steps description
		self.step1 = self.addStep(expected="successfully authenticated", description="connect to the machine through ssh", summary="connect to the machine through ssh")
		self.step2 = self.addStep(expected="date result", description="get the date of the server", summary="get the date of the server")
		self.step3 = self.addStep(expected="disconnected", description="tcp disconnection from the server", summary="tcp disconnection from the server")
	def prepare(self):
		# adapters and libraries
		self.ADP_SSH = SutAdapters.SSH.Client(parent=self, login=input('LOGIN'), password=input('PWD'), bindIp='', bindPort=0, 
																			destIp=input('DEST_IP'), destPort=input('DEST_PORT'), 
																			destHost='', socketTimeout=10.0, socketFamily=4, name=None, debug=input('DEBUG'),
																	logEventSent=True, logEventReceived=True, parentName=None, shared=False,
																	agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT'))
	def cleanup(self, aborted):
		pass

	def definition(self):

		if self.step1.isEnabled():
			self.step1.start()
			if not self.ADP_SSH.doConnect(timeout=input('TIMEOUT'), prompt=input('PROMPT_SSH')):
				self.step1.setFailed('authentication failed'); self.abort()
			self.step1.setPassed('ssh authenticated and channel opened')
			
		if self.step2.isEnabled():
			self.step2.start()
			data = self.ADP_SSH.doSendCommand(command=input('CMD_SSH') , timeout=input('TIMEOUT'), 
																														expectedData=None, prompt=input('PROMPT_SSH'))
			if data is None:
				self.step2.setFailed('no expected data returned')
			else:
				self.step2.setPassed('data returned')
				if input('CMD_SSH') in data:
					date = data.split(input('CMD_SSH'))[1].split(input('PROMPT_SSH'))[0]
				else:
					date = data.split(input('PROMPT_SSH'))[0]
				self.warning( date.strip() )

		if self.step3.isEnabled():
			self.step3.start()
			if not self.ADP_SSH.doDisconnect(timeout=input('TIMEOUT')):
				self.step3.setFailed('ssh disconnection failed'); self.abort()
			self.step3.setPassed('ssh disconnection successful')

class TESTCASE_SSH_CLIENT_PRIVATE_KEY_02(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		
		# steps description
		self.step1 = self.addStep(expected="successfully authenticated", description="connect to the machine through ssh", summary="connect to the machine through ssh")
		self.step4 = self.addStep(expected="disconnected", description="tcp disconnection from the server", summary="tcp disconnection from the server")
	def prepare(self):
		# adapters and libraries

		self.ADP_SSH = SutAdapters.SSH.Client(parent=self, login=input('LOGIN'), bindIp='', bindPort=0, 
																			destIp=input('DEST_IP'), destPort=input('DEST_PORT'),  privateKey=input('PRIVATE_KEY'),
																			destHost='', socketTimeout=10.0, socketFamily=4, name=None, debug=input('DEBUG'),
																	logEventSent=True, logEventReceived=True, parentName=None, shared=False,
																	agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT'))
	def cleanup(self, aborted):
		
		self.step4.start()
		self.ADP_SSH.disconnect()
		if not self.ADP_SSH.isDisconnected(timeout=input('TIMEOUT')):
			self.step4.setFailed('unable to disconnect from ssh properly')
		else:
			self.step4.setPassed('disconnected')
			
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_SSH.connect()
		if not self.ADP_SSH.isConnected(timeout=input('TIMEOUT')):
			self.abort('unable to connect through tcp')
		
		if not self.ADP_SSH.isNegotiated(timeout=input('TIMEOUT')):
			self.step1.setFailed('unable to negotiate ssh')
			self.abort('unable to negotiate ssh')
	
		if not self.ADP_SSH.isAuthenticated(timeout=input('TIMEOUT')):
			self.step1.setFailed('unable to authenticate through ssh')
			self.abort('unable to authenticate through ssh')

		if not self.ADP_SSH.isChannelOpened(timeout=input('TIMEOUT')):
			self.step1.setFailed('unable to open channel through ssh')
			self.abort('unable to open channel through ssh')

		self.step1.setPassed('ssh authenticated and channel opened')
class TESTCASE_SSH_NO_VERBOSE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
			
			
			self.ADP_SSH = SutAdapters.SSH.Client(parent=self, destIp=input('DEST_IP'), destPort=22, bindIp='0.0.0.0', bindPort=0, 
																								destHost='', login=input('LOGIN'), password=input('PWD'), privateKey=None,
																								socketTimeout=10.0, socketFamily=4, name=None,  verbose=input('VERBOSE'),
																								tcpKeepAlive=False, tcpKeepAliveInterval=30.0, debug=input('DEBUG'), 
																								logEventSent=True, logEventReceived=True, parentName=None,
																								shared=False, sftpSupport=False, agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT'))
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
			
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()

			connected = self.ADP_SSH.doConnect(timeout=input('TIMEOUT'), prompt='~]#')
			if not connected: self.abort("connect failed")
			self.info("SSH connection OK" )
			
			BreakPoint(self)
			rsp = self.ADP_SSH. doSendCommand(command='ps fax', timeout=input('TIMEOUT'), expectedData=None, prompt='~]#')
			if rsp is None: self.abort("run command failed")
			self.warning( rsp )

			disconnected = self.ADP_SSH.doDisconnect(timeout=input('TIMEOUT'))
			if not disconnected: self.abort("disconnect failed")
			self.info("SSH disconnection OK" )
			
			self.step1.setPassed(actual="success")
			
# SSH console

class TESTCASE_SSH_CONSOLE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		self.ADP_CONSOLE = SutAdapters.SSH.Console(parent=self, destIp=input('DEST_IP'), destPort=input('DEST_PORT'), 
																																		bindIp='0.0.0.0', bindPort=0, destHost='', prompt='~]#', 
																																		login=input('LOGIN'), password=input('PWD'), privateKey=None, 
																																		verbose=input('VERBOSE'), socketTimeout=10.0, socketFamily=4, name=None, 
																																		tcpKeepAlive=False, tcpKeepAliveInterval=30.0, debug=input('DEBUG'), logEventSent=True, 
																																		logEventReceived=True, parentName=None, shared=False, sftpSupport=False, 
																																		agent=None, agentSupport=False, loopFrequence=1)
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			if not self.ADP_CONSOLE.doConnect(timeout=input('TIMEOUT')):
				self.abort("unable to login to the server")
				
			self.wait(2)
			self.ADP_CONSOLE.sendData(dataRaw="su - extensivetesting\n")
			self.wait(2)
			self.ADP_CONSOLE.sendData(dataRaw="su -\n")
			#self.ADP_CONSOLE.sendData(dataRaw="q\n")
			self.wait(10)
			
			if not self.ADP_CONSOLE.doDisconnect(timeout=input('TIMEOUT')):
				self.abort("unable to logout to the server")
				
			self.step1.setPassed(actual="success")
	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)

	]]></testdefinition>
<testexecution><![CDATA[
if not input('SUPPORT_AGENT'):
	TESTCASE_SSH_CLI_01(suffix=None).execute()
	TESTCASE_SSH_CLI_WRONG_PASSWORD_01(suffix=None).execute()
	TESTCASE_SSH_CLI_WRONG_HOST_01(suffix=None).execute()
	TESTCASE_SSH_CLI_WRONG_PORT_01(suffix=None).execute()
#	TESTCASE_SSH_CLI_WRONG_PORT_02(suffix=None).execute()
	TESTCASE_SSH_CLI_TIMEOUT_01(suffix=None).execute()
	TESTCASE_SSH_CONSOLE_01(suffix=None).execute()


TESTCASE_SSH_CLIENT_01(suffix=None).execute()
TESTCASE_SSH_CLIENT_02(suffix=None).execute()
#TESTCASE_SSH_CLIENT_PRIVATE_KEY_02(suffix=None).execute()
TESTCASE_SSH_NO_VERBOSE_01(suffix=None).execute()

]]></testexecution>
<testdevelopment>1386105846.63</testdevelopment>
</file>