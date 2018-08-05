<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>23/09/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><value>True</value><description /><name>DEBUG</name><type>bool</type><scope>local</scope></parameter><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class CIPHER_BLOWFISH_ECB_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)		
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.Blowfish(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
		text = "\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF"
		
#		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(strKey=key)
		self.info( "key: %s" % self.ciph.getKey() )
		
		encryptedText = self.ciph.encrypt(text)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(strData=encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_BLOWFISH_ECB_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.Blowfish(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "FFFFFFFFFFFFFFFF"
		text = "FFFFFFFFFFFFFFFF"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(hexKey=key)
		self.info( "key: %s" % self.ciph.getKey(hexKey=True) )
		
		encryptedText = self.ciph.encrypt(hexData=text, hexdigit=True)
		self.info( "text encrypted: %s" % encryptedText)
		
		decryptedText = self.ciph.decrypt(hexData=encryptedText)
		self.info( "text decrypted: %s" % decryptedText)
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_BLOWFISH_CBC_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.Blowfish(parent=self, debug=input('DEBUG'), mode=SutLibraries.Ciphers.MODE_CBC)
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "This is the key"
		text = "testtest"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(strKey=key)
		self.info( "key: %s" % self.ciph.getKey() )
		
		encryptedText = self.ciph.encrypt(text)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(strData=encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_RC4_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.RC4(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "Key"
		text = "Plaintext"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(strKey=key)	
		self.info( "key: %s" % self.ciph.getKey(strKey=True, hexKey=False) )
		
		encryptedText = self.ciph.encrypt(text)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_RC4_02(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.RC4(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "Key"
		text = "Plaintext"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(strKey=key)	
		self.info( "key: %s" % self.ciph.getKey(strKey=False, hexKey=True) )
		
		encryptedText = self.ciph.encrypt(strData=text, hexdigit=True)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(hexData=encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_RC4_03(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.RC4(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "Key"
		text = "\xdd\xdd"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(strKey=key)	
		self.info( "key: %s" % self.ciph.getKey(strKey=True, hexKey=False) )
		
		encryptedText = self.ciph.encrypt(text)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
		
class CIPHER_RC4_04(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.ciph = SutLibraries.Ciphers.RC4(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
		
		key = "bbeedd"
		text = "ffaabb01edff"
		
		self.info( "text in clear: %s" % text )
		
		self.ciph.setKey(hexKey=key)	
		self.info( "key: %s" % self.ciph.getKey(strKey=True, hexKey=False) )
		
		encryptedText = self.ciph.encrypt(hexData=text)
		self.info( "text encrypted: %s" % encryptedText )
		
		decryptedText = self.ciph.decrypt(strData=encryptedText)
		self.info( "text decrypted: %s" % decryptedText )
		
		self.step1.setPassed(actual="pass")
class OPENSSL_01(TestCase):
	def description(self):
		self.step1 = self.addStep(expected="ok", description="set as pass", summary="set as pass", enabled=True)	
	def prepare(self):
		self.openssl = SutLibraries.Ciphers.OpenSSL(parent=self, debug=input('DEBUG'))
	def cleanup(self, aborted):
		pass
	def definition(self):
		self.step1.start()
#		
#		ret = self.openssl.execute(cmd="rand -base64 128")
#		self.warning(ret)
		
		d = "hello"
#		self.warning("clear:%s" % d)
#		# base64
#		encoded = self.openssl.encrypt(cipher="base64", data=d)
#		self.warning("encoded: %s" % encoded)
#		
#		decoded = self.openssl.decrypt(cipher="base64", data=encoded)
#		self.warning("decoded: %s" % decoded)
		
		# aes
		k="dfb6ec4967d628079893a44de247a6fba4d54d8533d8e938a50231c82f66484c"
		iv="6773FE6BE7DA9ADF65047B2C58C72402"
		encoded = self.openssl.encrypt(cipher="aes-256-cbc", data=d, key=k, iv=iv, base64=True)
		self.warning("encoded: %s" % encoded )
		
		decoded = self.openssl.decrypt(cipher="aes-256-cbc", data=encoded, key=k, iv=iv, base64=True)
		self.warning("decoded: %s" % decoded)
		
		self.step1.setPassed(actual="pass")

class RSA_01(TestCase):
	def description(self):
		self.setPurpose(purpose=description('summary'))
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		self.LIB_RSA = SutLibraries.Ciphers.RSA(parent=self, name=None, debug=False, shared=False)

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			public, private = self.LIB_RSA.generate(keysize=2048)
			Trace(self).info(txt=public, bold=False, italic=False, multiline=False, raw=False)
			Trace(self).info(txt=private, bold=False, italic=False, multiline=False, raw=False)
			
			self.step1.setPassed(actual="success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
CIPHER_BLOWFISH_ECB_01(suffix=None).execute()
CIPHER_BLOWFISH_ECB_02(suffix=None).execute()
CIPHER_BLOWFISH_CBC_01(suffix=None).execute()
CIPHER_RC4_01(suffix=None).execute()
CIPHER_RC4_02(suffix=None).execute()
CIPHER_RC4_03(suffix=None).execute()
CIPHER_RC4_04(suffix=None).execute()
OPENSSL_01(suffix=None).execute()
RSA_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386106014.72</testdevelopment>
</file>