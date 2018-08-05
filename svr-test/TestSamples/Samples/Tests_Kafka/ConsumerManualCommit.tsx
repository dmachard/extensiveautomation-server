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

			self.info('Connect to Kafka Cluster')
			consumer.connect( group_id='test-09', auto_offset_reset='earliest', enable_auto_commit=False,consumer_timeout_ms =2000)
			consumer.isConnected()
			
			
			self.info('Subscribe consumer to a topic with one partition')
			consumer.subscribe(input('TOPIC'))
			consumer.isSubscribe()		

			topic = TopicPartition(input('TOPIC'), 0)
			self.info('Get the first topic partition offset')
			consumer.beginning_offsets([topic])
			consumer.isBeginning_offsets()

			self.info('Fetch 10 records from last committed offset')
			consumer.poll(timeout_ms=1000, max_records=10)
			consumer.isPoll()	
			
			self.info('Commit and get last committed offset')
			consumer.commit()
			consumer.isCommit()


			self.info('Expect a committed offset lower than 100')
			consumer.committed(topic)
			offsets= { "offsets": TestOperatorsLib.LowerThan(x=100)}
			consumer.isCommitted(offsets=offsets)
			
			self.info('Pause partition to avoid fetch records from')
			consumer.pause(topic)
			consumer.isPause()
			consumer.paused()
			consumer.isPaused()

			consumer.poll(timeout_ms=1000, max_records=10)		
			consumer.isPoll()	
			
			self.info('Resume partition fetching records from')		
			consumer.resume(topic)
			consumer.isResume()
			consumer.paused()
			consumer.isPaused()
			
			
			self.info('Fetch 10 new records')
			consumer.poll(timeout_ms=1000, max_records=10)
			consumer.isPoll()	

			self.info('Commit async and get last committed offset')
			consumer.commit_async()
			consumer.isCommit_async()

			self.info('Wait before request last commited offset because of async call')
			time.sleep(2)
			consumer.committed(topic)
			consumer.isCommitted()

			self.info('Close')
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