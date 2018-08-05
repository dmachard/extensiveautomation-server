<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><probes><probe><type>default</type><args /><name>probe01</name><active>False</active></probe></probes><descriptions><description><value>admin</value><key>author</key></description><description><value>04/02/2018 18:52:08</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>Require topic creation: /opt/kafka/bin/kafka-topics.sh --zookeeper 127.0.0.1:2181 --topic test --create --partitions 1 --replication-factor 1</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><outputs-parameters><parameter><type>float</type><name>TIMEOUT</name><value>60.0</value><color /><description /><scope>local</scope></parameter></outputs-parameters><inputs-parameters><parameter><type>list</type><name>BOOTSTRAP_SERVERS</name><value>127.0.0.1:9092</value><description /><scope>local</scope></parameter><parameter><type>bool</type><name>DEBUG</name><value>False</value><color /><description /><scope>local</scope></parameter><parameter><type>bool</type><name>SUPPORT_AGENT</name><value>False</value><description /><scope>local</scope></parameter><parameter><type>float</type><name>TIMEOUT</name><value>10.0</value><color /><description /><scope>local</scope></parameter><parameter><type>str</type><name>TOPIC</name><description /><value>test</value><scope>local</scope></parameter><parameter><type>bool</type><name>VERBOSE</name><value>True</value><color /><description /><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><name>AGENT</name><value>KafkaAgent</value><description /></agent></agents></properties>
<testdefinition><![CDATA[ import json
import uuid
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib

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
		self.producer = SutAdapters.Kafka.ProducerClient(parent=self, 
																																					name=None, 
																																					bootstrap_servers=input('BOOTSTRAP_SERVERS'), 
																																					debug=False, 
																																					agentSupport=input('SUPPORT_AGENT'), 
																																					agent=agent('AGENT'), 
																																					shared=False, 
																																					verbose=True)
		

		pass

	def definition(self):
		# starting initial step
		if self.step1.isEnabled():
			self.step1.start()
			self.info('Connect to Kafka Cluster')
			self.producer.connect(request_timeout_ms=2000)
			ret=self.producer.isConnect(timeout=10)
			
			self.info("Get Partition for topic {0}".format(input('TOPIC')))
			self.producer.partitions_for(topic=input('TOPIC'))
			ret=self.producer.isPartitions_for(timeout=10)

	
			msg={'document': "'"+str(uuid.uuid4()).replace("-","")+"'"}
			self.info("Send json message {0}".format(msg))
			self.producer.send(input('TOPIC'), key="mykey", value=json.dumps(msg),timeout=10)
			resp=self.producer.isSend(timeout=10)
			
			if resp is not None:
				offset=resp.get("SEND", "Offset")

				expected_offset = offset+1
				self.producer.send(input('TOPIC'),  value=json.dumps(msg),timestamp_ms=576567230000, timeout=10)

				record = { "Topic":TestOperatorsLib.RegEx(input('TOPIC')), 
												"Partition": TestOperatorsLib.Any(), 
												"Offset":TestOperatorsLib.Any() , 
												"Timestamp": TestOperatorsLib.LowerThan(x=576567230001),
												"Checksum": TestOperatorsLib.Any(), 
												"Serialized_key_size":TestOperatorsLib.Any(), 
												"Serialized_value_size": TestOperatorsLib.Any()}
				ret=self.producer.isSend(timeout=10, record=record)
				self.producer.flush(timeout=10)
				ret=self.producer.isFlush(timeout=10)
				self.step1.setPassed(actual='produced')
			else:
				self.step1.setFailed(actual='failure')
				
			self.producer.close(10)
			ret=self.producer.isClose(timeout=10)


	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517766728.462951</testdevelopment>
</file>