<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>14/05/2014 08:43:20</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class COMPRESS_GZIP_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample")
	def prepare(self):
		# adapters and libraries
		self.LIB_GZIP = SutLibraries.Compression.GZIP(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		self.step1.setPassed(actual="success")
		
		data = """This application tries to save your time and make your life easier at work."""
		data += """This application tries to save your time and make your life easier at work."""
		
		self.info( 'Initial Size: %s' % data )
		
		data_compressed = self.LIB_GZIP.compress(data)
		self.warning( "Size compressed: %s" % len(data_compressed) )
		
		data_uncompressed = self.LIB_GZIP.uncompress(data_compressed)
		self.warning( "Size uncompressed: %s" % len(data_uncompressed) )]]></testdefinition>
<testexecution><![CDATA[
COMPRESS_GZIP_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1400049800.06</testdevelopment>
</file>