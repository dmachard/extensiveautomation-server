#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
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

import Core.GenericTool as GenericTool
import Libs.Settings as Settings
import Libs.FifoQueue as FifoQueue

import sys
from kafka import KafkaProducer,KafkaConsumer
from kafka.errors import KafkaError
import threading

try:
    xrange
except NameError: # support python3
    xrange = range

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    

__TOOL_TYPE__ = GenericTool.TOOL_AGENT
__WITH_IDE__ = False  
__APP_PATH__ = ""
__TYPE__="""kafka"""
__RESUME__="""Just a dummy agent. Use only for development.
Can be used on Linux or Windows."""

__DESCRIPTION__="""Example, just a dummy agent.
This agent enables to receive or send data from or to the test server.

Events messages:
    Agent->Server
        * Error(data)
        * Notify(data)
        * Data(data)

    Server->Agent
        * Init(data)
        * Notify(data)
        * Reset(data)

The data argument can contains anything, but a dictionary is prefered.

Targetted operating system: Windows, Linux"""

def initialize (controllerIp, controllerPort, toolName, toolDesc, 
                defaultTool, supportProxy, proxyIp, proxyPort, sslSupport):
    """
    Wrapper to initialize the object agent
    """
    return Kafka( controllerIp, controllerPort, toolName, toolDesc, 
                  defaultTool, supportProxy, proxyIp, proxyPort, sslSupport )
    

class Kafka(GenericTool.Tool):
    def __init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, supportProxy=0,
                        proxyIp=None, proxyPort=None, sslSupport=True):
        """
        Kafka agent

        @param controllerIp: controller ip/host
        @type controllerIp: string

        @param controllerPort: controller port
        @type controllerPort: integer

        @param toolName: agent name
        @type toolName: string

        @param toolDesc: agent description
        @type toolDesc: string

        @param defaultTool: True if the agent is started by the server, False otherwise
        @type defaultTool: boolean
        """
        GenericTool.Tool.__init__(self, controllerIp, controllerPort, toolName, toolDesc, defaultTool, 
                                    supportProxy=supportProxy, proxyIp=proxyIp, 
                                    proxyPort=proxyPort, sslSupport=sslSupport)
        self.__type__ = __TYPE__
        self.__mutex__ = threading.RLock()


    def getType(self):
        """
        Returns agent type

        @return: agent type
        @rtype: string
        """
        return self.__type__

    def onCleanup(self):
        """
        Cleanup all
        In this function, you can stop your program
        """
        pass
        
    def initAfterRegistration(self):
        """
        Called on successful registration
        In this function, you can start your program automatically.
        """
        self.onToolLogWarningCalled("Starting dummy agent")
        self.onToolLogWarningCalled("Dummy agent started")
        self.onPluginStarted()
    
    def pluginStarting(self):
        """
        Function to reimplement
        """
        pass
        
    def onPluginStarted(self):
        """
        Function to reimplement
        """
        pass

    def pluginStopped(self):
        """
        Function to reimplement
        """
        pass

    def onResetAgentCalled(self):
        """
        Function to reimplement
        """
        pass
        
    def onToolLogWarningCalled(self, msg):
        """
        Logs warning on main application

        @param msg: warning message
        @type msg: string
        """
        pass

    def onToolLogErrorCalled(self, msg):
        """
        Logs error on main application

        @param msg: error message
        @type msg: string
        """
        pass

    def onToolLogSuccessCalled(self, msg):
        """
        Logs success on main application

        @param msg: error message
        @type msg: string
        """
        pass
    
    def onAgentAlive(self, client, tid, request):
        """
        Called on keepalive received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        pass
        
    def onAgentInit(self, client, tid, request):
        """
        Called on init received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        self.onToolLogWarningCalled(msg="init called: %s" % request['data'])
        self.sendNotify(request=request, data="notify sent")

    def onAgentReset(self, client, tid, request):
        """
        Called on reset received from test server
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}
        or 
        {'event': 'agent-reset', 'source-adapter': '1', 'script_id': '7_3_0'}
        
        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        if 'data' in request:
            self.onToolLogWarningCalled(msg="reset called: %s" % request['data'])
        else:
            self.onToolLogWarningCalled(msg="reset called")
            
    def onAgentNotify(self, client, tid, request):
        """
        Called on notify received from test server and dispatch it
        {'task-id': 'xx', 'from': 'tester', 'destination-agent': 'xxxxx', 'source-adapter': 'xx', 
        'script-name': 'xxxx', 'script_id': 'xxx', 'data': 'xxx', 'event': 'agent-init', 'test-id': 'xxx'}

        @param client: server address ip/port
        @type client: tuple

        @param tid: transaction id
        @type tid: integer

        @param request: request received from the server
        @type request: dict
        """
        self.__mutex__.acquire()
        self.onToolLogWarningCalled(msg="notify received: %s" % request['data'])

        if request['uuid'] in self.context():
            if request['source-adapter'] in self.context()[request['uuid']]:
                ctx_test = self.context()[request['uuid']][request['source-adapter']]
                self.execAction(request)
            else:
                self.error("Adapter context does not exists TestUuid=%s AdapterId=%s" % (request['uuid'], 
                                                                                         request['source-adapter'] ) )
        else:
            self.error("Test context does not exits TestUuid=%s" % request['uuid'])
        self.__mutex__.release()

    def execAction(self, request):
        """
        Execute action
        """
        currentTest = self.context()[request['uuid']][request['source-adapter']]

        self.onToolLogWarningCalled( "<< Starting Command=%s TestId=%s AdapterId=%s" % (request['data']['cmd'],
                                                                                        request['script_id'], 
                                                                                        request['source-adapter']) )
        try:
            cmd = request['data']['cmd']
            data = request['data']
            # connect
            if cmd == 'producer_connect':
                # init 
                kargs=data['kargs']
                try:
                    self.producer = KafkaProducer(bootstrap_servers=data['bootstrap_servers'], **kargs )
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'connected' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )	
                    
            elif cmd == 'producer_send':
                kargs=data['kargs']
                try:
                    future = self.producer.send(data['topic'], **kargs)
                    record_metadata=future.get(timeout=data['timeout'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': record_metadata } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'producer_flush':
                try:
                    self.producer.flush(data['timeout'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'flushed' })
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'producer_partitions_for':
                try:
                    partitions = self.producer.partitions_for(data['topic'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': partitions })
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'producer_close':
                try:
                    self.producer.close(int(data['timeout']))
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'closed' })
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_connect':
                kargs=data['kargs']
                try:
                    if not data['topics']:
                        self.consumer = KafkaConsumer(bootstrap_servers=data['bootstrap_servers'], **kargs)
                    else:
                        self.consumer = KafkaConsumer(data['topics'][0], bootstrap_servers=data['bootstrap_servers'], **kargs)
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'connected' })
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_consume':
                try:
                    for msg in self.consumer :
                        self.sendNotify(request=request, data={ "cmd": cmd , 'result': msg } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_close':
                try:
                    self.consumer.close(data['autocommit'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'closed' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_assign':
                try:
                    self.consumer.assign(data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'assigned' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_assignment':
                try:
                    topicpartitions = self.consumer.assignment()
                    self.sendNotify(request=request, data={ "cmd": cmd , 'topicpartitions': topicpartitions } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_beginning_offsets':
                try:
                    offsets = self.consumer.beginning_offsets(data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'offsets': offsets } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_commit':
                try:
                    self.consumer.commit(data['offsets'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'committed' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_commit_async':
                try:
                    future = self.consumer.commit_async(offsets=data['offsets'],callback=data['callback'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'future': future } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_committed':
                try:
                    offsets = self.consumer.committed(data['topicpartition'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'offsets': offsets } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_end_offsets':
                try:
                    partitions = self.consumer.end_offsets(data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'partitions': partitions } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_highwater':
                try:
                    offset = self.consumer.highwater(data['partition'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'offset': offset } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_offsets_for_times':
                try:
                    offsets = self.consumer.offsets_for_times(data['timestamps'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'offsets': offsets } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_partitions_for_topic':
                try:
                    partitions = self.consumer.partitions_for_topic(data['topic'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'partitions': partitions } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_pause':
                try:
                    self.consumer.pause(data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_paused':
                try:
                    partitions=self.consumer.paused()
                    self.sendNotify(request=request, data={ "cmd": cmd , 'partitions': partitions } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_poll':
                try:
                    records = self.consumer.poll(timeout_ms=data['timeout_ms'], max_records=data['max_records'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'records': records } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_position':
                try:
                    offset = self.consumer.position(data['topicpartition'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'offset': offset } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_resume':
                try:
                    self.consumer.resume(data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_seek':
                try:
                    self.consumer.seek(data['partition'],data['offset'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_seek_to_beginning':
                try:
                    self.consumer.seek_to_beginning(*data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_seek_to_end':
                try:
                    self.consumer.seek_to_end(*data['partitions'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_subscribe':
                try:
                    self.consumer.subscribe(topics=data['topics'], pattern=data['pattern'], listener=data['listener'])
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_subscription':
                try:
                    topics=self.consumer.subscription()
                    self.sendNotify(request=request, data={ "cmd": cmd , 'topics': topics } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_topics':
                try:
                    topics = self.consumer.topics()
                    self.sendNotify(request=request, data={ "cmd": cmd , 'topics': topics } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            elif cmd == 'consumer_unsubscribe':
                try:
                    self.consumer.unsubscribe()
                    self.sendNotify(request=request, data={ "cmd": cmd , 'result': 'success' } )
                except KafkaError  as e:
                    self.sendError( request , data={"cmd": cmd , "err-msg": str(e)} )
                    
            # unknown command
            else:
                raise Exception('cmd not supported: %s' % request['data']['cmd'] )
        except Exception as e:
            self.error( 'unable to run command: %s' % str(e) )
            self.sendError( request , data="unable to run command")

        self.onToolLogWarningCalled( "<< Terminated Command=%s TestId=%s AdapterId=%s" % (request['data']['cmd'],
                                                                                          request['script-id'], 
                                                                                          request['source-adapter']) )

