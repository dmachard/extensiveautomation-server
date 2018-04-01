#!/usr/bin/env python
# -*- coding=utf-8 -*-

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import copy
import logging
import templates
from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

from kafka import KafkaConsumer
from kafka.errors import KafkaError

__NAME__="""KAFKA"""

AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='kafka'
CONSUMER="consumer"

CONNECT = "connect"
CONSUME = "consume"
POSITION='position'
POLL="poll"
RESUME="resume"
PAUSE="pause"
PAUSED="paused"
SEEK='seek'
ASSIGN='assign'
ASSIGNMENT='assignment'
SEEK_TO_BEGINNING="seek_to_beginning"
SEEK_TO_END="seek_to_end"
DISCONNECT="close" 
PARTITIONS_FOR="partitions_for"
HIGHWATER="highwater"
END_OFFSETS="end_offsets"
SUBSCRIBE="subscribe"
SUBSCRIPTION="subscription"
UNSUBSCRIBE="unsubscribe"
TOPICS="topics"
OFFSETS_FOR_TIMES="offsets_for_times"
PARTITIONS_FOR_TOPIC="partitions_for_topic"
COMMITTED="committed"
COMMIT_ASYNC="commit_async"
COMMIT="commit"
CLOSE="close" 
BEGINNING_OFFSETS="beginning_offsets"

class ConsumerClient(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, name=None, bootstrap_servers=None,  debug=False, agentSupport=False, agent=None, shared=False, verbose=True, logEventSent=True, logEventReceived=True):
		"""
		KAFKA Consumer client Adapter. simple Mapping of kafka-python KafkaConsumer

		@param parent: parent testcase
		@type parent: testcase

		@bootstrap_servers: Kafka broker used to boostrap at connect call (list of ip address port )
		@type bootstrap_servers: List
		
		@param agent: agent to use when this mode is activated
		@type agent: string/None
		
		@param name: adapter name used with from origin/to destination (default=None)
		@type name: string/none
		
		@param debug: active debug mode (default=False)
		@type debug:	boolean

		@param shared: shared adapter (default=False)
		@type shared:	boolean
		"""	
		self.bootstrap_servers = bootstrap_servers

		# check agent
		if agentSupport and agent is None:
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "Agent cannot be undefined!" )	
			
		if agentSupport:
			if not isinstance(agent, dict) : 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent argument is not a dict (%s)" % type(agent) )
			if not len(agent['name']): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "agent name cannot be empty" )
			if  unicode(agent['type']) != unicode(AGENT_TYPE_EXPECTED): 
				raise TestAdapterLib.ValueException(TestAdapterLib.caller(), 'Bad agent type: %s, expected: %s' % (agent['type'], unicode(AGENT_TYPE_EXPECTED))  )
		

		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, debug=debug, realname=name,
																							agentSupport=agentSupport, agent=agent, shared=shared)
		self.parent = parent
		self.codecX2D = Xml2Dict.Xml2Dict()
		self.codecD2X = Dict2Xml.Dict2Xml(coding = None)
		self.logEventSent = logEventSent
		self.logEventReceived = logEventReceived
		self.parent = parent
		self.cfg = {}
		if agent is not None:
			self.cfg['agent'] = agent
			self.cfg['agent-name'] = agent['name']
		self.cfg['agent-support'] = agentSupport

		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, name="keepalive-agent", callback=self.aliveAgent,
																																logEvent=False, enabled=True)		

		self.__checkConfig()
		
		# initialize the agent with no data
		if agent is not None:
			if self.cfg['agent-support']:
				self.prepareAgent(data={'shared': shared})
				if self.agentIsReady(timeout=30) is None: raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
				self.TIMER_ALIVE_AGT.start()
		if debug:
			self.__getKafkaClientLogger()

	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)	
		if self.cfg['agent-support'] :
			self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], self.cfg['agent']['type']) ) 
	
	def encapsule(self, *input_layers):
		"""
		Encapsule layers in template message
		"""

		if self.cfg['agent-support']:
			layer_agent= TestTemplatesLib.TemplateLayer('AGENT')
			layer_agent.addKey(name='name', data=self.cfg['agent']['name'] )
			layer_agent.addKey(name='type', data=self.cfg['agent']['type'] )

		tpl = TestTemplatesLib.TemplateMessage()

		if self.cfg['agent-support']:
			tpl.addLayer(layer=layer_agent)
		for layer in input_layers:
			tpl.addLayer(layer=layer)

		return tpl
	
	def onReset(self):
		"""
		Called automaticly on reset adapter
		"""
		# stop timer
		self.TIMER_ALIVE_AGT.stop()
		
		# cleanup remote agent
		self.resetAgent()

	def receivedNotifyFromAgent(self, data):
		"""
		Function to reimplement
		"""
#		self.info( 'Notify received from agent: %s' % data )
		if 'cmd' in data:
			if data['cmd'] == AGENT_INITIALIZED:
				tpl = TestTemplatesLib.TemplateMessage()
				layer = TestTemplatesLib.TemplateLayer('AGENT')
				layer.addKey("ready", True)
				layer.addKey(name='name', data=self.cfg['agent']['name'] )
				layer.addKey(name='type', data=self.cfg['agent']['type'] )
				tpl.addLayer(layer= layer)
				self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )
			elif data['cmd'] == "consumer_{0}".format(CONNECT):
				tpl = templates.kafka_ops(method=CONNECT)
				self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(CONSUME):
				record = data['result']
				consumer_rec = {"Partition": record.partition , "Offset": record.offset ,  "Key": record.key, "Value": record.value ,"Timestamp": record.timestamp ,"Timestamp_type": record.timestamp_type ,"Checksum": record.checksum, "Serialized_key_size":  record.serialized_key_size, "Serialized_value_size":  record.serialized_value_size}
				tpl = templates.kafka_ops(method=CONSUME, more=consumer_rec)
				self.logRecvEvent( shortEvt = "consumed", tplEvt =  self.encapsule( self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(ASSIGN):
				tpl = templates.kafka_ops(method=ASSIGN)		
				self.logRecvEvent( shortEvt = "assigned", tplEvt =  self.encapsule(self.consumerTpl ,tpl))			
			elif data['cmd'] == "consumer_{0}".format(ASSIGNMENT):
				topicpartitions = data['topicpartitions']
				tpl = templates.kafka_ops(method=ASSIGNMENT, topicpartitions=list(topicpartitions))				
				self.logRecvEvent( shortEvt = "resp assignment", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(COMMIT): 
				tpl = templates.kafka_ops(method=COMMIT)
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(COMMIT_ASYNC): 
				tpl = templates.kafka_ops(method=COMMIT_ASYNC,future=data['future'])
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(COMMITTED): 
				tpl = templates.kafka_ops(method=COMMITTED,offsets=data['offsets'])
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(PAUSE): 
				tpl = templates.kafka_ops(method=PAUSE)
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(PAUSED): 
				tpl = templates.kafka_ops(method=PAUSED, partitions=list(data['partitions'])	)
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(RESUME): 
				tpl = templates.kafka_ops(method=RESUME)
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))				
			elif data['cmd'] == "consumer_{0}".format(BEGINNING_OFFSETS): 
				tpl = templates.kafka_ops(method=BEGINNING_OFFSETS,offsets=data['offsets'])
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(END_OFFSETS):
				tpl = templates.kafka_ops(method=END_OFFSETS,partitions=data['partitions'])				
				self.logRecvEvent( shortEvt = "resp end_offsets", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(HIGHWATER):
				tpl = templates.kafka_ops(method=HIGHWATER,offset=data['offset'])								
				self.logRecvEvent( shortEvt = "resp highwater", tplEvt =  self.encapsule(self.consumerTpl ,tpl))				
			elif data['cmd'] == "consumer_{0}".format(OFFSETS_FOR_TIMES):
				tpl = templates.kafka_ops(method=OFFSETS_FOR_TIMES, offsets=data['offsets'])				
				self.logRecvEvent( shortEvt = "resp offsets_for_times", tplEvt =self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(PARTITIONS_FOR_TOPIC):
				partitionlist = list(data['partitions'])	
				tpl = templates.kafka_ops(method=PARTITIONS_FOR_TOPIC, partitions=partitionlist)								
				self.logRecvEvent( shortEvt = "resp partitions_for_topic", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(TOPICS):
				topiclist = list(data['topics'])	
				tpl = templates.kafka_ops(method=TOPICS, topics=topiclist)								
				self.logRecvEvent( shortEvt = "resp topics", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(POLL):
				tpl = templates.kafka_ops(method=POLL, records=data['records'])					
				self.logRecvEvent( shortEvt = "resp poll", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(POSITION):			
				tpl = templates.kafka_ops(method=POSITION, offset=data['offset'])							
				self.logRecvEvent( shortEvt = "resp position", tplEvt =  self.encapsule(self.consumerTpl ,tpl))		
			elif data['cmd'] == "consumer_{0}".format(SEEK):
				tpl = templates.kafka_ops(method=SEEK)					
				self.logRecvEvent( shortEvt = "resp seek", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(SEEK_TO_BEGINNING):
				tpl = templates.kafka_ops(method=SEEK_TO_BEGINNING)							
				self.logRecvEvent( shortEvt = "resp seek_to_beginning", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(SEEK_TO_END):
				tpl = templates.kafka_ops(method=SEEK_TO_END)			
				self.logRecvEvent( shortEvt = "resp seek_to_end", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			elif data['cmd'] == "consumer_{0}".format(SUBSCRIBE):
				tpl = templates.kafka_ops(method=SUBSCRIBE)																	
				self.logRecvEvent( shortEvt = "resp subscribe", tplEvt =  self.encapsule( self.consumerTpl ,tpl ))	
			elif data['cmd'] == "consumer_{0}".format(SUBSCRIPTION):	
				topiclist = list(data['topics'])
				tpl = templates.kafka_ops(method=SUBSCRIPTION, topics=topiclist)	
				self.logRecvEvent( shortEvt = "resp subscription", tplEvt=self.encapsule(self.consumerTpl ,tpl))	
			elif data['cmd'] == "consumer_{0}".format(UNSUBSCRIBE):
				tpl = templates.kafka_ops(method=UNSUBSCRIBE)				
				self.logRecvEvent( shortEvt = "resp unsubscribed", tplEvt =  self.encapsule( self.consumerTpl ,tpl ))	
			elif data['cmd'] == "consumer_{0}".format(CLOSE):
				tpl = templates.kafka_ops(method=CLOSE)
				self.logRecvEvent( shortEvt = "closed", tplEvt =  self.encapsule( self.consumerTpl ,tpl))			
		else:
			self.warning( 'Notify received from agent: %s' % data )


	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if "cmd" in data:
			if data['cmd'] in [ CONNECT, CLOSE,CONSUME,POLL,POSITION,HIGHWATER,SEEK,SEEK_TO_BEGINNING,SEEK_TO_END,PARTITIONS_FOR,END_OFFSETS,PARTITIONS_FOR_TOPIC,OFFSETS_FOR_TIMES,TOPICS,SUBSCRIBE,UNSUBSCRIBE,SUBSCRIPTION	]:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=data['err-msg'], method=data['cmd'] ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
			else:
				self.error("unknown command received: %s" % data["cmd"])
		else:
			self.error( 'Generic error: %s' % data )
	def receivedDataFromAgent(self, data):
		"""
		Function to reimplement
		"""
		self.warning( 'Data received from agent: %s' % data )
		
	def prepareAgent(self, data):
		"""
		Prepare agent
		"""
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def initAgent(self, data):
		"""
		Init agent
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	def resetAgent(self):
		"""
		Reset agent
		"""
		self.parent.sendResetToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')
		
	def aliveAgent(self):
		"""
		Keep alive agent
		"""
		self.parent.sendAliveToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData='')
		self.TIMER_ALIVE_AGT.restart()
		
	@doc_public
	def sendInitToAgent(self, data):
		"""
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	@doc_public
	def sendNotifyToAgent(self, data):
		"""
		"""
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
		
	@doc_public
	def sendResetToAgent(self, data):
		"""
		"""
		self.parent.sendResetToAgent(adapterId=self.getAdapterId(), agentName=self.cfg['agent-name'], agentData=data)
	def agentIsReady(self, timeout=1.0):
		"""
		Waits to receive "agent ready" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float	
		
		@return: an event matching with the template or None otherwise
		@rtype: templatemessage		
		"""
		tpl = TestTemplatesLib.TemplateMessage()
		layer = TestTemplatesLib.TemplateLayer('AGENT')
		layer.addKey("ready", True)
		layer.addKey(name='name', data=self.cfg['agent']['name'] )
		layer.addKey(name='type', data=self.cfg['agent']['type'] )
		tpl.addLayer(layer= layer)
		evt = self.received( expected = tpl, timeout = timeout )
		return evt
				
	def __getKafkaClientLogger(self):
		logger = logging.getLogger('kafka')
		logger.addHandler(logging.StreamHandler(sys.stdout))
		logger.setLevel(logging.DEBUG)

	def connect(self, *topics,**kargs ):
		"""
		Instantiate the KafkaConsumer

		@param kargs: keyword arguments from KafkaProducer class: 
		@type kargs: keyword 
		
		"""
		if 'bootstrap_servers' in kargs:
			bootstrap_servers = kargs.pop('bootstrap_servers')
		else:
			bootstrap_servers=self.bootstrap_servers
		self.topic=topics
		# Log start connexion  event
		self.consumerTpl = templates.kafka_connect(api=CONSUMER,bootstrap_servers=bootstrap_servers, **kargs)
		tpl = templates.kafka_ops(method=CONNECT)	
		self.logSentEvent( shortEvt = "consumer connection", tplEvt = self.encapsule(self.consumerTpl,tpl))

		# Agent mode
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(CONNECT),
							'topics': topics,
							'bootstrap_servers': bootstrap_servers,
							'kargs': kargs
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:			
				self.consumer = KafkaConsumer(*topics, bootstrap_servers=bootstrap_servers, **kargs)		
				self.logRecvEvent( shortEvt = "consumer connected", tplEvt = self.encapsule(self.consumerTpl,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=CONNECT ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	def close(self, autocommit=True):
		tpl = templates.kafka_ops(method=DISCONNECT,autocommit=autocommit)
		self.logSentEvent( shortEvt = "req close", tplEvt = self.encapsule(self.consumerTpl ,tpl) )

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(DISCONNECT),
							'autocommit': autocommit
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.close(autocommit)
				tpl = templates.kafka_ops(method=DISCONNECT,autocommit=autocommit)
				self.logRecvEvent( shortEvt = "closed", tplEvt =self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=DISCONNECT ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
	def consume(self):
		"""
		Consum message of assigned/subscribed topic.
		"""		
		tpl = templates.kafka_ops(method=CONSUME, topic=self.topic)
		self.logSentEvent( shortEvt = "req consume", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(CONSUME)
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				for record in self.consumer :
					consumer_rec = {"Partition": record.partition , "Offset": record.offset ,  "Key": record.key, "Value": record.value ,"Timestamp": record.timestamp ,"Timestamp_type": record.timestamp_type ,"Checksum": record.checksum, "Serialized_key_size":  record.serialized_key_size, "Serialized_value_size":  record.serialized_value_size}
					tpl = templates.kafka_ops(method=CONSUME, more=consumer_rec)			
					self.logRecvEvent( shortEvt = "resp consume", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=CONSUME ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		
	def assign(self, partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=ASSIGN, partitions=partitions)
		self.logSentEvent( shortEvt = "req assign", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(ASSIGN),
							'partitions': partitions
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.assign(partitions)
				tpl = templates.kafka_ops(method=ASSIGN, partitions=partitions)																					
				self.logRecvEvent( shortEvt = "resp assign", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=ASSIGN))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

		
	def assignment(self):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=ASSIGNMENT)
		self.logSentEvent( shortEvt = "req assignment", tplEvt = self.encapsule(self.consumerTpl ,tpl) )
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(ASSIGNMENT)
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				topicpartitions=self.consumer.assignment()
				tpl = templates.kafka_ops(method=ASSIGNMENT, topicpartitions=topicpartitions)				
				self.logRecvEvent( shortEvt = "resp assignment", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=ASSIGNMENT))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
	def beginning_offsets(self, partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=BEGINNING_OFFSETS, partitions=partitions)
		self.logSentEvent( shortEvt = "req beginning_offsets", tplEvt = self.encapsule(self.consumerTpl ,tpl))	

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(BEGINNING_OFFSETS),
							'partitions': partitions
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				topicpartitions=self.consumer.beginning_offsets(partitions)
				tpl = templates.kafka_ops(method=BEGINNING_OFFSETS, offsets=topicpartitions)
				self.logRecvEvent( shortEvt = "resp beginning_offsets", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=BEGINNING_OFFSETS))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				

	def commit(self, offsets=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=COMMIT, offsets=offsets)
		self.logSentEvent( shortEvt = "req commit", tplEvt = self.encapsule(self.consumerTpl ,tpl))	

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(COMMIT),
							'offsets': offsets
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.commit(offsets=offsets)
				tpl = templates.kafka_ops(method=COMMIT)
				self.logRecvEvent( shortEvt = "resp commit", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=COMMIT))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
	def commit_async(self, offsets=None, callback=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=COMMIT_ASYNC, offsets=offsets,callback=callback)
		self.logSentEvent( shortEvt = "req commit_async", tplEvt = self.encapsule(self.consumerTpl ,tpl))	

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(COMMIT_ASYNC),
							'offsets': offsets,
							'callback': callback
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				future=self.consumer.commit_async(offsets=offsets, callback=callback)
				tpl = templates.kafka_ops(method=COMMIT_ASYNC, future=future)
				self.logRecvEvent( shortEvt = "resp commit_async", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=COMMIT_ASYNC))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
	def committed(self, topicpartition):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=COMMITTED, topicpartition=topicpartition)
		self.logSentEvent( shortEvt = "req committed", tplEvt = self.encapsule(self.consumerTpl ,tpl))	
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(COMMITTED),
							'topicpartition': topicpartition
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				offsets=self.consumer.committed(topicpartition)
				tpl = templates.kafka_ops(method=COMMITTED,offsets=offsets)
				self.logRecvEvent( shortEvt = "resp committed", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=COMMITTED))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

		
	def end_offsets(self, *topicpartitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=END_OFFSETS, partitions=topicpartitions)
		self.logSentEvent( shortEvt = "req end_offsets", tplEvt = self.encapsule(self.consumerTpl ,tpl))	
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(END_OFFSETS),
							'partitions': topicpartitions
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				partitions=self.consumer.end_offsets(topicpartitions)
				tpl = templates.kafka_ops(method=END_OFFSETS,partitions=partitions)				
				self.logRecvEvent( shortEvt = "resp end_offsets", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=END_OFFSETS))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

		
	def highwater(self, topicpartition):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=HIGHWATER, partition=topicpartition)
		self.logSentEvent( shortEvt = "req highwater", tplEvt = self.encapsule(self.consumerTpl ,tpl))	
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(HIGHWATER),
							'partition': topicpartition
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				offset=self.consumer.highwater(topicpartition)
				tpl = templates.kafka_ops(method=HIGHWATER,offset=offset)								
				self.logRecvEvent( shortEvt = "resp highwater", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=HIGHWATER ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	
	def offsets_for_times(self, timestamps):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=OFFSETS_FOR_TIMES,timestamps=timestamps)
		self.logSentEvent( shortEvt = "req offsets_for_times", tplEvt = self.encapsule(self.consumerTpl ,tpl) )
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(OFFSETS_FOR_TIMES),
							'timestamps': timestamps
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				offsets=self.consumer.offsets_for_times(timestamps)
				tpl = templates.kafka_ops(method=OFFSETS_FOR_TIMES, offsets=offsets)				
				self.logRecvEvent( shortEvt = "resp offsets_for_times", tplEvt =self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=OFFSETS_FOR_TIMES ))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
		
	def partitions_for_topic(self, topic):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=PARTITIONS_FOR_TOPIC,topic=topic)
		self.logSentEvent( shortEvt = "req partitions_for_topic", tplEvt = self.encapsule(self.consumerTpl ,tpl ))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(PARTITIONS_FOR_TOPIC),
							'topic': topic
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				partitions=self.consumer. partitions_for_topic(topic)
				partitionlist = list(partitions)	
				tpl = templates.kafka_ops(method=PARTITIONS_FOR_TOPIC, partitions=partitionlist)								
				self.logRecvEvent( shortEvt = "resp partitions_for_topic", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=PARTITIONS_FOR_TOPIC ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
	def pause(self, partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=PAUSE,partitions=partitions)
		self.logSentEvent( shortEvt = "req pause", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(PAUSE),
							'partitions': partitions				
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.pause(partitions)
				tpl = templates.kafka_ops(method=PAUSE)							
				self.logRecvEvent( shortEvt = "resp pause", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=PAUSE ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		
	def paused(self):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=PAUSED)
		self.logSentEvent( shortEvt = "req paused", tplEvt = self.encapsule(self.consumerTpl ,tpl ))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(PAUSED) 
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				partitions=self.consumer.paused()
				partitionslist = list(partitions)
				tpl = templates.kafka_ops(method=PAUSED, partitions=partitionslist)	
				self.logRecvEvent( shortEvt = "resp paused", tplEvt=self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, cmd=PAUSED ))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
	def poll(self, timeout_ms=None, max_records=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=POLL,timeout_ms=timeout_ms,max_records=max_records)	
		self.logSentEvent( shortEvt = "req poll", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(POLL),
							'max_records': max_records,
							'timeout_ms': timeout_ms
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				records=self.consumer.poll(timeout_ms=timeout_ms, max_records=max_records)
				tpl = templates.kafka_ops(method=POLL, records=records)					
				self.logRecvEvent( shortEvt = "resp poll", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=POLL ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
	def position(self, topicpartition):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=POSITION,topicpartition=topicpartition)
		self.logSentEvent( shortEvt = "req position", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd':  "consumer_{0}".format(POSITION),
							'topicpartition': topicpartition
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				offset=self.consumer.position(topicpartition)
				tpl = templates.kafka_ops(method=POSITION, offset=offset)							
				self.logRecvEvent( shortEvt = "resp position", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=POSITION))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	def resume(self,partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=RESUME,partitions=partitions)
		self.logSentEvent( shortEvt = "req resume", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(RESUME),
							'partitions': partitions				
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.resume(partitions)
				tpl = templates.kafka_ops(method=RESUME)							
				self.logRecvEvent( shortEvt = "resp resume", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=RESUME ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		

		
	def seek(self,partition, offset):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=SEEK,partition=partition,  offset=offset)
		self.logSentEvent( shortEvt = "req seek", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(SEEK),
							'partition': partition,
							'offset': offset							
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.seek(partition, offset)
				tpl = templates.kafka_ops(method=SEEK)					
				self.logRecvEvent( shortEvt = "resp seek", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=OFFSETS_FOR_TIMES ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	
	def seek_to_beginning(self,*partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=SEEK_TO_BEGINNING,partitions=partitions)
		self.logSentEvent( shortEvt = "req seek_to_beginning", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(SEEK_TO_BEGINNING),
							'partitions': partitions				
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.seek_to_beginning(*partitions)
				tpl = templates.kafka_ops(method=SEEK_TO_BEGINNING)							
				self.logRecvEvent( shortEvt = "resp seek_to_beginning", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=SEEK_TO_BEGINNING ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		
	def seek_to_end(self,*partitions):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=SEEK_TO_END,partitions=partitions)
		self.logSentEvent( shortEvt = "req seek_to_end", tplEvt = self.encapsule(self.consumerTpl ,tpl))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(SEEK_TO_END),
							'partitions': partitions				
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.seek_to_end(*partitions)
				tpl = templates.kafka_ops(method=SEEK_TO_END)			
				self.logRecvEvent( shortEvt = "resp seek_to_end", tplEvt =  self.encapsule(self.consumerTpl ,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=SEEK_TO_END ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		
	def subscribe(self,topics=(), pattern=None, listener=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=SUBSCRIBE,topics=topics, pattern=pattern, listener=listener)
		self.logSentEvent( shortEvt = "req subscribe", tplEvt = self.encapsule(self.consumerTpl ,tpl) )
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(SUBSCRIBE),
							'topics': topics,
							'pattern': pattern,
							'listener': listener
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.subscribe(topics=topics, pattern=pattern, listener=listener)
				tpl = templates.kafka_ops(method=SUBSCRIBE,topics=topics, pattern=pattern, listener=listener)																	
				self.logRecvEvent( shortEvt = "resp subscribe", tplEvt =  self.encapsule( self.consumerTpl ,tpl ))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=SUBSCRIBE ))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

		
	def subscription(self):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=SUBSCRIPTION)
		self.logSentEvent( shortEvt = "req subscription", tplEvt = self.encapsule(self.consumerTpl ,tpl ))
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(SUBSCRIPTION) 
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				topics=self.consumer.subscription()
#				topiclist = dict(enumerate(list(topics)))
				topiclist = list(topics)
				tpl = templates.kafka_ops(method=SUBSCRIPTION, topics=topiclist)	
				self.logRecvEvent( shortEvt = "resp subscription", tplEvt=self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, cmd=SUBSCRIPTION ))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		
		
	def topics(self):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=TOPICS)
		self.logSentEvent( shortEvt = "req topics", tplEvt = self.encapsule(self.consumerTpl ,tpl) )
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(TOPICS)
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				topics=self.consumer.topics()
				topiclist = list(topics)
				tpl = templates.kafka_ops(method=TOPICS, topics=topiclist)						
				self.logRecvEvent( shortEvt = "resp topics", tplEvt =  self.encapsule(self.consumerTpl ,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.consumerTpl ,templates.response_err(msg=e, method=TOPICS))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )


	def unsubscribe(self):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=UNSUBSCRIBE)
		self.logSentEvent( shortEvt = "req unsubscribe", tplEvt = self.encapsule(self.consumerTpl ,tpl) )
	
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "consumer_{0}".format(UNSUBSCRIBE)
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.consumer.unsubscribe()
				tpl = templates.kafka_ops(method=UNSUBSCRIBE)				
				self.logRecvEvent( shortEvt = "resp unsubscribed", tplEvt =  self.encapsule( self.consumerTpl ,tpl ))	
			except KafkaError  as e:
				tpl = self.encapsule( self.consumerTpl ,templates.response_err(msg=e, method=UNSUBSCRIBE ))
				tpl.addRaw( str(e) )
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
		

	def isConnected(self, timeout=2):
		"""
		Wait to receive response from "connect" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		# construct the expected template
		expected = templates.kafka_ops(method=CONNECT)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected), timeout=timeout )
		return evt	


	def isPosition(self, timeout=2,offset=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		if offset == None:
			offset= { "offset":TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=POSITION, more=offset)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isPartitions_for_topic(self, timeout=2,partitions=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		# construct the expected template
		if partitions == None:
			partitions= { "partitions":TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=PARTITIONS_FOR_TOPIC, more=partitions)			
		# try to match the template 
		evt = self.received( expected=self.encapsule(self.consumerTpl , expected ), timeout=timeout )
		return evt	


	def isConsumed(self, timeout=2,record=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if record == None:
			record = {"Partition": TestOperatorsLib.Any() , "Offset": TestOperatorsLib.Any() ,  "Key": TestOperatorsLib.Any(), "Value": TestOperatorsLib.Any() ,"Timestamp": TestOperatorsLib.Any() ,"Timestamp_type": TestOperatorsLib.Any() ,"Checksum":  TestOperatorsLib.Any(), "Serialized_key_size":  TestOperatorsLib.Any(), "Serialized_value_size": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=CONSUME, more=record)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isTopics(self, timeout=2, topics=None):
		"""
		Wait to receive "connected" event until the end of the timeout
		
		@param timeout: time max to wait to receive event in second (default=1s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if topics == None:
			topics= { "topics":TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=TOPICS, more=topics)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isSubscribe(self, timeout=2):
		"""
		Wait to receive response from "subscribe" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=SUBSCRIBE)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt		
		
	def isSubscription(self, timeout=2,topics=None):
		"""
		Wait to receive response from "subscription" request and match returned TopicPartitions  until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param offset: Optional dict that we expect to be assigned to consumer 
		@type offset: list of of TopicPartitions
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if topics == None:
			topics= { "topics":TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=SUBSCRIPTION, more=topics)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isUnsubscribe(self, timeout=2):
		"""
		Wait to receive response from "unsubscribe" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=UNSUBSCRIBE)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
		
	def isClosed(self, timeout=2):
		"""
		Wait to receive response from "closed" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=CLOSE)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isOffsets_for_times(self, timeout=2, offsets=None):
		"""
		Wait to receive response from "offsets_for_times" request and match returned TopicPartitions  until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param offset: Optional dict that we expect to be assigned to consumer 
		@type offset: dict of of TopicPartitions/OffsetAndTimestamp
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if offsets == None:
			offsets= {"offsets": TestOperatorsLib.Any() }
		expected = templates.kafka_ops(method=OFFSETS_FOR_TIMES, more=offsets)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isAssigned(self, timeout=2):
		"""
		Wait to receive response from "assigned" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=ASSIGN)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isAssignment(self, timeout=2,topicpartitions=None):
		"""
		Wait to receive response from "assignement" request and match returned TopicPartitions  until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param offset: Optional partitions that we expect to be assigned to consumer 
		@type offset: list of TopicPartitions 
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if topicpartitions == None:
			topicpartitions= { "topicpartitions": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=ASSIGNMENT, more=topicpartitions)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isSeek(self, timeout=2):
		"""
		Wait to receive response from "seek" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=SEEK)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isSeek_to_beginning(self, timeout=2):
		"""
		Wait to receive response from "seek_to_beginning" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		expected = templates.kafka_ops(method=SEEK_TO_BEGINNING)			
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isSeek_to_end(self, timeout=2):
		"""
		Wait to receive response from "seek_to_end" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
			
		expected = templates.kafka_ops(method=SEEK_TO_END)			
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isHighwater(self, timeout=2, offset=None):
		"""
		Wait to receive response from "highwater" request and match returned offset until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param offset: Optional partitions that we expect to be paused 
		@type offset: Int
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if offset == None:
			offset= { "offset": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=HIGHWATER, more=offset)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isEnd_offsets(self, timeout=2, partitions=None):
		"""
		Wait to receive response from "end_offset" request and match returned TopicPartiton with offset until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param partitions: Optional TopicPartition object with expect last topic offset 
		@type partitions: TopicPartition
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if partitions == None:
			partitions= { "partitions": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=END_OFFSETS, more=partitions)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	


	def isPoll(self, timeout=2, records=None):
		"""
		Wait to receive response from "poll" request and match returned Records with offset until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param records: Optional records  that we expect to fetch 
		@type records: dict of topic/records
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if records == None:
			records= { "records": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=POLL, more=records)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isCommit(self, timeout=2):
		"""
		Wait to receive response from "commit" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=COMMIT)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isCommit_async(self, timeout=2):
		"""
		Wait to receive response from "commit_async" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=COMMIT_ASYNC)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isCommitted(self, timeout=2, offsets=None):
		"""
		Wait to receive response from "comitted" request and match returned TopicPartiton with offset until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param offsets: Optional offset for partitions that we expect to be paused 
		@type offsets: TopicPartition
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if offsets == None:
			offsets= { "offsets": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=COMMITTED, more=offsets)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	
		
	def isBeginning_offsets(self, timeout=2, topicpartitions=None):
		"""
		Wait to receive response from "beginning_offsets" request and match returned list of TopicPartiton with offset until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param topicpartitions: Optional partitions/offset list that we expect to be returned 
		@type topicpartitions: list of TopicPartitions	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if topicpartitions == None:
			topicpartitions= { "offsets": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=BEGINNING_OFFSETS, more=topicpartitions)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt	

	def isPause(self, timeout=2):
		"""
		Wait to receive response from "pause" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=PAUSE)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt		
		
	def isPaused(self, timeout=2, topicpartitions=None):
		"""
		Wait to receive response from "pause" request and match returned partition until the end of the timeout.
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		@param topicpartitions: Optional partitions that we expect to be paused 
		@type timeout: list of TopicPartitions	
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		if topicpartitions == None:
			topicpartitions= { "partitions": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=PAUSED, more=topicpartitions)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt		
		
	def isResume(self, timeout=2):
		"""
		Wait to receive response from "resume" request until the end of the timeout
		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		if not ( isinstance(timeout, int) or isinstance(timeout, float) ) or isinstance(timeout,bool): 
			raise TestAdapterLib.ValueException(TestAdapterLib.caller(), "timeout argument is not a float or integer (%s)" % type(timeout) )
		
		expected = templates.kafka_ops(method=RESUME)		
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.consumerTpl ,expected ), timeout=timeout )
		return evt		