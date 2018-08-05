<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><description /><type /><name>AGENT</name><value>agent-socket01</value></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>23/08/2013</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></inputs-parameters><outputs-parameters><parameter><description /><type>float</type><name>TIMEOUT</name><value>1.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class CRC32_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.crc32 = SutLibraries.Hashing.CRC32(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		crc = self.crc32.compute(data='AB')
		self.info( crc )
		self.step1.setPassed(actual="pass")

class CRC32_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.crc32 = SutLibraries.Hashing.CRC32(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		crc = self.crc32.compute(data='AB', hexdigit=True)
		self.info( crc )
		self.step1.setPassed(actual="pass")
		
class CHECKSUM_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.checksum = SutLibraries.Hashing.Checksum(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sum = self.checksum.compute(data='AB')
		self.info( sum )
		self.step1.setPassed(actual="pass")
		
class CHECKSUM_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.checksum = SutLibraries.Hashing.Checksum(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sum = self.checksum.compute(data='AB', hexdigit=True)
		self.info( sum )
		self.step1.setPassed(actual="pass")
		
class MD5_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.md5 = SutLibraries.Hashing.MD5(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		md5_d = self.md5.compute(data='AB')
		self.info( md5_d )
		self.step1.setPassed(actual="pass")
class MD5_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.md5 = SutLibraries.Hashing.MD5(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		md5_d = self.md5.compute(data='AB', hexdigit=True)
		self.info( md5_d )
		self.step1.setPassed(actual="pass")
class SHA1_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha1 = SutLibraries.Hashing.SHA1(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha1_d = self.sha1.compute(data='AB')
		self.info( sha1_d )
		self.step1.setPassed(actual="pass")
class SHA1_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha1 = SutLibraries.Hashing.SHA1(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha1_d = self.sha1.compute(data='AB', hexdigit=True)
		self.info( sha1_d )
		self.step1.setPassed(actual="pass")
class SHA256_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha256 = SutLibraries.Hashing.SHA256(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha256_d = self.sha256.compute(data='AB')
		self.info( sha256_d )
		self.step1.setPassed(actual="pass")
class SHA256_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha256 = SutLibraries.Hashing.SHA256(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha256_d = self.sha256.compute(data='AB', hexdigit=True)
		self.info( sha256_d )
		self.step1.setPassed(actual="pass")
class SHA512_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha512 = SutLibraries.Hashing.SHA512(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha512_d = self.sha512.compute(data='AB')
		self.info( sha512_d )
		self.step1.setPassed(actual="pass")
class SHA512_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.sha512 = SutLibraries.Hashing.SHA512(parent=self, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		sha512_d = self.sha512.compute(data='AB', hexdigit=True)
		self.info( sha512_d )
		self.step1.setPassed(actual="pass")
class HMAC_MD5_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = '\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b'
		self.hmac = SutLibraries.Hashing.HMAC_MD5(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="Hi There")
		self.info( hmac_str )
		self.step1.setPassed(actual="pass")
class HMAC_MD5_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = '\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b\x0b'
		self.hmac = SutLibraries.Hashing.HMAC_MD5(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="Hi There", hexdigit=True)
		self.info( hmac_str )
		self.step1.setPassed(actual="pass")
class HMAC_SHA1_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = "Jefe"
		self.hmac = SutLibraries.Hashing.HMAC_SHA1(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="what do ya want for nothing?")
		self.info( hmac_str )
		self.step1.setPassed(actual="pass")
class HMAC_SHA1_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = "Jefe"
		self.hmac = SutLibraries.Hashing.HMAC_SHA1(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="what do ya want for nothing?", hexdigit=True)
		self.info( hmac_str )
		self.step1.setPassed(actual="pass")
class HMAC_SHA256_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = "Jefe"
		self.hmac = SutLibraries.Hashing.HMAC_SHA256(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="what do ya want for nothing?")
		self.info( hmac_str )
		self.step1.setPassed(actual="pass")
class HMAC_SHA256_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		key = "Jefe"
		self.hmac = SutLibraries.Hashing.HMAC_SHA256(parent=self, key=key, debug=False)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		hmac_str = self.hmac.compute(data="what do ya want for nothing?", hexdigit=True)
		self.info( len(hmac_str) )
		self.step1.setPassed(actual="pass")]]></testdefinition>
<testexecution><![CDATA[
CHECKSUM_01(suffix=None).execute()
CHECKSUM_02(suffix=None).execute()
CRC32_01(suffix=None).execute()
CRC32_02(suffix=None).execute()
MD5_01(suffix=None).execute()
MD5_02(suffix=None).execute()
SHA1_01(suffix=None).execute()
SHA1_02(suffix=None).execute()
SHA256_01(suffix=None).execute()
SHA256_02(suffix=None).execute()
SHA512_01(suffix=None).execute()
SHA512_02(suffix=None).execute()
HMAC_MD5_01(suffix=None).execute()
HMAC_MD5_02(suffix=None).execute()
HMAC_SHA1_01(suffix=None).execute()
HMAC_SHA1_02(suffix=None).execute()
HMAC_SHA256_01(suffix=None).execute()
HMAC_SHA256_02(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106016.92</testdevelopment>
</file>