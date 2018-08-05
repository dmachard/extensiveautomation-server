<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>06/09/2015 11:11:47</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>self-ip</type><name>DEST_IP</name><value>10.0.0.240 (eth0)</value><scope>local</scope></parameter><parameter><description /><type>int</type><name>DEST_PORT</name><value>22</value><scope>local</scope></parameter><parameter><description /><type>str</type><name>LOGIN</name><value>root</value><scope>local</scope></parameter><parameter><description>-----BEGIN RSA PRIVATE KEY-----
xxxxx
-----END RSA PRIVATE KEY-----</description><type>str</type><name>PRIVATE_KEY</name><value>-----BEGIN RSA PRIVATE KEY-----
xxxxx
-----END RSA PRIVATE KEY-----</value><scope>local</scope></parameter><parameter><description /><type>pwd</type><name>PWD</name><value>xxx</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter><parameter><description /><type>bool</type><name>VERBOSE</name><value>False</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>dummy</type><name>AGENT</name><value>agent-dummy01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_SFTP_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)

	def prepare(self):
		# adapters and libraries

			self.SFTP_ADP = SutAdapters.SFTP.Client(parent=self, login=input('LOGIN'), password=input('PWD'), bindIp='', bindPort=0, 
																				destIp=input('DEST_IP'), destPort=input('DEST_PORT'), debug=input('DEBUG'),
																				agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT') )


	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")
			

			self.SFTP_ADP.connect()
			if not self.SFTP_ADP.isConnected(timeout=input('TIMEOUT')):
				self.abort('unable to connect through SFTP')
			if not self.SFTP_ADP.isLogged(timeout=input('TIMEOUT')):
				self.abort('unable to login through SFTP')
				
			self.SFTP_ADP.listingFolder(path="/home/ftpuser/")
			if self.SFTP_ADP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
				pass
				
			self.SFTP_ADP.listingFolder(path="/home/ftpuser/", extended=True)
			if self.SFTP_ADP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
				pass

			self.SFTP_ADP.addFolder(path="/home/ftpuser/test/")
			if self.SFTP_ADP.isFolderAdded(timeout=input('TIMEOUT')) is not None:
				pass
				
			self.SFTP_ADP.renameFolder(currentPath="/home/ftpuser/test/", newPath="/home/ftpuser/test2/")
			if self.SFTP_ADP.isFolderRenamed(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.deleteFolder(path="/home/ftpuser/test2")
			if self.SFTP_ADP.isFolderDeleted(timeout=input('TIMEOUT')) is not None:
				pass
			
			self.SFTP_ADP.putFile(toFilename="/home/ftpuser/toto.txt",  rawContent="dsqdsqé")
			if self.SFTP_ADP.hasUploadedFile(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.getFile(filename="/home/ftpuser/toto.txt", toPrivate=True)
			if self.SFTP_ADP.hasDownloadedFile(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.renameFile(currentFilename="/home/ftpuser/toto.txt", newFilename="/home/ftpuser/toto2.txt")
			if self.SFTP_ADP.isFileRenamed(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.deleteFile(filename="/home/ftpuser/toto2.txt")
			if self.SFTP_ADP.isFileDeleted(timeout=input('TIMEOUT')) is not None:
				pass
			
			self.SFTP_ADP.disconnect()
			if not self.SFTP_ADP.isDisconnected(timeout=input('TIMEOUT')):
				self.abort('unable to disconnect through SFTP')

class TESTCASE_SFTP_PRIVATEKEY_02(TestCase):

	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)


	def prepare(self):
		# adapters and libraries
			

			self.SFTP_ADP = SutAdapters.SFTP.Client(parent=self, login=input('LOGIN'), privateKey=input('PRIVATE_KEY'), bindIp='', bindPort=0, 
																				destIp=input('DEST_IP'), destPort=input('DEST_PORT'), debug=input('DEBUG'),
																			agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT') 	)

	def cleanup(self, aborted):
		pass


	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.step1.setPassed(actual="success")

			self.SFTP_ADP.connect()
			if not self.SFTP_ADP.isConnected(timeout=input('TIMEOUT')):
				self.abort('unable to connect through SFTP')
			if not self.SFTP_ADP.isLogged(timeout=input('TIMEOUT')):
				self.abort('unable to login through SFTP')
				
			self.SFTP_ADP.listingFolder(path="/home/ftpuser/")
			if self.SFTP_ADP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
				pass
				
			self.SFTP_ADP.listingFolder(path="/home/ftpuser/", extended=True)
			if self.SFTP_ADP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
				pass

			self.SFTP_ADP.addFolder(path="/home/ftpuser/test/")
			if self.SFTP_ADP.isFolderAdded(timeout=input('TIMEOUT')) is not None:
				pass
				
			self.SFTP_ADP.renameFolder(currentPath="/home/ftpuser/test/", newPath="/home/ftpuser/test2/")
			if self.SFTP_ADP.isFolderRenamed(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.deleteFolder(path="/home/ftpuser/test2")
			if self.SFTP_ADP.isFolderDeleted(timeout=input('TIMEOUT')) is not None:
				pass
			
			self.SFTP_ADP.putFile(toFilename="/home/ftpuser/toto.txt",  rawContent="dsqdsqé")
			if self.SFTP_ADP.hasUploadedFile(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.getFile(filename="/home/ftpuser/toto.txt")
			if self.SFTP_ADP.hasDownloadedFile(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.renameFile(currentFilename="/home/ftpuser/toto.txt", newFilename="/home/ftpuser/toto2.txt")
			if self.SFTP_ADP.isFileRenamed(timeout=input('TIMEOUT')) is not None:
				pass
			self.SFTP_ADP.deleteFile(filename="/home/ftpuser/toto2.txt")
			if self.SFTP_ADP.isFileDeleted(timeout=input('TIMEOUT')) is not None:
				pass
			
			self.SFTP_ADP.disconnect()
			if not self.SFTP_ADP.isDisconnected(timeout=input('TIMEOUT')):
				self.abort('unable to disconnect through SFTP')

class TESTCASE_SFTP_REGEXP_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
	
		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
	
			self.ADP = SutAdapters.SFTP.Client(parent=self, destIp=input('DEST_IP'), destPort=input('DEST_PORT'), bindIp='', bindPort=0,
																												login=input('LOGIN'), password=input('PWD'), privateKey=None,
																												name=None, debug=input('DEBUG'),
																												shared=False, agent=agent('AGENT'), agentSupport=input('SUPPORT_AGENT') ,
																												verbose=input('VERBOSE'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()

			connected = self.ADP.doConnect(timeout=input('TIMEOUT'))
			if not connected: self.step1.setFailed(actual="do connect error"); self.abort("connect failed")
			self.info("SFTP connection OK" )
			
			BreakPoint(self)
			self.ADP.listingFolder(path="/var/log/", extended=False)
			rsp = self.ADP.hasFolderListing(timeout=input('TIMEOUT'))
			if rsp is None: self.step1.setFailed(actual="no listing");  self.error("unable to get listing")
			self.warning( rsp.get("SFTP", "result") )
			
			self.ADP.waitForFile(path='/var/log/', filename='^messages-.*$', timeout=input('TIMEOUT'))
			found = self.ADP.hasDetectedFile(path=None, filename=None, timeout=input('TIMEOUT'))
			if found is None: self.step1.setFailed(actual="file not found"); self.error("file not found")
			
			self.ADP.disconnect()
			disconnected = self.ADP.doDisconnect(timeout=input('TIMEOUT'))
			if not disconnected: self.step1.setFailed(actual="do disconnect error");  self.abort("disconnect failed")
			self.info("SFTP disconnection OK" )
	
			self.step1.setPassed(actual="success")
			]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_SFTP_01(suffix=None).execute()
#TESTCASE_SFTP_PRIVATEKEY_02(suffix=None).execute()
TESTCASE_SFTP_REGEXP_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1441530707.005597</testdevelopment>
</file>