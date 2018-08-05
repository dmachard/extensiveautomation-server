<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><key>author</key><value>admin</value></description><description><key>creation date</key><value>04/02/2018 18:52:08</value></description><description><key>summary</key><value>Just a basic sample.</value></description><description><key>prerequisites</key><value>None.</value></description><description><key>comments</key><value><comments /></value></description><description><key>libraries</key><value>myplugins</value></description><description><key>adapters</key><value>myplugins</value></description><description><key>state</key><value>Writing</value></description><description><key>requirement</key><value>REQ_01</value></description></descriptions><inputs-parameters><parameter><type>list</type><description /><name>BOOTSTRAP_SERVERS</name><value>127.0.0.1:9092</value><scope>local</scope></parameter><parameter><type>bool</type><color /><description /><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><type>bool</type><description /><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><type>float</type><color /><description /><name>TIMEOUT</name><value>10.0</value><scope>local</scope></parameter><parameter><type>str</type><value>test</value><name>TOPIC</name><description /><scope>local</scope></parameter><parameter><type>bool</type><color /><description /><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><description /><name>AGENT</name><value>KafkaAgent</value></agent></agents><probes><probe><active>False</active><args /><type>default</type><name>probe01</name></probe></probes><outputs-parameters><parameter><type>float</type><color /><description /><name>TIMEOUT</name><value>60.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[import json
import time
import uuid
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
			producer = SutAdapters.Kafka.ProducerClient(parent=self, 
																																			name=None, 
																																			bootstrap_servers=input('BOOTSTRAP_SERVERS'), 
																																			debug=False, 
																																			agentSupport=input('SUPPORT_AGENT'), 
																																			agent=agent('AGENT'), 
																																			shared=False, 
																																			verbose=True)
		
			self.info('Connect to Kafka Cluster')
			producer.connect(request_timeout_ms=2000)
			ret=producer.isConnect(timeout=10)
			if ret != None:
				self.info('Connected to Kafka Cluster')
			else:
				self.info('Connection issue')
#			producer.partitions_for(topic=input('TOPIC'))
			
			

			self.info('Produce 10 messages')			
			for key in range(10):
				msg={'document': "'"+str(uuid.uuid4()).replace("-","")+"'"}
				producer.send(input('TOPIC'), key=str(key), value=json.dumps(msg),timeout=10)
				ret=producer.isSend(timeout=10)

			self.info('Close Kafka Cluster Producer')
			producer.close(10)
			ret=producer.isClose(timeout=10)

			self.step1.setPassed(actual='Success')
	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517766728.462951</testdevelopment>
</file>