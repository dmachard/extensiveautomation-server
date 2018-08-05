<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><outputs-parameters><parameter><type>float</type><color /><name>TIMEOUT</name><description /><value>60.0</value><scope>local</scope></parameter></outputs-parameters><descriptions><description><value>admin</value><key>author</key></description><description><value>04/02/2018 18:52:08</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><probes><probe><type>default</type><args /><name>probe01</name><active>False</active></probe></probes><inputs-parameters><parameter><type>list</type><name>BOOTSTRAP_SERVERS</name><description /><value>127.0.0.1:9092</value><scope>local</scope></parameter><parameter><type>bool</type><color /><name>DEBUG</name><description /><value>False</value><scope>local</scope></parameter><parameter><type>bool</type><name>SUPPORT_AGENT</name><description /><value>False</value><scope>local</scope></parameter><parameter><type>float</type><color /><name>TIMEOUT</name><description /><value>10.0</value><scope>local</scope></parameter><parameter><type>str</type><description /><name>TOPIC</name><value>test</value><scope>local</scope></parameter><parameter><type>bool</type><color /><name>VERBOSE</name><description /><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><name>AGENT</name><description /><value>KafkaAgent</value></agent></agents></properties>
<testdefinition><![CDATA[
import time

class TESTCASE_01(TestCase):
	def description(self):
		self.setPurpose(purpose=description('summary'))
		self.setRequirement(requirement=description('requirement'))

		# steps description
		self.step1 = self.addStep(
																				expected="result expected", 
																				description="step description", 
																				summary="step sample", 
																				enabled=True
																			)
	def prepare(self):
		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			consumer  = SutAdapters.Kafka.ConsumerClient(parent=self, 
																																					name=None, 
																																					bootstrap_servers=input('BOOTSTRAP_SERVERS'), 
																																					debug=False, 
																																					agentSupport=input('SUPPORT_AGENT'), 
																																					agent=agent('AGENT'), 
																																					shared=False, 
																																					verbose=True)


			consumer.connect(input('TOPIC'), 
																group_id='my-group5535',
																auto_offset_reset='earliest', 
																enable_auto_commit=False,
																consumer_timeout_ms =2000)


			time.sleep(5)
			consumer.consume()
			ret=consumer.isConsumed(timeout=10)
			
			time.sleep(5)
			consumer.close()
			self.step1.setPassed(actual="Success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517766728.462951</testdevelopment>
</file>