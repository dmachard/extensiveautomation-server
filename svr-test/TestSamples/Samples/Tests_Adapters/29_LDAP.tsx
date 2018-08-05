<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><value>admin</value><key>author</key></description><description><value>17/10/2016 07:50:26</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>cn=ldapadm,dc=extensivetesting,dc=local</value><description>admin dn</description><name>LDAP_DN</name><type>str</type><scope>local</scope></parameter><parameter><value>10.0.0.240</value><description /><name>LDAP_IP</name><type>str</type><scope>local</scope></parameter><parameter><value>389</value><description /><name>LDAP_PORT</name><type>int</type><scope>local</scope></parameter><parameter><value>bonjour</value><description>admin password

</description><name>LDAP_PWD</name><type>str</type><scope>local</scope></parameter><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter><parameter><value>True</value><description /><name>VERBOSE</name><type>bool</type><color /><scope>local</scope></parameter></inputs-parameters><agents><agent><value>agent-dummy01</value><description /><name>AGENT</name><type>dummy</type></agent></agents><probes><probe><active>False</active><args /><name>probe01</name><type>default</type></probe></probes><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[
class LDAP_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample")
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(expected="result expected", description="step description", summary="step sample", enabled=True)
	def prepare(self):
		# adapters and libraries
		self.ADP_LDAP = SutAdapters.LDAP.Client(parent=self, ip=input('LDAP_IP'), dn=input('LDAP_DN'), 
																																password=input('LDAP_PWD'), port=input('LDAP_PORT'), 
																															name=None, debug=False, shared=False, agentSupport=False, agent=None)
	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			
			self.ADP_LDAP.connect()
			if self.ADP_LDAP.isConnected(timeout=input('TIMEOUT')) is None:
				self.abort("unable to connect")
			
			baseDN = "dc=extensivetesting,dc=local"
			self.ADP_LDAP.search(baseDN, filter= '(objectclass=*)', attrs=[  ])
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")
			# self.warning( "%s" % rsp.get("LDAP", "results").getAsPy() )

			baseDN = "uid=denis9,ou=People,dc=extensivetesting,dc=local"
			add_record = [
															('objectclass', [ 'top', 'account', 'posixAccount']),
															('cn', ['denis4']),
															('uidNumber', ['8888']),
															('gidNumber', ['101']),
															('homeDirectory', ['/home/denis2']),
													]
			self.ADP_LDAP.add(baseDN, record = add_record)
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")

			self.ADP_LDAP.updateAttribute(baseDn=baseDN, attrName="homeDirectory", value="/home/denisX")
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")
			
			self.ADP_LDAP.addAttribute(baseDn=baseDN, attrName="loginShell", value="/bin/bash")
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")
			
			self.ADP_LDAP.deleteAttribute(baseDn=baseDN, attrName="loginShell", value="/bin/bash")
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")
			
			self.ADP_LDAP.delete(baseDn=baseDN)
			if self.ADP_LDAP.hasReceivedResponse(timeout=input('TIMEOUT'))  is None: self.abort("unable to get response")
			
			self.step1.setPassed(actual="success")
	def cleanup(self, aborted):
		self.ADP_LDAP.disconnect()
		if aborted: self.step1.setFailed(actual=aborted)
]]></testdefinition>
<testexecution><![CDATA[
LDAP_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1476683426.734798</testdevelopment>
</file>