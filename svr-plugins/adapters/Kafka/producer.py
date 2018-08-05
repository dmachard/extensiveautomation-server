#!/usr/bin/env python
# -*- coding=utf-8 -*-

# ------------------------------------------------------------------
# Copyright (c) 2018 Jordane Fillatre
# This file is part of the extensive automation project
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301 USA
# -------------------------------------------------------------------

import TestExecutorLib.TestValidatorsLib as TestValidatorsLib
import TestExecutorLib.TestTemplatesLib as TestTemplatesLib
import TestExecutorLib.TestOperatorsLib as TestOperatorsLib
import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib
from TestExecutorLib.TestExecutorLib import doc_public

import sys
import copy
import templates

from Libs.PyXmlDict import Xml2Dict
from Libs.PyXmlDict import Dict2Xml

from kafka import KafkaProducer
from kafka.errors import KafkaError
import logging

__NAME__="""KAFKA"""
AGENT_INITIALIZED = "AGENT_INITIALIZED"
AGENT_TYPE_EXPECTED='kafka'
PRODUCER="producer"
SEND = "send"
CONNECT = "connect"
FLUSH="flush" 
CLOSE="close" 
PARTITIONS_FOR="partitions_for"


class ProducerClient(TestAdapterLib.Adapter):
	@doc_public
	def __init__ (self, parent, name=None, bootstrap_servers=None, 
											debug=False, agentSupport=False, agent=None, 
											shared=False, verbose=True, 
											logEventSent=True, logEventReceived=True):
		"""
		KAFKA Producer client Adapter. Mapping of kafka-python KafkaProducer
		
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
		TestAdapterLib.Adapter.__init__(self, name = __NAME__, parent = parent, 
																									debug=debug, realname=name,
																									agentSupport=agentSupport, 
																									agent=agent, shared=shared,
																									caller=TestAdapterLib.caller(),
																									agentType=AGENT_TYPE_EXPECTED)
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
		
		self.TIMER_ALIVE_AGT = TestAdapterLib.Timer(parent=self, duration=20, 
																																			name="keepalive-agent", 
																																			callback=self.aliveAgent,
																																			logEvent=False, enabled=True)
		self.__checkConfig()
		
		# initialize the agent with no data
		if agent is not None:
			if self.cfg['agent-support']:
				self.prepareAgent(data={'shared': shared})
				if self.agentIsReady(timeout=30) is None: 
					raise Exception("Agent %s is not ready" % self.cfg['agent-name'] )
				self.TIMER_ALIVE_AGT.start()

		self.bootstrap_servers = bootstrap_servers

		if debug:
			self.__getKafkaClientLogger()

	def __checkConfig(self):
		"""
		"""
		self.debug("config: %s" % self.cfg)		
		self.warning('Agent used Name=%s Type=%s' % (self.cfg['agent']['name'], 
																																										self.cfg['agent']['type']) ) 
	
	
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
		if 'cmd' in data:
			if data['cmd'] == AGENT_INITIALIZED:
				tpl = TestTemplatesLib.TemplateMessage()
				layer = TestTemplatesLib.TemplateLayer('AGENT')
				layer.addKey("ready", True)
				layer.addKey(name='name', data=self.cfg['agent']['name'] )
				layer.addKey(name='type', data=self.cfg['agent']['type'] )
				tpl.addLayer(layer= layer)
				self.logRecvEvent( shortEvt = "Agent Is Ready" , tplEvt = tpl )

			elif data['cmd'] == "producer_{0}".format(CONNECT):
				self.__kafka_connected = True
				tpl = templates.kafka_ops(method=CONNECT,bootstrap_servers=self.bootstrap_servers)
				self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(self.producerTpl ,tpl))

			elif data['cmd'] == "producer_{0}".format(SEND):
				record_metadata = data['result']
				self.__kafka_send = True
				rec = { "Topic":record_metadata[0], 
										"Partition": record_metadata[1] , 
										"Offset":record_metadata[3] , 
										"Timestamp": record_metadata[4] ,
										"Checksum": record_metadata[5], 
										"Serialized_key_size": record_metadata[6], 
										"Serialized_value_size": record_metadata[7]}
				tpl = templates.kafka_ops(method=SEND, more=rec)
				self.logRecvEvent( shortEvt = "sended", tplEvt =  self.encapsule(self.producerTpl ,tpl))

			elif data['cmd'] =="producer_{0}".format(FLUSH) :
				tpl = templates.kafka_ops(method=FLUSH)
				self.logRecvEvent( shortEvt = "flushed", tplEvt =  self.encapsule(self.producerTpl ,tpl))	

			elif data['cmd'] =="producer_{0}".format(PARTITIONS_FOR) :
				partitions = data['result']
				tpl = templates.kafka_ops(method=PARTITIONS_FOR, partitions=partitions)
				self.logRecvEvent( shortEvt = "partitions_for", tplEvt =  self.encapsule(self.producerTpl ,tpl))				
			elif data['cmd'] == "producer_{0}".format(CLOSE):
				tpl = templates.kafka_ops(method=CLOSE)
				self.logRecvEvent( shortEvt = "closed", tplEvt =  self.encapsule(self.producerTpl ,tpl))			
		else:
			self.warning( 'Notify received from agent: %s' % data )

	def receivedErrorFromAgent(self, data):
		"""
		Function to reimplement
		"""
		if "cmd" in data:
			if data['cmd'] in [ CONNECT, CLOSE, SEND, FLUSH,PARTITIONS_FOR	]:
				tpl = self.encapsule(self.producerTpl, templates.response_err(msg=data['err-msg'], method=data['cmd'] ))
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
		self.parent.sendReadyToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData=data)
																										
	def initAgent(self, data):
		"""
		Init agent
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), 
																						agentName=self.cfg['agent-name'], 
																						agentData=data)
																								
	def resetAgent(self):
		"""
		Reset agent
		"""
		self.parent.sendResetToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData='')
																										
	def aliveAgent(self):
		"""
		Keep alive agent
		"""
		self.parent.sendAliveToAgent(adapterId=self.getAdapterId(), 
																							agentName=self.cfg['agent-name'], 
																							agentData='')
		self.TIMER_ALIVE_AGT.restart()

	def sendInitToAgent(self, data):
		"""
		"""
		self.parent.sendInitToAgent(adapterId=self.getAdapterId(), 
																						agentName=self.cfg['agent-name'], 
																						agentData=data)
																								
	def sendNotifyToAgent(self, data):
		"""
		"""
		self.parent.sendNotifyToAgent(adapterId=self.getAdapterId(), 
																								agentName=self.cfg['agent-name'], 
																								agentData=data)

	def sendResetToAgent(self, data):
		"""
		"""
		self.parent.sendResetToAgent(adapterId=self.getAdapterId(), 
																							agentName=self.cfg['agent-name'], 
																							agentData=data)

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

	@doc_public
	def connect(self, **kargs ):
		"""
		Instantiate the KafkaProducer and Fetch Kafka Cluster Metadata

		@param kargs: keyword arguments from KafkaProducer class: 
		@type kargs: keyword 
		
		"""
		if 'bootstrap_servers' in kargs:
			bootstrap_servers = kargs.pop('bootstrap_servers')
		else:
			bootstrap_servers=self.bootstrap_servers

		# Log start connexion  event
		self.producerTpl = templates.kafka_connect(api=PRODUCER,bootstrap_servers=bootstrap_servers, **kargs)
		tpl = templates.kafka_ops(method=CONNECT,bootstrap_servers=bootstrap_servers, **kargs)
		self.logSentEvent( shortEvt = "connection", tplEvt = self.encapsule(self.producerTpl,tpl))

		self.__kafka_connected = False

		# Agent mode
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "producer_{0}".format(CONNECT),
							'bootstrap_servers': bootstrap_servers,
							'kargs': kargs
						}
			self.sendNotifyToAgent(data=remote_cfg)
				
		else:
			try:
				self.producer = KafkaProducer(bootstrap_servers=bootstrap_servers, **kargs )
				tpl = templates.kafka_ops(method=CONNECT,bootstrap_servers=bootstrap_servers, **kargs)
				self.logRecvEvent( shortEvt = "connected", tplEvt = self.encapsule(self.producerTpl,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.producerTpl,  templates.response_err(msg=e, method=CONNECT ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	@doc_public			
	def send(self, topic, **kargs):
		"""
		Publish a message to a topic.

		@topic (str): topic where the message will be published    
		
		@value (optional): message value as bytes.
		
		@partition (int, optional): optionally specify a partition. If not set, the partition will be selected using the configured 'partitioner'.
		
		@key (optional): a key to associate with the message. Can be used to determine which partition to send the message to. 
		
		@timestamp_ms (int, optional): epoch milliseconds (from Jan 1 1970 UTC) to use as the message timestamp. Defaults to current time.
		"""		
		tpl = templates.kafka_ops(method=SEND, **kargs)
		self.logSentEvent( shortEvt = "req send", tplEvt = self.encapsule(self.producerTpl ,tpl))

		# Timeout for record metadata retreving
		if "timeout" in kargs:
			timeout = kargs.pop("timeout")
		else:
			timeout=2
		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "producer_{0}".format(SEND),
							'topic': topic,
							'timeout': timeout,
							'kargs': kargs
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				future = self.producer.send(topic,**kargs)
				record_metadata=future.get(timeout=timeout)

				rec = { "Topic":record_metadata[0], 
										"Partition": record_metadata[1] , 
										"Offset":record_metadata[3] , 
										"Timestamp": record_metadata[4] ,
										"Checksum": record_metadata[5], 
										"Serialized_key_size": record_metadata[6], 
										"Serialized_value_size": record_metadata[7]}
				tpl = templates.kafka_ops(method=SEND, more=rec)
				self.logRecvEvent( shortEvt = "resp send", tplEvt =  self.encapsule(self.producerTpl,tpl))
			except KafkaError  as e:
				tpl = self.encapsule(self.producerTpl,  templates.response_err(msg=e, method=SEND ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	@doc_public	
	def partitions_for(self, topic):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=PARTITIONS_FOR, topic=topic)
		self.logSentEvent( shortEvt = "req partitions_for", tplEvt = self.encapsule(self.producerTpl ,tpl))

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "producer_{0}".format(PARTITIONS_FOR),
							'topic': topic
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				partitions = self.producer.partitions_for(topic)	
				tpl = templates.kafka_ops(method=PARTITIONS_FOR,topic=topic, partitions=partitions)
				self.logRecvEvent( shortEvt = "resp partitions_for", tplEvt =  self.encapsule(self.producerTpl,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.producerTpl,  templates.response_err(msg=e, method=PARTITIONS_FOR ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )				

	@doc_public
	def flush(self, timeout=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=FLUSH, timeout=timeout)
		self.logSentEvent( shortEvt = "req flush", tplEvt = self.encapsule(self.producerTpl,tpl))	

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "producer_{0}".format(FLUSH),
							'timeout': timeout
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.producer.flush(timeout)	
				tpl = templates.kafka_ops(method=FLUSH)
				self.logRecvEvent( shortEvt = "resp flush", tplEvt =  self.encapsule(self.producerTpl,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.producerTpl,  templates.response_err(msg=e, method=FLUSH ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )

	@doc_public
	def close(self, timeout=None):
		"""
		All fonction documentation available on http://kafka-python.readthedocs.io.
		"""		
		tpl = templates.kafka_ops(method=CLOSE, timeout=timeout)
		self.logSentEvent( shortEvt = "req close", tplEvt = self.encapsule(self.producerTpl,tpl))	

		if self.cfg['agent-support']:
			remote_cfg = {
							'cmd': "producer_{0}".format(CLOSE),
							'timeout': timeout
						}
			self.sendNotifyToAgent(data=remote_cfg)
		else:
			try:
				self.producer.close(timeout=timeout)
				tpl = templates.kafka_ops(method=CLOSE,timeout=timeout)
				self.logRecvEvent( shortEvt = "closed", tplEvt =  self.encapsule(self.producerTpl,tpl))	
			except KafkaError  as e:
				tpl = self.encapsule(self.producerTpl,  templates.response_err(msg=e, method=CLOSE ))
				self.logRecvEvent( shortEvt = "response error", tplEvt = tpl )
				
	@doc_public
	def isSend(self, timeout=2, record=None):
		"""
		Wait to receive response from "send" request and match returned RecordMetadata  until the end of the timeout.

		@param timeout: time max to wait to receive event in second (default=2s)
		
		@type timeout: float	
		
		@param offset: Optional RecordMetadata that we expect to be assigned to consumer 
		
		@type offset:  RecordMetadata
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		if record == None:
			record = { "Topic":TestOperatorsLib.Any(), 
											"Partition": TestOperatorsLib.Any(), 
											"Offset":TestOperatorsLib.Any() , 
											"Timestamp":TestOperatorsLib.Any() ,
											"Checksum": TestOperatorsLib.Any(), 
											"Serialized_key_size":TestOperatorsLib.Any(),
											"Serialized_value_size": TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=SEND, more=record)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.producerTpl ,expected ), timeout=timeout )
		return evt

	@doc_public		
	def isConnect(self, timeout=2):
		"""
		Wait to receive response from "connect" request until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = templates.kafka_ops(method=CONNECT, bootstrap_servers=self.bootstrap_servers)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.producerTpl ,expected), timeout=timeout )
		return evt	

	@doc_public
	def isFlush(self, timeout=2):
		"""
		Wait to receive response from "flush" request until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = templates.kafka_ops(method=FLUSH)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.producerTpl ,expected), timeout=timeout )
		return evt		
	
	@doc_public    
	def isClose(self, timeout=2):
		"""
		Wait to receive response from "close" request until the end of the timeout

		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)
		
		# construct the expected template
		expected = templates.kafka_ops(method=CLOSE)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.producerTpl ,expected), timeout=timeout )
		return evt		
		
	@doc_public
	def isPartitions_for(self, timeout=2,partitions=None):
		"""
		Wait to receive response from "partitions_for" request and match returned Topics until the end of the timeout.

		@param timeout: time max to wait to receive event in second (default=2s)
		@type timeout: float		

		@param offset: Optional list that we expect to be view by producer 
		@type offset: list of of Topics
		"""
		TestAdapterLib.check_timeout(caller=TestAdapterLib.caller(), timeout=timeout)

		if partitions == None:
			partitions= { "partitions":TestOperatorsLib.Any()}
		expected = templates.kafka_ops(method=PARTITIONS_FOR,more=partitions)
		# try to match the template 
		evt = self.received( expected=self.encapsule( self.producerTpl ,expected), timeout=timeout )
		return evt	