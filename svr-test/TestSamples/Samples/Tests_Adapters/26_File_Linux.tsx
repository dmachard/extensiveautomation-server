<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>08/05/2014 11:28:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>20</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type>file</type><name>AGENT_FILE_LINUX</name><value>agent-linux-file01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[# tests for linux
class TESTCASE_GETFILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.getFile(file="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no file')
		else:
			content = rsp.get('FILE', 'content')
			self.warning( content )


class TESTCASE_ISFILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isFile(path="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedIsFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no is file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_ISDIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isDirectory(path="/var/log/")
	
		rsp = self.AGT_FILE.hasReceivedIsDirectory(timeout=input('TIMEOUT'), isFolder=True)
		if rsp is None:
			self.abort('no is folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_ISLINK_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.isLink(path="/opt/xtc/current")
	
		rsp = self.AGT_FILE.hasReceivedIsLink(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no is file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_CHECKSUM_MD5_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.checksumFile(file="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedChecksumFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no checksum file response')
		else:
			content = rsp.get('FILE', 'checksum')
			self.warning( content )
class TESTCASE_WAIT_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.waitForFile(path="/var/log/test", timeout=15)
	
		rsp = self.AGT_FILE.hasReceivedWaitFile(timeout=input('TIMEOUT'), fileExists=True)
		if rsp is None:
			self.abort('no file exists response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_WAIT_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		reqId = self.AGT_FILE.waitForDirectory(path="/var/log/toto/", timeout=15)
	
		rsp = self.AGT_FILE.hasReceivedWaitDirectory(timeout=input('TIMEOUT'), directoryExists=True, requestId=reqId)
		if rsp is None:
			self.abort('no folder exists response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
			
class TESTCASE_EXISTS_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.existsFile(path="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedExistsFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no exists file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )

class TESTCASE_EXISTS_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.existsDirectory(path="/var/")
	
		rsp = self.AGT_FILE.hasReceivedExistsDirectory(timeout=input('TIMEOUT'), directoryExists=True)
		if rsp is None:
			self.abort('no exists folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_DELETE_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.deleteFile(file="/var/log/test")
	
		rsp = self.AGT_FILE.hasReceivedDeleteFile(timeout=input('TIMEOUT'), fileDeleted=True)
		if rsp is None:
			self.abort('no delete file response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
class TESTCASE_DELETE_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.deleteDirectory(path="/var/log/toto/")
	
		rsp = self.AGT_FILE.hasReceivedDeleteDirectory(timeout=input('TIMEOUT'), directoryDeleted=True)
		if rsp is None:
			self.abort('no delete folder response')
		else:
			content = rsp.get('FILE', 'result')
			self.warning( content )
			
class TESTCASE_SIZE_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.sizeOfFile(file="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedSizeFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no size file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_SIZE_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.sizeOfDirectory(path="/var/log/")
	
		rsp = self.AGT_FILE.hasReceivedSizeDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no size directory response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_COPY_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.copyFile(fileSrc="/var/log/titi.txt", fileDst="/var/log/titi2.txt")
	
		rsp = self.AGT_FILE.hasReceivedCopyFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no copy file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_COPY_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.copyDirectory(pathSrc="/var/log/tutu/", pathDst="/var/log/tutu2/")
	
		rsp = self.AGT_FILE.hasReceivedCopyDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no copy folder response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MOVE_DIRECTORY_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.moveDirectory(pathSrc="/var/log/tutu/", pathDst="/var/log/tutu2/")
	
		rsp = self.AGT_FILE.hasReceivedMoveDirectory(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move folder response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MOVE_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.moveFile(fileSrc="/var/log/titi.txt", fileDst="/var/log/tutu2/")
	
		rsp = self.AGT_FILE.hasReceivedMoveFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_MODIFICATION_DATE_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.modificationDateOfFile(file="/var/log/messages")
	
		rsp = self.AGT_FILE.hasReceivedModificationDateFile(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no move file response')
		else:
			content = rsp.get('FILE', 'size')
			self.warning( content )
class TESTCASE_LIST_FILES_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		self.AGT_FILE.listFiles(path="/var/log/")
	
		rsp = self.AGT_FILE.hasReceivedListFiles(timeout=input('TIMEOUT'))
		if rsp is None:
			self.abort('no list file response')
		else:
			content = rsp.get('FILE', 'list-files')
			self.warning( content )
class TESTCASE_START_FOLLOW_FILE_LINUX_01(TestCase):
	## >> called on test initialization
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")

	## >> called on test preparation, adapters and libraries definitions
	def prepare(self):
		# adapters and libraries
		self.AGT_FILE = SutAdapters.System.File(parent=self, agent=agent('AGENT_FILE_LINUX'),  debug=input('DEBUG'), shared=False)

	## >> called on error or to cleanup the test properly
	def cleanup(self, aborted):
		pass
## >> called on test begin
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		tailFile = "/opt/xtc/current/Var/Logs/"

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
TESTCASE_GETFILE_LINUX_01(suffix=None).execute()
TESTCASE_ISFILE_LINUX_01(suffix=None).execute()
TESTCASE_ISDIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_ISLINK_LINUX_01(suffix=None).execute()
TESTCASE_CHECKSUM_MD5_FILE_LINUX_01(suffix=None).execute()
TESTCASE_WAIT_FILE_LINUX_01(suffix=None).execute()
TESTCASE_WAIT_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_EXISTS_FILE_LINUX_01(suffix=None).execute()
TESTCASE_EXISTS_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_DELETE_FILE_LINUX_01(suffix=None).execute()
TESTCASE_DELETE_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_SIZE_FILE_LINUX_01(suffix=None).execute()
TESTCASE_SIZE_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_COPY_FILE_LINUX_01(suffix=None).execute()
TESTCASE_COPY_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_MOVE_DIRECTORY_LINUX_01(suffix=None).execute()
TESTCASE_MOVE_FILE_LINUX_01(suffix=None).execute()
TESTCASE_MODIFICATION_DATE_FILE_LINUX_01(suffix=None).execute()
TESTCASE_LIST_FILES_LINUX_01(suffix=None).execute()
TESTCASE_START_FOLLOW_FILE_LINUX_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1399541300.3</testdevelopment>
</file>