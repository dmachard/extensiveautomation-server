<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><key>author</key><value>admin</value></description><description><key>creation date</key><value>04/02/2018 18:52:08</value></description><description><key>summary</key><value>Just a basic sample.</value></description><description><key>prerequisites</key><value>None.</value></description><description><key>comments</key><value><comments /></value></description><description><key>libraries</key><value>myplugins</value></description><description><key>adapters</key><value>myplugins</value></description><description><key>state</key><value>Writing</value></description><description><key>requirement</key><value>REQ_01</value></description></descriptions><inputs-parameters><parameter><type>list</type><description /><name>BOOTSTRAP_SERVERS</name><value>127.0.0.1:9092</value><scope>local</scope></parameter><parameter><color /><type>bool</type><description /><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><type>bool</type><description /><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><color /><type>float</type><description /><name>TIMEOUT</name><value>10.0</value><scope>local</scope></parameter><parameter><type>str</type><description /><name>TOPIC</name><value>test</value><scope>local</scope></parameter><parameter><color /><type>bool</type><description /><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><description /><name>AGENT</name><value>KafkaAgent</value></agent></agents><probes><probe><active>False</active><args /><type>default</type><name>probe01</name></probe></probes><outputs-parameters><parameter><color /><type>float</type><description /><name>TIMEOUT</name><value>60.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[from kafka import TopicPartition
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
			topic = input('TOPIC')
			consumer.connect(topic, group_id='test')
			consumer.isConnected()

			self.info('List authorized topics for consumer')
			consumer.topics()
			consumer.isTopics()

			self.info('Subscribe consumer to a topic and check subscription')

			consumer.subscribe(input('TOPIC'))
			consumer.isSubscribe()
			consumer.subscription()
			consumer.isSubscription()

			
			self.info('Get partitions for topic')
			consumer.partitions_for_topic(topic)			
			resp=consumer.isPartitions_for_topic()
			partitions=resp.get(name="PARTITIONS_FOR_TOPIC", key="partitions")

			self.info('Get the earliest offset for each partition whose timestamp is greater than or equal to the given timestamp: origin')
			timestampms = 0

			partitions=eval(partitions) 
			for	partition in partitions:
				tp = TopicPartition(input('TOPIC'), partition)

				topics_timestamp_dict = {}
				topics_timestamp_dict[tp] = timestampms 
				consumer.offsets_for_times(topics_timestamp_dict)
				consumer.isOffsets_for_times()

			self.info('Unubscribe consumer from topic')
			consumer.unsubscribe()

			self.info('Close consumer')	
			consumer.close()
			consumer.isClosed()
			self.step1.setPassed(actual="Success")

	def cleanup(self, aborted):
		pass
]]></testdefinition>
<testexecution><![CDATA[
TESTCASE_01(suffix=None).execute()]]></testexecution>
<testdevelopment>1517766728.462951</testdevelopment>
</file>