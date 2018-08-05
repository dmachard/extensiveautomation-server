<?xml version="1.0" encoding="utf-8" ?>
<file>
<properties><descriptions><description><key>author</key><value>admin</value></description><description><key>creation date</key><value>04/02/2018 18:52:08</value></description><description><key>summary</key><value>Just a basic sample.</value></description><description><key>prerequisites</key><value>None.</value></description><description><key>comments</key><value><comments /></value></description><description><key>libraries</key><value>myplugins</value></description><description><key>adapters</key><value>myplugins</value></description><description><key>state</key><value>Writing</value></description><description><key>requirement</key><value>REQ_01</value></description></descriptions><probes><probe><active>False</active><args /><type>default</type><name>probe01</name></probe></probes><inputs-parameters><parameter><type>list</type><description /><name>BOOTSTRAP_SERVERS</name><value>127.0.0.1:9092</value><scope>local</scope></parameter><parameter><color /><description /><type>bool</type><name>DEBUG</name><value>False</value><scope>local</scope></parameter><parameter><type>bool</type><description /><name>SUPPORT_AGENT</name><value>False</value><scope>local</scope></parameter><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>10.0</value><scope>local</scope></parameter><parameter><type>str</type><description /><name>TOPIC</name><value>test</value><scope>local</scope></parameter><parameter><color /><description /><type>bool</type><name>VERBOSE</name><value>True</value><scope>local</scope></parameter></inputs-parameters><agents><agent><type>kafka</type><description /><name>AGENT</name><value>KafkaAgent</value></agent></agents><outputs-parameters><parameter><color /><description /><type>float</type><name>TIMEOUT</name><value>60.0</value><scope>local</scope></parameter></outputs-parameters></properties>
<testdefinition><![CDATA[from kafka import TopicPartition

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

			consumer.connect( group_id=None)
			consumer.isConnected()
			self.info('Assign consumer to a topic and check assignement')
			topic = TopicPartition(input('TOPIC'), 0)
			consumer.assign([topic])
			consumer.isAssigned()
			
			consumer.assignment()
			consumer.isAssignment()
			
			self.info('Get position of next record that will be fetched')
			consumer.position(topic)

			self.info('Get current offset position')
			resp=consumer.isPosition()
			position=resp.get("POSITION", "offset")
			
			self.info('Specify to fetch the last message')

			consumer.seek(topic, int(position) - 1)	
			consumer.isSeek()		
			consumer.poll(timeout_ms=10000, max_records=10)
			consumer.isPoll()		
			
			self.info('Specify to fetch the 10 first messages')		
			consumer.seek_to_beginning(topic)
			consumer.isSeek_to_beginning()
	
			consumer.poll(timeout_ms=10000, max_records=10)
			consumer.isPoll()		
			
			self.info('Specify to fetch only currently produced messages')		
			consumer.seek_to_end(topic)			
			consumer.isSeek_to_end()
			consumer.poll(timeout_ms=10000, max_records=10)	
			consumer.isPoll()		
			self.info('Get highwater, next offset will be assigned to record procuced')
			consumer.highwater(topic)	
			consumer.isHighwater()		
			self.info('Get end_offsets, the offset of the upcoming message')
			consumer.end_offsets(topic)				
			consumer.isEnd_offsets()
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