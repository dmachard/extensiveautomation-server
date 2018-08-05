<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/05/2014 11:28:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>20</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent.win.file01</value><description /><name>AGENT_FILE_WIN</name><type>file</type></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
# tests for windows
class TESTCASE_GETFILE_WIN_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.getFile(file="C:\\Windows\\write.exe")
	
		rsp = self.AGT_FILE.hasReceivedFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no file')
		else:
			content = rsp.get('FILE', 'content')
			self.warning( content.decode("latin1").encode("utf8") )


class TESTCASE_ISFILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isFile(path="C:\\Windows\\write.exe")
	
		rsp = self.AGT_FILE.hasReceivedIsFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no is file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_ISDIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isDirectory(path="C:\\Windows\\")
	
		rsp = self.AGT_FILE.hasReceivedIsDirectory(timeout=input('TIMEOUT'), isFolder=True)
		if rsp is None:
			self.abort('no is folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_ISLINK_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isLink(path="C:\\Users\\Public\\Desktop\\Extensive Testing Client.lnk")
	
		rsp = self.AGT_FILE.hasReceivedIsLink(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no is file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_CHECKSUM_MD5_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.checksumFile(file="C:\\Windows\\write.exe")
	
		rsp = self.AGT_FILE.hasReceivedChecksumFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no checksum file response')
		else:
			content = rsp.get('FILE', 'checksum')
			self.warning( content )
class TESTCASE_WAIT_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.waitForFile(path="C:\\usb_driver\\test.txt", timeout=15)
	
		rsp = self.AGT_FILE.hasReceivedWaitFile(timeout=input('TIMEOUT'), fileExists=True)
		if rsp is None:
			self.abort('no file exists response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_WAIT_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		reqId = self.AGT_FILE.waitForDirectory(path="C:\\Windows\\test\\", timeout=15)
	
		rsp = self.AGT_FILE.hasReceivedWaitDirectory(timeout=input('TIMEOUT'), directoryExists=True, requestId=reqId)
		if rsp is None:
			self.abort('no folder exists response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
			
class TESTCASE_EXISTS_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.existsFile(path="C:\\Windows\\writea.exe")
	
		rsp = self.AGT_FILE.hasReceivedExistsFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no exists file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_EXISTS_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.existsDirectory(path="C:\\Windows\\")
	
		rsp = self.AGT_FILE.hasReceivedExistsDirectory(timeout=input('TIMEOUT'), directoryExists=True)
		if rsp is None:
			self.abort('no exists folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_DELETE_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.deleteFile(file="D:\\My Lab\\ExtensiveTesting\\test.txt")
	
		rsp = self.AGT_FILE.hasReceivedDeleteFile(timeout=input('TIMEOUT'), fileDeleted=True)
		if rsp is None:
			self.abort('no delete file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_DELETE_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.deleteDirectory(path="D:\\My Lab\\ExtensiveTesting\\tmp\\")
	
		rsp = self.AGT_FILE.hasReceivedDeleteDirectory(timeout=input('TIMEOUT'), directoryDeleted=True)
		if rsp is None:
			self.abort('no delete folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
			
class TESTCASE_SIZE_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.sizeOfFile(file="C:\\Windows\\write2.exe")
	
		rsp = self.AGT_FILE.hasReceivedSizeFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no size file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_SIZE_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.sizeOfDirectory(path="C:\\Windows\\Web\\")
	
		rsp = self.AGT_FILE.hasReceivedSizeDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no size directory response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_COPY_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.copyFile(fileSrc="C:\\Newfolder\\test.txt", fileDst="C:\\Newfolder\\test2.txt")
	
		rsp = self.AGT_FILE.hasReceivedCopyFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no copy file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_COPY_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.copyDirectory(pathSrc="C:\\Newfolder\\", pathDst="C:\\Newfolder2\\")
	
		rsp = self.AGT_FILE.hasReceivedCopyDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no copy folder response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MOVE_DIRECTORY_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.moveDirectory(pathSrc="C:\\Newfolder2\\", pathDst="C:\\Newfolder\\")
	
		rsp = self.AGT_FILE.hasReceivedMoveDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move folder response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MOVE_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.moveFile(fileSrc="C:\\Newfolder\\Newfolder2\\titi.txt", fileDst="C:\\Newfolder\\")
	
		rsp = self.AGT_FILE.hasReceivedMoveFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MODIFICATION_DATE_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.modificationDateOfFile(file="C:\\Newfolder\\titi.txt")
	
		rsp = self.AGT_FILE.hasReceivedModificationDateFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_LIST_FILES_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.listFiles(path="C:\\Newfolder\\")
	
		rsp = self.AGT_FILE.hasReceivedListFiles(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no list file response')
		else:
			content = rsp.get('FILE', 'list-files')
			self.warning( content )
class TESTCASE_COMPARE_FILES_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.compareFiles(fileSrc="D:\\My Lab\\ExtensiveTesting\\04_Sources\\TODO_global.txt", 
																					fileDst="D:\\My Lab\\ExtensiveTesting\\04_Sources\\TODO_global.txt")
	
		rsp = self.AGT_FILE.hasReceivedCompareFiles(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no compare file response')
		else:
			content = rsp.get('FILE', 'result-html')
			self.warning( content )
class TESTCASE_START_FOLLOW_FILE_WIN_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_WIN'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		tailFile = "C:\\"

		reqA = self.AGT_FILE.startFollowFile(path=tailFile, extensions=["log"],  filter="- INFO -")
		if self.AGT_FILE.hasStartedFollowing(timeout=input('TIMEOUT')) is None:
			self.abort("unable to start tailf")

		log = self.AGT_FILE.hasReceivedLogFile(timeout=input('TIMEOUT'), 
												content=TestOperators.Contains(needle="Task registered", AND=True, OR=False) )
		if log is None:
			self.error( "expected log no received" )
		else:
			self.warning( log.get("FILE", "content") )
		
		self.AGT_FILE.stopFollowFile(followId=reqA)
		if self.AGT_FILE.hasStoppedFollowing(timeout=input('TIMEOUT')) is None:
			self.abort("unable to stop tailf")
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_GETFILE_WIN_01(suffix=None).execute()
TESTCASE_ISFILE_WIN_01(suffix=None).execute()
TESTCASE_ISDIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_ISLINK_WIN_01(suffix=None).execute()
TESTCASE_CHECKSUM_MD5_FILE_WIN_01(suffix=None).execute()
TESTCASE_WAIT_FILE_WIN_01(suffix=None).execute()
TESTCASE_WAIT_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_EXISTS_FILE_WIN_01(suffix=None).execute()
TESTCASE_EXISTS_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_DELETE_FILE_WIN_01(suffix=None).execute()
TESTCASE_DELETE_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_SIZE_FILE_WIN_01(suffix=None).execute()
TESTCASE_SIZE_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_COPY_FILE_WIN_01(suffix=None).execute()
TESTCASE_COPY_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_MOVE_DIRECTORY_WIN_01(suffix=None).execute()
TESTCASE_MOVE_FILE_WIN_01(suffix=None).execute()
TESTCASE_MODIFICATION_DATE_FILE_WIN_01(suffix=None).execute()
TESTCASE_LIST_FILES_WIN_01(suffix=None).execute()
TESTCASE_COMPARE_FILES_WIN_01(suffix=None).execute()
TESTCASE_START_FOLLOW_FILE_WIN_01(suffix=None).execute()
TESTCASE_START_FOLLOW_FILE_WIN_01(suffix=None).execute()
]]></testexecution>
<testdevelopment>1399541300.3</testdevelopment>
</file>