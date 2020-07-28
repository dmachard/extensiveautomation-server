#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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

import threading
import time
import inspect
import os
import socket
import re
import sys
import platform

try:
    xrange
except NameError:  # support python3
    xrange = range
try:
    import Queue
except ImportError:  # support python 3
    import queue as Queue

from ea.libs import Scheduler
from ea.testexecutorlib import TestSettings
from ea.testexecutorlib import TestTemplatesLib
from ea.testexecutorlib import TestLoggerXml as TLX

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

__DESCRIPTION__ = """The library provides some important functionalities to create adapters."""

__HELPER__ = [
    ('Adapter', ['__init__', 'getAdapterId', 'testcase',
                             'privateGetFile', 'privateAddFolder',
                             'privateGetPath', 'privateSaveFile',
                             'privateAppendFile', 'setRunning',
                             'unsetRunning', 'stopRunning',
                             'received', 'logSentEvent', 'logRecvEvent',
                             'info', 'error', 'warning', 'debug', 'onRun',
                             'onReset', 'receivedNotifyFromAgent',
                             'receivedErrorFromAgent',
                             'receivedDataFromAgent']),
    ('State', ['__init__', 'set', 'get']),
    ('Timer', ['__init__', 'setDisable', 'setEnable',
                           'setDuration', 'start', 'stop', 'restart'])
]


# AF_PACKET, SOCK_DGRAM, Ethernet protocol, cooked Linux packet socket
COOKED_PACKET_SOCKET = 0
# AF_PACKET, SOCK_RAW, Ethernet protocol, raw Linux packet socket
RAW_PACKET_SOCKET = 1
UNIX_DGRAM_SOCKET = 2     # AF_UNIX, SOCK_DGRAM, 0, Unix-domain datagram socket
UNIX_STREAM_SOCKET = 3     # AF_UNIX, SOCK_STREAM, 0, Unix-domain stream socket

INET6_RAW_SOCKET = 4     # AF_INET6, SOCK_RAW, an IP protocol, IPv6 raw socket
# AF_INET6, SOCK_DGRAM, 0 (or IPPROTO_UDP), UDP over IPv6
INIT6_DGRAM_SOCKET = 5
# AF_INET6, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv6
INIT6_STREAM_SOCKET = 6

INIT_ICMP_SOCKET = 7     # AF_INET, SOCK_RAW, 0x01
# AF_INET, SOCK_DGRAM, 0 (or IPPROTO_UDP), UDP over IPv4
INIT_DGRAM_SOCKET = 8
# AF_INET, SOCK_STREAM, 0 (or IPPROTO_TCP), TCP over IPv4
INIT_STREAM_SOCKET = 9
INIT_UDP_SOCKET = 10    # AF_INET, SOCK_RAW, 0x11
INIT_TCP_SOCKET = 11    # AF_INET, SOCK_RAW, 0x06

SOCKET_BUFFER = 65535

LEVEL_ADAPTER = 'ADAPTER'
LEVEL_SUT = 'SUT'
LEVEL_USER = 'USER'


class TestAdaptersException(Exception):
    pass


class TestTimerException(Exception):
    pass


class TestStateException(Exception):
    pass


def caller():
    """
    Function to find out which function is the caller of the current function.

    @return: caller function name
    @rtype: string
    """
    return inspect.getouterframes(inspect.currentframe())[1][1:4]


def check_timeout(timeout, caller):
    """
    """
    timeout_valid = False
    if isinstance(timeout, int):
        timeout_valid = True
    if isinstance(timeout, float):
        timeout_valid = True
    if isinstance(timeout, bool):
        timeout_valid = False
    if not timeout_valid:
        raise ValueException(
            caller,
            "timeout argument is not a float or integer (%s)" %
            type(timeout))


def check_agent(caller, agent, agent_support, agent_type):
    """
    """
    if agent_support and agent is None:
        raise ValueException(
            caller, "agent support activated, but no agent provided!")
    if agent_support:
        if not isinstance(agent, dict):
            raise ValueException(
                caller, "agent must be a dict (%s)" %
                type(agent))
        if not len(agent['name']):
            raise ValueException(caller, "agent name cannot be empty")
        if agent['type'] != agent_type:
            raise ValueException(
                caller, 'Bad agent type: %s, expected: %s' %
                (agent['type'], agent_type))


class AdapterException(Exception):
    """
    """

    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg

    def __str__(self):
        """
        """
        # normalize path
        sut = os.path.normpath(getMainPath())
        orig = os.path.normpath(self.orig[0])

        f = orig.split(sut)[1]
        ret = "Adapter.%s > %s" % (self.orig[2], self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret


class ValueException(Exception):
    """
    """

    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg

    def __str__(self):
        """
        """
        # sut adapters path normalized, remove double // or more
        sut = os.path.normpath(getMainPath())
        orig = os.path.normpath(self.orig[0])

        f = orig.split(sut)[1]
        ret = "Adapter.%s > %s" % (self.orig[2], self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret


def getSocket(sockType):
    """
    Get socket

    @param sockType: TestAdapter.RAW_PACKET_SOCKET | TestAdapter.INIT6_STREAM_SOCKET | TestAdapter.INIT_STREAM_SOCKET
    @type sockType: integer

    @return: socket
    @rtype: socket
    """
    if sockType == COOKED_PACKET_SOCKET:  # cooked Linux packet socket
        sock = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_DGRAM,
            socket.SOCK_RAW)
    elif sockType == RAW_PACKET_SOCKET:  # raw Linux packet socket
        sock = socket.socket(
            socket.AF_PACKET,
            socket.SOCK_RAW,
            socket.SOCK_RAW)
    elif sockType == UNIX_DGRAM_SOCKET:  # Unix-domain datagram socket
        sock = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_DGRAM,
            socket.SOCK_RAW)
    elif sockType == UNIX_STREAM_SOCKET:  # Unix-domain stream socket
        sock = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
            socket.SOCK_RAW)
    elif sockType == INET6_RAW_SOCKET:  # IPv6 raw socket
        sock = socket.socket(
            socket.AF_INET6,
            socket.SOCK_RAW,
            socket.IPPROTO_IP)
    elif sockType == INIT6_DGRAM_SOCKET:  # UDP over IPv6
        sock = socket.socket(
            socket.AF_INET6,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
    elif sockType == INIT6_STREAM_SOCKET:  # TCP over IPv6
        sock = socket.socket(
            socket.AF_INET6,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
    elif sockType == INIT_ICMP_SOCKET:  # ICMP socket
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_RAW,
            0x01)  # 0x01 == ICMP
    elif sockType == INIT_UDP_SOCKET:  # UDP socket
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_RAW,
            0x11)  # 0x11 == UDP
    elif sockType == INIT_TCP_SOCKET:  # TCP socket
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_RAW,
            0x06)  # 0x06 == TCP
    elif sockType == INIT_DGRAM_SOCKET:  # UDP over IPv4
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_DGRAM,
            socket.IPPROTO_UDP)
    elif sockType == INIT_STREAM_SOCKET:  # TCP over IPv4
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP)
    else:
        sock = None
    return sock


_GeneratorAdpId = 0
_GeneratorAdpIdMutex = threading.RLock()


def _getNewAdpId():
    """
    Generates a new unique ID.

    @return:
    @rtype:
    """
    global _GeneratorAdpId
    _GeneratorAdpIdMutex.acquire()
    _GeneratorAdpId += 1
    ret = _GeneratorAdpId
    _GeneratorAdpIdMutex.release()
    return ret


_GeneratorTimerId = 0
_GeneratorTimerIdMutex = threading.RLock()


def _getNewTimerId():
    """
    Generates a new unique ID for timer

    @return:
    @rtype:
    """
    global _GeneratorTimerId
    _GeneratorTimerIdMutex.acquire()
    _GeneratorTimerId += 1
    ret = _GeneratorTimerId
    _GeneratorTimerIdMutex.release()
    return ret


__mainPath = ''


def setMainPath(sutPath):
    """
    Set the main path
    """
    global __mainPath
    __mainPath = sutPath


def getMainPath():
    """
    Return path where adapter are installed

    @return: test result path
    @rtype: string
    """
    return TestSettings.get('Paths', 'sut-adapters')


ADAPTER_NAME = "Adapter"


class Adapter(threading.Thread):
    """
    Adapter class
    """

    def __init__(self, parent, name, realname=None, debug=False,
                 showEvts=True, showSentEvts=True, showRecvEvts=True, shared=False,
                 agentSupport=False, agent=None, timeoutSleep=0.1, caller=None,
                 agentType=None):
        """
        All adapters must inherent from this class

        @param parent: the parent testcase
        @type parent: testcase

        @param name: adapter type name
        @type name: string

        @param realname: adapter name
        @type realname: string/None

        @param agentSupport: use agent or not (default=False)
        @type agentSupport: boolean

        @param agent: agent name (default=None)
        @type agent: none/dict

        @param debug: True to activate debug mode, default value=False
        @type debug: boolean

        @param shared: True to activate shared mode, default value=False
        @type shared: boolean
        """
        self.setFailed = parent.setFailed

        threading.Thread.__init__(self)
        self.stopEvent = threading.Event()
        # queue for event
        self.queue = Queue.Queue(0)
        self.last_event_queue = None
        self.timeoutSleep = timeoutSleep

        self.__agentSupport = agentSupport
        self.__agentName = agent
        self.__agentType = agentType
        self.__caller = caller

        self.__adp_id__ = _getNewAdpId()
        self.__showEvts = showEvts
        self.__showSentEvts = showSentEvts
        self.__showRecvEvts = showRecvEvts
        self.debugMode = debug
        self.__timers = []
        self.__states = []

        # new in v19, checking the agent provided
        check_agent(caller=self.__caller,
                    agent=self.__agentName,
                    agent_support=self.__agentSupport,
                    agent_type=self.__agentType)
        # end of new

        self.NAME = self.__class__.__name__.upper()
        self.timerId = -1
        self.matchId = -1
        self.name__ = name.upper()
        self.realname__ = realname

        self.__testcase = parent
        self.testcaseId = parent.getId()
        self.__shared = shared
        parent.registerComponent(self, shared=shared)
        self.running = False

        self.initStorageData()

        self.received_running = False
        self.received_result = None
        self.received_template = None
        self.received_available = threading.Event()

        print("Start thread for adapter=%s" % self.NAME)
        self.start()

    def clear_queue(self):
        """clear the queue"""
        self.queue.queue.clear()
        
    def last_item_queue(self):
        """get last item from the queue"""
        return self.last_event_queue
        
    def getTestResultPath(self):
        """
        Return the test result path

        @return: test result path
        @rtype: string
        """
        return "%s/" % TestSettings.get('Paths', 'result')

    def getFromLevel(self):
        """
        Return the from level
        """
        if self.realname__ is None:
            self.realname__ = "%s #%s" % (LEVEL_ADAPTER, self.__adp_id__)
        return self.realname__.upper()

    def isShared(self):
        """
        This adapter is shared
        """
        return self.__shared

    def renewAdp(self, parent):
        """
        Renew the adapter
        """
        self.setFailed = parent.setFailed
        self.testcaseId = parent.getId()
        self.parent = parent

        # update parent timer
        for t in self.__timers:
            t.updateParent(parent=self)

        # update parent state
        for s in self.__states:
            s.updateParent(parent=self)

        parent.registerComponent(self, shared=self.__shared)
        self.initStorageData()

    def setTestcaseId(self, id):
        """
        Set the testcase id
        """
        self.testcaseId = id

    def getAdapterId(self):
        """
        Return the adapter id
        """
        return self.__adp_id__

    def isShowingEvts(self):
        """
        Is showing events
        """
        return self.__showEvts

    def isShowingSentEvts(self):
        """
        Is showing sent events
        """
        return self.__showSentEvts

    def isShowingRecvEvts(self):
        """
        Is showing received events
        """
        return self.__showRecvEvts

    def __repr__(self):
        """
        Repr
        """
        return ADAPTER_NAME

    def __str__(self):
        """
        Str
        """
        return ADAPTER_NAME

    def __unicode__(self):
        """
        Unicode
        """
        return ADAPTER_NAME

    def testcase(self):
        """
        Accessor to the testcase
        """
        return self.__testcase

    def getTcId(self):
        """
        Return testcase id
        """
        return self.testcaseId

    def getRealname(self):
        """
        Return realname of the adapter
        """
        return self.realname__

    def getName(self):
        """
        Return name
        """
        return self.name__

    def setName(self, name):
        """
        Set the name
        """
        self.name__ = name.upper()
        # init a second time if the name of the adapter is updated
        self.initStorageData()

    def getDataStoragePath(self):
        """
        Return the storage data path

        @return: storage path
        @rtype: string
        """
        pathData = TestSettings.get('Paths', 'tmp')
        path_storage = "%s/ADP-%s-#%s/" % (pathData,
                                           self.name__,
                                           self.__adp_id__)
        if platform.system() == "Windows":
            return os.path.normpath(path_storage)
        else:
            return os.path.normpath("/%s" % path_storage)

    def initStorageData(self):
        """
        Initiallize the storage data
        """
        pathData = TestSettings.get('Paths', 'tmp')
        if not os.path.exists(pathData):
            self.debug('temp data storage is missing...')
        else:
            path_storage = "%s/ADP-%s-#%s/" % (pathData,
                                               self.name__,
                                               self.__adp_id__)

            # create the adapter folder: FolderName-uniqueID
            if platform.system() == "Windows":
                adpDirName = os.path.normpath(path_storage)
            else:
                adpDirName = os.path.normpath("/%s" % path_storage)

            try:
                if not os.path.exists(adpDirName):
                    os.mkdir(adpDirName)
            except Exception as e:
                self.debug("unable to init storage data: %s" % str(e))

    def privateGetFile(self, filename):
        """
        Get file in private area

        @param filename: filename to read
        @type filename: string

        @return: file contetn
        @rtype: string
        """
        data = ''
        try:
            f = open("%s/%s" % (self.privateGetPath(), filename), 'rb')
            data = f.read()
            f.close()
        except OSError as e:
            raise Exception("os error on get file: %s" % e)
        return data

    def privateAddFolder(self, folder):
        """
        Add folder in the private area of the adapter

        @param folder: folder name to add
        @type folder: string
        """
        try:
            os.mkdir("%s/%s" % (self.privateGetPath(), folder))
        except OSError as e:
            raise Exception("adapter os error: %s" % e)

    def privateGetPath(self):
        """
        Return path to access to the private area of the adapter

        @return: public path
        @rtype: string
        """
        privatePath = self.getDataStoragePath()
        return "%s/" % os.path.normpath(privatePath)

    def privateSaveFile(self, destname, data):
        """
        Storing binary data. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        self.saveDataInStorage(destname, data)

    def saveDataInStorage(self, destname, data):
        """
        Storing binary data. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        # create the file
        self.debug('saving data in storage...')
        try:
            f = open("%s/%s" % (self.getDataStoragePath(), destname), 'wb')
            f.write(data)
            f.close()
            self.debug('data saved')
        except Exception as e:
            self.debug("unable to write data in data storage: %s" % str(e))

    def privateAppendFile(self, destname, data):
        """
        Append binary data. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        self.appendDataInStorage(destname, data)

    def appendDataInStorage(self, destname, data):
        """
        Append binary data. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        # create the file
        try:
            f = open("%s/%s" % (self.getDataStoragePath(), destname), 'ab')
            f.write(data)
            f.close()
        except Exception as e:
            self.debug("unable to append data in data storage: %s" % str(e))

    def setRunning(self):
        """
        Start to run the <onRun> function
        """
        self.running = True

    def unsetRunning(self):
        """
        Stop to run the <onRun> function
        """
        self.running = False

    def stopRunning(self):
        """
        Stop adapter
        """
        self.running = False
        self.stop()

    def registerTimer(self, timer):
        """
        Register timer to reset them properly at the end
        """
        self.__timers.append(timer)

    def registerState(self, state):
        """
        Register state
        """
        self.__states.append(state)

    def getTimerId(self):
        """
        Return the timer id
        """
        self.timerId += 1
        return self.timerId

    def getMatchId(self):
        """
        Return the match id
        """
        self.matchId += 1
        return self.matchId

    def received(self, expected, timeout, AND=True, XOR=False):
        """
        """
        
        if not AND and not XOR:
            raise TestAdaptersException("ERR_ADP_010: no condition defined")
        self.getMatchId()
        componentName = "%s [%s_%s]" % (
            self.name__, 'Match', str(self.matchId))

        if not isinstance(expected, list):
            self.received_template = [expected]
        else:
            self.received_template = expected

        # log match started event
        for i in xrange(len(self.received_template)):
            if not isinstance(
                    self.received_template[i], TestTemplatesLib.TemplateMessage):
                raise TestAdaptersException('ERR_ADP_009: template message expected '
                                            'but a bad type is passed '
                                            'on argument: %s' % type(self.received_template[i]))

            expctd = TestTemplatesLib.tpl2str(
                expected=self.received_template[i].get())
            if self.__showEvts:
                TLX.instance().log_match_started(fromComponent=componentName,
                                                 dataMsg=expctd,
                                                 tcid=self.testcaseId,
                                                 font='italic',
                                                 expire=timeout,
                                                 index=i,
                                                 fromlevel=self.getFromLevel(),
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__testcase.getTestInfo())

        self.received_running = True
        self.received_result = None
        
        timeoutBool = False
        startTime = time.time()
        while (self.received_result is None) and (not timeoutBool):

            # check if the timer is exceeded
            if (time.time() - startTime) >= float(timeout):
                timeoutBool = True

            if not self.queue.empty():
                evt = self.queue.get(False)
                self.last_event_queue = evt
                for i in xrange(len(self.received_template)):
                    success, tpl = TestTemplatesLib.comparePayload(payload=evt.get(),
                                                                   tpl=self.received_template[i].get(),
                                                                   debug=self.debug)
                    if success:
                        self.received_result = evt

                        if self.__showEvts:
                            TLX.instance().log_match_stopped(fromComponent=componentName,
                                                             dataMsg=(
                                                                 evt.get(), tpl),
                                                             tcid=self.testcaseId,
                                                             font='italic',
                                                             index=i,
                                                             fromlevel=self.getFromLevel(),
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testcase.getTestInfo())

                        break
                    else:
                        if self.__showEvts:
                            TLX.instance().log_match_info(fromComponent=componentName,
                                                          dataMsg=(
                                                              evt.get(), tpl),
                                                          tcid=self.testcaseId,
                                                          font='italic',
                                                          index=i,
                                                          fromlevel=self.getFromLevel(),
                                                          tolevel=LEVEL_USER,
                                                          testInfo=self.__testcase.getTestInfo())

            time.sleep(0.2)

        self.received_running = False
        return self.received_result

    def enqueueEvent(self, event):
        """
        Enqueue event
        """
        if not self.received_running:
            self.queue.put(event)

        else:
            self.last_event_queue = event
            
            componentName = "%s [%s_%s]" % (
                self.name__, 'Match', str(self.matchId))

            for i in xrange(len(self.received_template)):
                success, tpl = TestTemplatesLib.comparePayload(payload=event.get(),
                                                               tpl=self.received_template[i].get(),
                                                               debug=self.debug)
                if success:
                    self.received_running = False
                    self.received_result = event

                    if self.__showEvts:
                        TLX.instance().log_match_stopped(fromComponent=componentName,
                                                         dataMsg=(
                                                             event.get(), tpl),
                                                         tcid=self.testcaseId,
                                                         font='italic',
                                                         index=i,
                                                         fromlevel=self.getFromLevel(),
                                                         tolevel=LEVEL_USER,
                                                         testInfo=self.__testcase.getTestInfo())

                else:
                    if self.__showEvts:
                        TLX.instance().log_match_info(fromComponent=componentName,
                                                      dataMsg=(
                                                          event.get(), tpl),
                                                      tcid=self.testcaseId,
                                                      font='italic',
                                                      index=i,
                                                      fromlevel=self.getFromLevel(),
                                                      tolevel=LEVEL_USER,
                                                      testInfo=self.__testcase.getTestInfo())

    def recvFrom(self, shortMsg, dataMsg, typeMsg):
        """
        Receveid event from
        """
        try:
            TLX.instance().log_rcv(shortMsg,
                                   dataMsg,
                                   typeMsg,
                                   self.name__,
                                   self.testcaseId,
                                   fromlevel=LEVEL_SUT,
                                   tolevel=self.getFromLevel(),
                                   testInfo=self.__testcase.getTestInfo())
        except Exception as e:
            self.error('ERR_ADP_006: internal recv from: %s' % str(e))

    def sendTo(self, shortMsg, dataMsg, typeMsg):
        """
        Send event to
        """
        try:
            TLX.instance().log_snd(shortMsg,
                                   dataMsg,
                                   typeMsg,
                                   self.name__,
                                   self.testcaseId,
                                   fromlevel=self.getFromLevel(),
                                   tolevel=LEVEL_SUT,
                                   testInfo=self.__testcase.getTestInfo())
        except Exception as e:
            self.error('ERR_ADP_005: internal send to: %s' % str(e))

    def logSentEvent(self, shortEvt, tplEvt):
        """
        Log the event sent to the SUT

        @param shortEvt: short resume of the event
        @type shortEvt: string

        @param tplEvt: event sent
        @type tplEvt: templatemessage
        """
        if not isinstance(tplEvt, TestTemplatesLib.TemplateMessage):
            raise TestAdaptersException('ERR_ADP_001: template message expected '
                                        'but a bad type is passed '
                                        'on argument: %s' % type(tplEvt))

        if self.__showSentEvts:
            try:
                tpl = tplEvt.getEvent()
            except Exception as e:
                self.error('ERR_ADP_003: unable to get event '
                           'from the templatemessage sent: %s' % str(e))
            else:
                self.sendTo(
                    shortMsg=shortEvt,
                    dataMsg=tpl,
                    typeMsg=tplEvt.type())

    def logRecvEvent(self, shortEvt, tplEvt):
        """
        Log the received event from the SUT

        @param shortEvt: short resume of the event
        @type shortEvt: string

        @param tplEvt: event received
        @type tplEvt: templatemessage
        """
        if not isinstance(tplEvt, TestTemplatesLib.TemplateMessage):
            raise TestAdaptersException('ERR_ADP_002: template message expected '
                                        'but a bad type is passed '
                                        'on argument: %s' % type(tplEvt))

        if self.__showRecvEvts:
            try:
                tpl = tplEvt.getEvent()
            except Exception as e:
                self.error('ERR_ADP_004: unable to get event '
                           'from the templatemessage received: %s' % str(e))
            else:
                self.recvFrom(
                    shortMsg=shortEvt,
                    dataMsg=tpl,
                    typeMsg=tplEvt.type())
        self.enqueueEvent(event=tplEvt)

    def info(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an info message
        Nothing is displayed if txt=None

        @param txt: info message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        typeMsg = ''
        if raw:
            typeMsg = 'raw'

        try:
            TLX.instance().log_testcase_info(message=txt,
                                             component=self.name__,
                                             tcid=self.testcaseId,
                                             bold=bold,
                                             italic=italic,
                                             multiline=multiline,
                                             typeMsg=typeMsg,
                                             fromlevel=self.getFromLevel(),
                                             tolevel=LEVEL_USER,
                                             testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_info(message=txt.encode('utf8'),
                                             component=self.name__,
                                             tcid=self.testcaseId,
                                             bold=bold,
                                             italic=italic,
                                             multiline=multiline,
                                             typeMsg=typeMsg,
                                             fromlevel=self.getFromLevel(),
                                             tolevel=LEVEL_USER,
                                             testInfo=self.__testcase.getTestInfo())

    def error(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an error message
        Nothing is displayed if txt=None

        @param txt: error message
        @type txt: string

        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        typeMsg = ''
        if raw:
            typeMsg = 'raw'
        self.setFailed(internal=True)

        try:
            TLX.instance().log_testcase_error(message=txt,
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_error(message=txt.encode('utf8'),
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())

    def trace(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Trace message
        Nothing is displayed if txt=None

        @param txt: trace message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        typeMsg = ''
        if raw:
            typeMsg = 'raw'
        try:
            TLX.instance().log_testcase_trace(message=txt, component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_trace(message=txt.encode('utf8'),
                                              component=self.name__,
                                              tcid=self.testcaseId,
                                              bold=bold,
                                              italic=italic,
                                              multiline=multiline,
                                              typeMsg=typeMsg,
                                              fromlevel=self.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testcase.getTestInfo())

    def warning(self, txt, bold=False, italic=False,
                multiline=False, raw=False):
        """
        Display an debug message
        Nothing is displayed if txt=None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        typeMsg = ''
        if raw:
            typeMsg = 'raw'
        try:
            TLX.instance().log_testcase_warning(message=txt,
                                                component=self.name__,
                                                tcid=self.testcaseId,
                                                bold=bold,
                                                italic=italic,
                                                multiline=multiline,
                                                typeMsg=typeMsg,
                                                fromlevel=self.getFromLevel(),
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testcase.getTestInfo())
        except UnicodeEncodeError:
            TLX.instance().log_testcase_warning(message=txt.encode('utf8'),
                                                component=self.name__,
                                                tcid=self.testcaseId,
                                                bold=bold,
                                                italic=italic,
                                                multiline=multiline,
                                                typeMsg=typeMsg,
                                                fromlevel=self.getFromLevel(),
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testcase.getTestInfo())

    def debug(self, txt, raw=True):
        """
        Display an debug message

        @param txt: debug message
        @type txt: string
        """
        if self.debugMode:
            self.trace("[%s] %s" % (self.__class__.__name__, txt), raw=raw)

    def stop(self):
        """
        Stop adapter
        """
        print("Stop thread for adapter=%s" % self.NAME)
        self.stopEvent.set()

    def run(self):
        """
        On run
        """
        while not self.stopEvent.isSet():
            try:
                if self.running:
                    self.onRun()
                time.sleep(self.timeoutSleep)
            except Exception as e:
                self.error("error on run: %s" % str(e))
                self.stop()

    def onRun(self):
        """
        Function to reimplement
        """
        pass

    def onTimerReset(self):
        """
        """
        for tm in self.__timers:
            tm.stop()

    def onReset(self):
        """
        On reset, called automatically by framework
        Function to overwrite
        """
        pass

    def receivedNotifyFromAgent(self, data):
        """
        Received notify from agent
        Function to reimplement
        """
        pass

    def receivedErrorFromAgent(self, data):
        """
        Received error from agent
        Function to reimplement
        """
        pass

    def receivedDataFromAgent(self, data):
        """
        Received data from agent
        Function to reimplement
        """
        pass


TIMER_NAME = "Timer"


class Timer(object):
    """
    Timer object
    """

    def __init__(self, parent, duration, name, callback,
                 logEvent=True, enabled=True, callbackArgs={}):
        """
        Timer

        @param parent: adapter
        @type parent: adapter

        @param duration: time to wait in seconds
        @type duration: float

        @param name: timer description
        @type name: string

        @param callback: callback function
        @type callback: function

        @param logEvent: log timer events (default=True)
        @type logEvent: boolean

        @param enabled: timer enabled (default=True)
        @type enabled: boolean

        @param callbackArgs: arguments to the callback function
        @type callbackArgs: dict
        """
        if not isinstance(parent, Adapter):
            raise TestTimerException(
                'ERR_TMR_001: parent type not supported: %s' %
                type(parent))
        self.__evt = None
        if isinstance(duration, int) or isinstance(duration, float):
            self.__duration = duration
        else:
            raise TestTimerException(
                'ERR_TMR_002: integer or float expected to initialize the timer: %s' %
                type(duration))
        self.__name = name
        self.__parent = parent
        self.__cb = callback
        self.__cb_args = callbackArgs
        # tescase id
        self.__tcid = self.__parent.getTcId()
        # timer id
        self.__tid = self.__parent.getTimerId()
        # parent name
        self.__pname = self.__parent.getName()
        # new in 7.2.0
        self.__logEvent = logEvent
        self.__parent.registerTimer(timer=self)
        # new in 10.1
        self.__isenabled = enabled

    def updateParent(self, parent):
        """
        """
        self.__parent = parent
        self.__tcid = self.__parent.getTcId()
        self.__tid = self.__parent.getTimerId()
        self.__pname = self.__parent.getName()

    def __repr__(self):
        """
        repr
        """
        return TIMER_NAME

    def __str__(self):
        """
        str
        """
        return TIMER_NAME

    def __unicode__(self):
        """
        unicode
        """
        return TIMER_NAME

    def setDisable(self):
        """
        Disable the timer
        """
        self.__isenabled = False

    def setEnable(self):
        """
        Enable the timer
        """
        self.__isenabled = True

    def __onTimeout(self):
        """
        on timeout, internal function
        """

        self.__parent.debug(txt=self.__parent.testcase().getTestInfo())

        componentName = "%s [%s_%s]" % (self.__pname, 'Timer', str(self.__tid))
        if self.__logEvent:
            TLX.instance().log_timer_exceeded(fromComponent=componentName,
                                              dataMsg=self.__name,
                                              tcid=self.__tcid,
                                              font='italic',
                                              fromlevel=self.__parent.getFromLevel(),
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__parent.testcase().getTestInfo())
        else:
            self.__parent.debug(txt='%s on timeout' % componentName)
        self.__evt = None
        if self.__isenabled:
            self.__cb(**self.__cb_args)
        else:
            self.__parent.debug(txt='timer disabled, no run of the callback')

    def setDuration(self, duration):
        """
        Set the duration

        @param duration: time to wait in seconds
        @type duration: float
        """
        self.__duration = duration

    def start(self):
        """
        Start the timer
        """
        if not self.__isenabled:
            self.__parent.debug(txt="timer disabled, no start")
            return
        if self.__evt is None:
            self.__evt = Scheduler.registerEvent(
                delay=self.__duration, callback=self.__onTimeout)
            componentName = "%s [%s_%s]" % (
                self.__pname, 'Timer', str(self.__tid))
            if self.__logEvent:
                TLX.instance().log_timer_started(fromComponent=componentName,
                                                 dataMsg=self.__name,
                                                 tcid=self.__tcid,
                                                 font='italic',
                                                 expire=self.__duration,
                                                 fromlevel=self.__parent.getFromLevel(),
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__parent.testcase().getTestInfo())
            else:
                self.__parent.debug(txt='start timer %s' % componentName)

    def stop(self):
        """
        Stop the timer before the end
        """
        if self.__evt is not None:
            Scheduler.unregisterEvent(evt=self.__evt)
            componentName = "%s [%s_%s]" % (
                self.__pname, 'Timer', str(self.__tid))
            if self.__logEvent:
                TLX.instance().log_timer_stopped(fromComponent=componentName,
                                                 dataMsg=self.__name,
                                                 tcid=self.__tcid,
                                                 font='italic',
                                                 fromlevel=self.__parent.getFromLevel(),
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__parent.testcase().getTestInfo())
            else:
                self.__parent.debug(txt='stop timer %s' % componentName)
            self.__evt = None

    def restart(self):
        """
        Restart the timer before the end
        """
        if not self.__isenabled:
            self.__parent.debug(txt="timer disabled, no restart")
            return
        if self.__evt is None:
            self.__evt = Scheduler.registerEvent(
                delay=self.__duration, callback=self.__onTimeout)
            componentName = "%s [%s_%s]" % (
                self.__pname, 'Timer', str(self.__tid))
            if self.__logEvent:
                TLX.instance().log_timer_restarted(fromComponent=componentName,
                                                   dataMsg=self.__name,
                                                   tcid=self.__tcid,
                                                   font='italic',
                                                   expire=self.__duration,
                                                   fromlevel=self.__parent.getFromLevel(),
                                                   tolevel=LEVEL_USER,
                                                   testInfo=self.__parent.testcase().getTestInfo())
            else:
                self.__parent.debug(txt='restart timer %s' % componentName)


STATE_NAME = "Automaton"


class State(object):
    """
    """

    def __init__(self, parent, name, initial):
        """
        State manager

        @param parent: parent adapter
        @type parent: adapter

        @param name: automaton name
        @type name: string

        @param initial: initial state
        @type initial: string
        """
        if not isinstance(parent, Adapter):
            raise TestStateException(
                'ERR_STA_001: parent type not supported: %s' %
                type(parent))
        self.__parent = parent
        self.__testcaseId = self.__parent.getTcId()
        self.__name = name.upper()
        self.__current_state = None
        self.__stateId = -1
        self.__states = {}

        self.__parent.registerState(state=self)

        # initialize
        self.set(state=initial)

    def updateParent(self, parent):
        """
        """
        self.__parent = parent
        self.__testcaseId = self.__parent.getTcId()

    def __repr__(self):
        """
        repr
        """
        return STATE_NAME

    def __str__(self):
        """
        str
        """
        return STATE_NAME

    def __unicode__(self):
        """
        unicode
        """
        return STATE_NAME

    def set(self, state):
        """
        Set the state

        @param state: state
        @type state: string
        """
        if state in self.__states:
            stateid = self.__states[state]
        else:
            self.__stateId += 1
            self.__states[state] = self.__stateId
            stateid = self.__stateId
        self.__parent.debug(
            "%s: state %s > %s" %
            (self.__name, stateid, state.lower()))
        self.__current_state = state

    def get(self):
        """
        Returns the current state

        @return: current state
        @rtype: string
        """
        return self.__current_state
