<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/05/2014 11:28:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>ftp.freebsd.org</value><description /><name>FTP_HOST</name><type>custom</type><scope>local</scope></parameter><parameter><value>anonymous</value><description /><name>FTP_PWD</name><type>str</type><scope>local</scope></parameter><parameter><value>True</value><description /><name>FTP_TLS</name><type>bool</type><scope>local</scope></parameter><parameter><value>anonymous</value><description /><name>FTP_USER</name><type>str</type><scope>local</scope></parameter><parameter><value>False</value><description /><name>SUPPORT_AGENT</name><type>bool</type><scope>local</scope></parameter><parameter><value>30</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent-win-socket01</value><description /><name>AGENT_FTP</name><type>socket</type></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class TESTCASE_GETFILE_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		self.ADP_FTP = SutAdapters.FTP.Client(parent=self,  debug=input('DEBUG'), shared=False, 
																													destinationIp=input('FTP_HOST'),
																													user=input('FTP_USER'), password=input('FTP_PWD') ,
																													tlsSupport=False, agent=agent('AGENT_FTP'), 
																													agentSupport=input('SUPPORT_AGENT') )

	def cleanup(self, aborted):
		if aborted:
			self.step1.setFailed(actual=aborted)
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_FTP.connect(passiveMode=True)
		if self.ADP_FTP.isConnected(timeout=input('TIMEOUT')) is  None:
			self.abort("unable to connect")
	
		self.ADP_FTP.login()
		if self.ADP_FTP.isLogged(timeout=input('TIMEOUT')) is  None:
			self.abort("unable to login")
			
		self.ADP_FTP.gotoFolder(path="/")
		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
			self.step1.setFailed(actual="unable to go in /")
			
		self.ADP_FTP.listingFolder()
		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
			self.step1.setFailed(actual="unable to list folder")
			
#		self.ADP_FTP.listingFolder(path='/pub/', extended=True)
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to list folder /pub/")
#
#		# testing add, rename and delete folder
#		self.ADP_FTP.addFolder(path='/pub/test')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to go in /pub/test")
#			
#		self.ADP_FTP.renameFolder(currentPath='/pub/test', newPath='/pub/test2')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to rename folder /pub/test")
#			
#		self.ADP_FTP.deleteFolder(path='/pub/test2')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to delete folder /pub/test2")
#
#		# handle file
#		self.ADP_FTP.putFile(rawContent='world', toFilename='/pub/hello.txt')
#		if self.ADP_FTP.hasUploadedFile(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to upload file")
#
#		self.ADP_FTP.renameFile(currentFilename='/pub/hello.txt', newFilename='/pub/hello2.txt')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to rename file /pub/hello.txt")
#
#		self.ADP_FTP.sizeOfFile(filename='/pub/hello2.txt')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to get the size of the file")
#			
#		self.ADP_FTP.getFile(filename='/pub/hello2.txt')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to download file")
#
#		self.ADP_FTP.deleteFile(filename='/pub/hello2.txt')
#		if self.ADP_FTP.hasReceivedResponse(timeout=input('TIMEOUT')) is  None:
#			self.step1.setFailed(actual="unable to delete file")

		self.ADP_FTP.disconnect()
		if self.ADP_FTP.isDisconnected(timeout=input('TIMEOUT')) is None:
			self.step1.setFailed(actual="unable to disconnect from ftp")
			
		self.step1.setPassed(actual="success")
		
class TESTCASE_GETFILE_TLS_02(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.ADP_FTP = SutAdapters.FTP.Client(parent=self,  debug=input('DEBUG'), shared=False, 
																													destinationIp=input('FTP_HOST'),
																													user=input('FTP_USER'), password=input('FTP_PWD') ,
																													tlsSupport=input('FTP_TLS'), agent=agent('AGENT_FTP'),
																													agentSupport=input('SUPPORT_AGENT') )
	def cleanup(self, aborted):
		if aborted: self.step1.setFailed(actual=aborted)
	def definition(self):
		# starting initial step
		self.step1.start()

		self.ADP_FTP.connect(passiveMode=True)
		if self.ADP_FTP.isConnected(timeout=input('TIMEOUT')) is None:
			self.abort("unable to connect")

		self.ADP_FTP.login()
		if self.ADP_FTP.isLogged(timeout=input('TIMEOUT')) is  None:
			self.abort("unable to login")
		
		if self.ADP_FTP.hasReceivedWelcome(timeout=input('TIMEOUT')) is not None:

			if self.ADP_FTP.isDataSecured(timeout=input('TIMEOUT')) is not None:
				
				self.ADP_FTP.gotoFolder(path="/home/ftpuser/")
				if self.ADP_FTP.isFolderChanged(timeout=input('TIMEOUT')) is not None:
					pass
				self.ADP_FTP.currentPath()
				if self.ADP_FTP.hasCurrentPath(timeout=input('TIMEOUT')) is not None:
					pass
					
				self.ADP_FTP.listingFolder()
				if self.ADP_FTP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
					pass
					
#				self.ADP_FTP.listingFolder(path='/home/ftpuser/', extended=True)
#				if self.ADP_FTP.hasFolderListing(timeout=input('TIMEOUT')) is not None:
#					pass
#
#				self.ADP_FTP.addFolder(path='/home/ftpuser/test')
#				if self.ADP_FTP.isFolderAdded(timeout=input('TIMEOUT')) is not None:
#					pass
#					
#				self.ADP_FTP.renameFolder(currentPath='/home/ftpuser/test', newPath='/home/ftpuser/test2')
#				if self.ADP_FTP.isFolderRenamed(timeout=input('TIMEOUT')) is not None:
#					pass
#					
#				self.ADP_FTP.deleteFolder(path='/home/ftpuser/test2')
#				if self.ADP_FTP.isFolderDeleted(timeout=input('TIMEOUT')) is not None:
#					pass
#					
#				self.ADP_FTP.putFile(rawContent='fdsfdsfdsé', toFilename='/home/ftpuser/hello3.txt')
#				if self.ADP_FTP.hasUploadedFile(timeout=input('TIMEOUT')) is not None:
#					pass
#
#				self.ADP_FTP.renameFile(currentFilename='/home/ftpuser/hello3.txt', newFilename='/home/ftpuser/hello.txt')
#				if self.ADP_FTP.isFileRenamed(timeout=input('TIMEOUT')) is not None:
#					pass
#
#				self.ADP_FTP.sizeOfFile(filename='/home/ftpuser/hello.txt')
#				if self.ADP_FTP.hasFileSize(timeout=input('TIMEOUT')) is not None:
#					pass
#					
#				self.ADP_FTP.getFile(filename='/home/ftpuser/hello.txt')
#				if self.ADP_FTP.hasDownloadedFile(timeout=input('TIMEOUT')) is not None:
#					pass
#					
#				self.ADP_FTP.deleteFile(filename='/home/ftpuser/hello.txt')
#				if self.ADP_FTP.isFileDeleted(timeout=input('TIMEOUT')) is not None:
#					pass
			
		self.ADP_FTP.disconnect()
		if self.ADP_FTP.isDisconnected(timeout=input('TIMEOUT')) is not None:
			pass
			
		self.step1.setPassed(actual="success")
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_GETFILE_01(suffix=None).execute()
#TESTCASE_GETFILE_TLS_02(suffix=None).execute()]]></testexecution>
<testdevelopment>1399541300.3</testdevelopment>
</file>