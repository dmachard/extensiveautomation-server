<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><parameters /><probes><probe><active>False</active><args>{'interfaces': [{'interface': 'eth0', 'filter': ''}]}</args><name>network1</name><type>network</type></probe></probes><agents><agent><value>agent-socket01</value><description /><name>AGENT</name><type /></agent></agents><descriptions><description><value>admin</value><key>author</key></description><description><value>14/10/2012</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><value>False</value><description /><name>DEBUG</name><type>bool</type><color /><scope>local</scope></parameter><parameter><value>10.0.0.1</value><description /><name>DST</name><type>str</type><color /><scope>local</scope></parameter><parameter><value>eth0</value><description /><name>ETH</name><type>self-eth</type><color /><scope>local</scope></parameter><parameter><value>10.0.0.240 (eth0)</value><description /><name>SRC</name><type>self-ip</type><color /><scope>local</scope></parameter><parameter><value>1.0</value><description /><name>TIMEOUT</name><type>float</type><color /><scope>local</scope></parameter></inputs-parameters></properties>
<testdefinition><![CDATA[
class PING_01(TestCase):
	def description(self):
		# testcase description
		self.setPurpose(purpose="Testcase sample for ping adapter")

		# steps description
		self.step1 = self.addStep(expected="pong from %s" % input('DST'), description="send a ping to %s" % input('DST'), summary="ping")
		
	def prepare(self):
		# adapters
		self.ping = SutAdapters.ICMP.Ping(parent=self, debug=input('DEBUG'), ipVersion=4, version=1)
	def cleanup(self, aborted):
		pass
	def definition(self):
		# starting initial step
		self.step1.start()
		pong = self.ping.ip(interface=input('ETH'), source=input('SRC'), destination=input('DST'), timeout=input('TIMEOUT'))
		if pong is None:
			self.step1.setFailed(actual='no pong received')
		else:
			self.step1.setPassed(actual='pong received')
			self.info( pong )]]></testdefinition>
<testexecution><![CDATA[
PING_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1386105879.33</testdevelopment>
</file>