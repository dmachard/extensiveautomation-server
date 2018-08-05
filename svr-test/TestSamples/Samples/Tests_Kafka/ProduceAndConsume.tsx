<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><outputs-parameters><parameter><type>float</type><color /><name>TIMEOUT</name><description /><value>60.0</value><scope>local</scope></parameter></outputs-parameters><descriptions><description><value>admin</value><key>author</key></description><description><value>04/02/2018 18:52:08</value><key>creation date</key></description><description><value>Just a basic sample.</value><key>summary</key></description><description><value>None.</value><key>prerequisites</key></description><description><value><comments /></value><key>comments</key></description><description><value>myplugins</value><key>libraries</key></description><description><value>myplugins</value><key>adapters</key></description><description><value>Writing</value><key>state</key></description><description><value>REQ_01</value><key>requirement</key></description></descriptions><probes><probe><type>default</type><args /><name>probe01</name><active>False</active></probe></probes><inputs-parameters><parameter><type>list</type><name>BOOTSTRAP_SERVERS</name><description /><value>127.0.0.1:9092</value><scope>local</scope></parameter><parameter><type>bool</type><color /><name>DEBUG</name><description /><value>False</value><scope>local</scope></parameter><parameter><type>bool</type><name>SUPPORT_AGENT</name><description /><value>False</value><scope>local</scope></parameter><parameter><type>float</type><color /><name>TIMEOUT</name><description /><value>10.0</value><scope>local</scope></parameter><parameter><type>str</type><name>TOPIC</name><value>test</value><description /><scope>local</scope></parameter><parameter><type>bool</type><color /><name>VERBOSE</name><description /><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><name>AGENT</name><description /><value>KafkaAgent</value></agent></agents></properties>
<testdefinition><![CDATA[import json
import uuid
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
from kafka import TopicPartition
from kafka.consumer.fetcher import (
    CompletedFetch, ConsumerRecord, Fetcher, NoOffsetForPartitionError
)
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

			self.producer.partitions_for(topic=input('TOPIC'))
			ret=self.producer.isPartitions_for(timeout=10)

			msg={'document': "'"+str(uuid.uuid4()).replace("-","")+"'"}
			self.info("Send json message {0}".format(msg))
			self.producer.send(input('TOPIC'), key="mykey", value=json.dumps(msg),timeout=10)
			resp=self.producer.isSend(timeout=10)
			offset=resp.get("SEND", "Offset")

			self.info('Close producer')
			self.producer.close(10)
			ret=self.producer.isClose(timeout=10)

			self.info('Connect consumer')
			consumer  = SutAdapters.Kafka.ConsumerClient(parent=self, 
																																					 name=None, 
																																					 bootstrap_servers=input('BOOTSTRAP_SERVERS'), 
																																					 debug=False, 
																																					 agentSupport=input('SUPPORT_AGENT'), 
																																					 agent=agent('AGENT'), 
																																					 shared=False, 
																																					 verbose=True)

			consumer.connect( group_id='test-09', 
																	auto_offset_reset='earliest', 
																	enable_auto_commit=False,
																	consumer_timeout_ms =2000, 
																	value_deserializer=lambda m: json.loads(m.decode('utf-8')))
			topic = TopicPartition(input('TOPIC'), 0)
			consumer.assign([topic])
			self.info("Seek consumer at offset {0}".format(offset))
			consumer.seek(topic, offset)	
			consumer.isSeek()	
			self.info("Poll only record at offset {0}".format(offset))
			consumer.poll(timeout_ms=1000, max_records=1)

			resp=consumer.isPoll()		
			record=eval(resp.get("POLL", "records"))
			consumer_record= record.values()[0][0]
			message= consumer_record[6]
			self.info("Message retrieved: {0}".format(json.dumps(message)))		
			consumer.close()
			consumer.isClosed()			
			self.step1.setPassed(actual='Success')
	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517766728.462951</testdevelopment>
</file>