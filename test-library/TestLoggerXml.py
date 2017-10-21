#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2017 Denis Machard
# This file is part of the extensive testing project
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

import time 
import traceback
import StringIO
import sys
import re
import uuid
import json

class TestLoggerException(Exception): pass

import base64

try:
    import cPickle
except ImportError: # support python 3
    import pickle as cPickle
PICKLE_VERSION=2

import TestClientInterface as TCI
import TestSettings

EVENT_SCRIPT_STARTED = 'script-started'
EVENT_SCRIPT_STOPPED = 'script-stopped'

EVENT_TESTGLOBAL_STARTED = 'testglobal-started'
EVENT_TESTGLOBAL_STOPPED = 'testglobal-stopped'

EVENT_TESTPLAN_STARTED = 'testplan-started'
EVENT_TESTPLAN_STOPPED = 'testplan-stopped'
EVENT_TESTPLAN_SEP_TERMINATED = 'testplan-separator-terminated'
EVENT_TESTPLAN_SEP = 'testplan-separator'

EVENT_TESTABSTRACT_STARTED = 'testabstract-started'
EVENT_TESTABSTRACT_STOPPED = 'testabstract-stopped'

EVENT_TESTUNIT_STARTED = 'testunit-started'
EVENT_TESTUNIT_STOPPED = 'testunit-stopped'

EVENT_TESTSUITE_STARTED = 'testsuite-started'
EVENT_TESTSUITE_STOPPED = 'testsuite-stopped'

EVENT_TESTCASE_STARTED = 'testcase-started'
EVENT_TESTCASE_STOPPED = 'testcase-stopped'

class TestLoggerXml:
    """
    Test logger xml
    """
    def __init__ (self, path, name, user_,testname_, id_, replay_id_, task_id_, userid_, channelid_):
        """
        Constructor for the test logger xml

        @param address:
        @type address:

        @param address:
        @type address:

        @param address:
        @type address:

        @param address:
        @type address:
        """
        # colors definitions
        self.STATE=TestSettings.get( 'Event_Colors', 'state' )
        self.STATE_TEXT=TestSettings.get( 'Event_Colors', 'state-text' )

        self.INTERNAL=TestSettings.get( 'Event_Colors', 'internal' )
        self.INTERNAL_TEXT=TestSettings.get( 'Event_Colors', 'internal-text' )

        self.TIMER=TestSettings.get( 'Event_Colors', 'timer' )
        self.TIMER_TEXT=TestSettings.get( 'Event_Colors', 'timer-text' )

        self.MATCH=TestSettings.get( 'Event_Colors', 'match' )
        self.MATCH_TEXT=TestSettings.get( 'Event_Colors', 'match-text' )

        self.MISMATCH=TestSettings.get( 'Event_Colors', 'mismatch' )
        self.MISMATCH_TEXT=TestSettings.get( 'Event_Colors', 'mismatch-text' )

        self.PAYLOAD=TestSettings.get( 'Event_Colors', 'payload' )
        self.PAYLOAD_TEXT=TestSettings.get( 'Event_Colors', 'payload-text' )

        self.INFO_TG=TestSettings.get( 'Event_Colors', 'info-tg' )
        self.INFO_TG_TEXT=TestSettings.get( 'Event_Colors', 'info-tg-text' )

        self.INFO_TP=TestSettings.get( 'Event_Colors', 'info-tp' )
        self.INFO_TP_TEXT=TestSettings.get( 'Event_Colors', 'info-tp-text' )

        self.INFO_TS=TestSettings.get( 'Event_Colors', 'info-ts' )
        self.INFO_TS_TEXT=TestSettings.get( 'Event_Colors', 'info-ts-text' )

        self.INFO_TC =TestSettings.get( 'Event_Colors', 'info-tc' )
        self.INFO_TC_TEXT =TestSettings.get( 'Event_Colors', 'info-tc-text' )

        self.ERROR_TG = TestSettings.get( 'Event_Colors', 'error-tg' )
        self.ERROR_TG_TEXT = TestSettings.get( 'Event_Colors', 'error-tg-text' )

        self.ERROR_TP = TestSettings.get( 'Event_Colors', 'error-tp' )
        self.ERROR_TP_TEXT = TestSettings.get( 'Event_Colors', 'error-tp-text' )

        self.ERROR_TS = TestSettings.get( 'Event_Colors', 'error-ts' )
        self.ERROR_TS_TEXT = TestSettings.get( 'Event_Colors', 'error-ts-text' )

        self.ERROR_TC = TestSettings.get( 'Event_Colors', 'error-tc' )
        self.ERROR_TC_TEXT = TestSettings.get( 'Event_Colors', 'error-tc-text' )

        self.WARNING_TG = TestSettings.get( 'Event_Colors', 'warning-tg' )
        self.WARNING_TG_TEXT = TestSettings.get( 'Event_Colors', 'warning-tg-text' )

        self.WARNING_TP = TestSettings.get( 'Event_Colors', 'warning-tp' )
        self.WARNING_TP_TEXT = TestSettings.get( 'Event_Colors', 'warning-tp-text' )

        self.WARNING_TS = TestSettings.get( 'Event_Colors', 'warning-ts' )
        self.WARNING_TS_TEXT = TestSettings.get( 'Event_Colors', 'warning-ts-text' )

        self.WARNING_TC = TestSettings.get( 'Event_Colors', 'warning-tc' )
        self.WARNING_TC_TEXT = TestSettings.get( 'Event_Colors', 'warning-tc-text' )

        self.STEP_STARTED = TestSettings.get( 'Event_Colors', 'step-started' )
        self.STEP_STARTED_TEXT = TestSettings.get( 'Event_Colors', 'step-started-text' )

        self.STEP_PASSED = TestSettings.get( 'Event_Colors', 'step-passed' )
        self.STEP_PASSED_TEXT = TestSettings.get( 'Event_Colors', 'step-passed-text' )

        self.STEP_FAILED = TestSettings.get( 'Event_Colors', 'step-failed' )
        self.STEP_FAILED_TEXT = TestSettings.get( 'Event_Colors', 'step-failed-text' )

        self.__path = path
        self.testname = testname_
        self.__filename = "%s_%s.log" % ( testname_, replay_id_ )
        self.__filename_hdr = "%s_%s.hdr" % ( testname_, replay_id_ )
        self.__filename_json = "%s_%s.json" % ( testname_, replay_id_ )
        self.__nbline = 0
        self.__user = user_
        self.__userid = userid_
        self.__channelid = channelid_
        self.__id = id_
        self.__replayid = replay_id_
        self.uniqueId = 0
        self.taskId = task_id_
        self.mainTestName = testname_
        self.mainScriptId = '%s_%s_%s' % (self.taskId, self.__id, self.uniqueId)
        self.scriptId = '%s_%s_%s' % (self.taskId, self.__id, self.uniqueId)
        # Used only with testplan
        self.testPassed = {'0': 1, '0-0': 1 }
        self.currentTsId = None
        
        # Universally Unique IDentifiers
        self.testUuid = "%s" % uuid.uuid4()
    
    def getPath(self):
        """
        Return path
        """
        return self.__path

    def setMainTpId(self, tpId):
        """
        Set the main tp id
        """
        self.testPassed.update( {'%s' % tpId: 1} )
        self.testPassed.update( {'%s-0' % tpId: 1} )

    def setMainTpResult(self, tpId):
        """
        Set the main tp result
        """
        self.testPassed["%s" % tpId] = 0
        self.testPassed["%s-0" % tpId] = 0

    def setMainId (self):
        """
        Set the main id
        """
        self.testname = self.mainTestName
        self.scriptId = self.mainScriptId

    def setUniqueId (self, testName, tsId):
        """
        Used only with testplan
        """
        self.testname = testName
        self.uniqueId += 1
        self.scriptId = '%s_%s_%s' % (self.taskId, self.__id, self.uniqueId)
        self.testPassed[tsId] = 1
        self.currentTsId = tsId
        
    def setResult (self, result):
        """
        Set the result
        """        
        if result == 'PASS':
            ret = 1
        elif result in ['FAIL', 'UNDEFINED']:
            ret = 0

        if self.currentTsId is not None:
            self.testPassed[self.currentTsId] = self.testPassed[self.currentTsId] & ret
            regex = re.compile("(\d+-\d+-\d+)")
            if regex.search(self.currentTsId):
                mainTpId, _ , testId = self.currentTsId.split('-')
                self.testPassed["%s-0" % mainTpId] = self.testPassed["%s-0" % mainTpId] & ret

    def allPassed (self, tsId, notCond=""):
        """
        All passed
        """
        ret = False
        if tsId in self.testPassed: # Issue 255
            ret =  self.testPassed[tsId]
        else:
            if notCond.lower()=="not":
                ret = True
            else:
                ret = False
        return ret
        
    def getBackTrace(self):
        """
        Returns the current backtrace.

        @return:
        @rtype:
        """
        backtrace = StringIO.StringIO()
        traceback.print_exc(None, backtrace)
        ret = backtrace.getvalue()
        backtrace.close()
        return ret

    def getTestInfo(self):
        """
        Return the test info
        """
        return { 'from': self.__user, 'task-id': self.taskId, 'test-id': self.__id, 
                'script_name': self.testname, 'script_id': self.scriptId, 'uuid': self.testUuid,
                'channel-id': self.__channelid, 'test-replay-id': self.__replayid }

    def to_notif_json(self, value={}, testInfo={}):
        """
        """
        pass
        
    def to_notif(self, value = '', testInfo={}):
        """
        To notif

        @param address:
        @type address:
        """
        self.__nbline += 1
        try:
            if len(testInfo):
                value.update( testInfo )
            else:
                value.update( self.getTestInfo() )

            # log to header
            if value['event'] in [EVENT_SCRIPT_STARTED, EVENT_SCRIPT_STOPPED,
                                  EVENT_TESTGLOBAL_STARTED, EVENT_TESTGLOBAL_STOPPED,
                                  EVENT_TESTPLAN_STARTED, EVENT_TESTPLAN_STOPPED, EVENT_TESTPLAN_SEP, EVENT_TESTPLAN_SEP_TERMINATED,
                                  EVENT_TESTABSTRACT_STARTED, EVENT_TESTABSTRACT_STOPPED, 
                                  EVENT_TESTUNIT_STARTED, EVENT_TESTUNIT_STOPPED,
                                  EVENT_TESTSUITE_STARTED, EVENT_TESTSUITE_STOPPED,
                                  EVENT_TESTCASE_STARTED, EVENT_TESTCASE_STOPPED]:

                value['header-index'] = self.__nbline
                self.to_header(value=value)
                
            if TestSettings.get( 'Trace', 'level' ) == 'DEBUG':
                self.trace( "event sent: %s" % value )

            # open the file and append notification
            f = open('%s/%s' % (self.__path, self.__filename), 'a', 0)
            #f.write(str(value) + '\n')
            
            # pickle the notif and encode in base64
            pickled = cPickle.dumps(value, protocol=PICKLE_VERSION)
            encoded = base64.b64encode(pickled) 
            
            # write and close it
            f.write( encoded + '\n' )
            f.close()
            TCI.instance().notify( data = value)
        except Exception as e:
            self.error( "[to_notif] %s" % str(e) )

    def to_header(self, value=''):
        """
        """
        try:
            f = open('%s/%s' % (self.__path, self.__filename_hdr), 'a', 0)
            
            pickled = cPickle.dumps(value, protocol=PICKLE_VERSION)
            encoded = base64.b64encode(pickled)
            
            # write and close it
            f.write( encoded + '\n' )
            f.close()
        except Exception as e:
            self.error( "[to_header] %s" % str(e) )
            
    def set_final_verdict(self, verdict):
        """
        Set the final verdict
        """
        try:
            f = open('%s/VERDICT_%s' % (self.__path, verdict), 'w', 0)
            f.close()
        except Exception as e:
            self.error( "[set_final_verdict] %s" % str(e) )

    def get_timestamp (self):
        """
        Return a timestamp

        @return:
        @rtype:
        """
        return time.strftime( "%H:%M:%S", time.localtime(time.time())) + ".%4.4d" % int((time.time() * 10000) % 10000)
    
    ############## Global events
    def log_script_started (self, fromlevel='', tolevel='', tid='000', testInfo={}):
        """
        Log script started event
        """
        self.to_notif( { 'event': EVENT_SCRIPT_STARTED, 'timestamp': self.get_timestamp(),
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid }, testInfo=testInfo )

    def log_script_stopped (self, duration=0, finalverdict='UNDEFINED', prjId=0, fromlevel='', tolevel='', testInfo={}):
        """
        Log script stopped event
        """
        self.set_final_verdict(verdict=finalverdict)
        self.to_notif( { 
                        'event': EVENT_SCRIPT_STOPPED,  'timestamp': self.get_timestamp(), 'duration': str(duration),
                         'user-id': self.__userid, 'prj-id': prjId, 'from-level': fromlevel, 'to-level': tolevel 
                     }, testInfo=testInfo )

    ############### Test global events
    def log_testglobal_started(self, fromlevel='', tolevel='', tid='', testInfo={}):
        """
        Log testglobal started event
        """
        self.to_notif({ 'event': EVENT_TESTGLOBAL_STARTED, 'timestamp': self.get_timestamp(),
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid }, testInfo=testInfo)

    def log_testglobal_stopped(self, result, duration=0, nbTs=0, nbTu=0, nbTc=0, prjId=0, fromlevel='', tolevel='', testInfo={}):
        """
        Log testglobal stopped event
        """
        self.setResult(result)
        self.to_notif( { 
                           'event': EVENT_TESTGLOBAL_STOPPED,  'timestamp': self.get_timestamp(), 'result': str(result), 'duration': str(duration), 
                          'nb-ts': nbTs, 'nb-tu': nbTu, 'nb-tc': nbTc, 'user-id': self.__userid, 'prj-id': prjId, 
                          'from-level': fromlevel, 'to-level': tolevel 
                      }, testInfo=testInfo)

    def log_testglobal_info(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}, flagEnd=False, flagBegin=False):
        """
        Log testglobal info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testglobal',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'color': self.INFO_TG, 'color-text': self.INFO_TG_TEXT,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel,
                'flag-end': flagEnd, 'flag-begin': flagBegin
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testglobal_trace(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log testglobal trace event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testglobal',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'from-level': fromlevel, 'to-level': tolevel,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
             } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testglobal_warning(self, message, component, font="normal", bold = False, italic=False,
                                    multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testglobal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testglobal',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'warning', 'color': self.WARNING_TG, 'color-text': self.WARNING_TG_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )

    def log_testglobal_error(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testglobal error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testglobal',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'error', 'color': self.ERROR_TG, 'color-text': self.ERROR_TG_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )

    def log_testglobal_internal(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal testglobal event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testglobal', 'level': 'section', 'from-component': component, 
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT,
                        'font': font, 'italic': italic , 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )


    ############### Test plan events

    def log_testplan_separator(self, testname, fromlevel='', tolevel='', tid='', alias='', testInfo={}):
        """
        Log testplan separator
        """
        self.to_notif(  
                        { 
                            'event': EVENT_TESTPLAN_SEP,
                            'timestamp': self.get_timestamp(),
                            'from-level': fromlevel,
                            'to-level': tolevel, 
                            'test-internal-id': tid, 
                            'testname': testname,
                            'alias': alias
                           }, testInfo=testInfo
                       )

    def log_testplan_separator_terminated(self, testname, fromlevel='', tolevel='', tid='', duration=0, alias='', testInfo={}):
        """
        Log testplan terminated separator
        """
        self.to_notif(  
                        { 
                            'event': EVENT_TESTPLAN_SEP_TERMINATED,
                            'timestamp': self.get_timestamp(),
                            'from-level': fromlevel,
                            'to-level': tolevel,
                            'test-internal-id': tid,
                            'testname': testname,
                            'duration': duration,
                            'alias': alias
                        }, testInfo=testInfo
                      )

    def log_testplan_started(self, fromlevel='', tolevel='', tid='', testInfo={}):
        """
        Log testplan started event
        """
        self.to_notif({ 'event': EVENT_TESTPLAN_STARTED, 'timestamp': self.get_timestamp(),
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid }, testInfo=testInfo)

    def log_testplan_stopped(self, result, duration=0, nbTs=0, nbTu=0, nbTc=0, prjId=0, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testplan stopped event
        """
        self.setResult(result)
        self.to_notif( { 
                          'event': EVENT_TESTPLAN_STOPPED,  'timestamp': self.get_timestamp(), 'result': str(result), 'duration': str(duration),
                          'nb-ts': nbTs, 'nb-tu': nbTu, 'nb-tc': nbTc, 'user-id': self.__userid,
                          'prj-id': prjId, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    def log_testplan_info(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}, flagEnd=False, flagBegin=False):
        """
        Log testplan info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = {
                'event': 'testplan',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'color': self.INFO_TP, 'color-text': self.INFO_TP_TEXT,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel,
                'flag-end': flagEnd, 'flag-begin': flagBegin
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testplan_trace(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log testplan trace event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testplan',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'from-level': fromlevel, 'to-level': tolevel,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testplan_warning(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testplan warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testplan',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'warning', 'color': self.WARNING_TP, 'color-text': self.WARNING_TP_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    def log_testplan_error(self, message, component, font="normal", bold = False, italic=False,
                            multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testplan error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testplan',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'error', 'color': self.ERROR_TP, 'color-text': self.ERROR_TP_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    def log_testplan_internal(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testplan', 'level': 'section', 'from-component': component, 
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT,
                        'font': font, 'italic': italic , 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )
    
    ############### Test abstract events

    def log_testabstract_started(self, fromlevel='', tolevel='', tid='000', alias='', testInfo={}):
        """
        Log testabstract started event
        """
        self.to_notif({ 'event': EVENT_TESTABSTRACT_STARTED, 'timestamp': self.get_timestamp(), 
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid,
                        'alias': alias }, testInfo=testInfo)

    def log_testabstract_stopped(self, result, duration=0, nbTc=0, prjId=0, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testabstract stopped event
        """
        self.setResult(result)
        self.to_notif( { 
                        'event': EVENT_TESTABSTRACT_STOPPED,  'timestamp': self.get_timestamp(), 
                        'result': str(result), 'duration': str(duration),
                        'nb-tc': nbTc, 'user-id': self.__userid, 'prj-id': prjId, 
                        'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )
    
    def log_testabstract_info(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}, flagEnd=False, flagBegin=False):
        """
        Log testabstract info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testabstract',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'color': self.INFO_TS, 'color-text': self.INFO_TS_TEXT,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel,
                'flag-end': flagEnd, 'flag-begin': flagBegin
               } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testabstract_trace(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log testabstract trace event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testabstract',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info',  'from-level': fromlevel, 'to-level': tolevel,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testabstract_warning(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testabstract warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testabstract',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'warning', 'color': self.WARNING_TC, 'color-text': self.WARNING_TC_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'msg-multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )

    def log_testabstract_error(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testabstract error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testabstract',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'error', 'color': self.ERROR_TS, 'color-text': self.ERROR_TS_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    def log_testabstract_internal(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testabstract', 'level': 'section', 'from-component': component, 
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT,
                        'font': font, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    ############### Test unit events

    def log_testunit_started(self, fromlevel='', tolevel='', tid='000', alias='', testInfo={}):
        """
        Log testsuite started event
        """
        self.to_notif({ 'event': EVENT_TESTUNIT_STARTED, 'timestamp': self.get_timestamp(), 
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid,
                        'alias': alias }, testInfo=testInfo)

    def log_testunit_stopped(self, result, duration=0, nbTc=0, prjId=0, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite stopped event
        """
        self.setResult(result)
        self.to_notif( { 
                        'event': EVENT_TESTUNIT_STOPPED,  'timestamp': self.get_timestamp(), 
                        'result': str(result), 'duration': str(duration),
                        'nb-tc': nbTc, 'user-id': self.__userid, 'prj-id': prjId, 
                        'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )
    
    def log_testunit_info(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}, flagEnd=False, flagBegin=False):
        """
        Log testsuite info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testunit',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'color': self.INFO_TS, 'color-text': self.INFO_TS_TEXT,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel,
                'flag-end': flagEnd, 'flag-begin': flagBegin
               } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testunit_trace(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log testsuite trace event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testunit',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info',  'from-level': fromlevel, 'to-level': tolevel,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testunit_warning(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testunit',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'warning', 'color': self.WARNING_TC, 'color-text': self.WARNING_TC_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'msg-multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                     }, testInfo=testInfo )

    def log_testunit_error(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testunit',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'error', 'color': self.ERROR_TS, 'color-text': self.ERROR_TS_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    def log_testunit_internal(self, message, component, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testunit', 'level': 'section', 'from-component': component, 
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT,
                        'font': font, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                      }, testInfo=testInfo )

    ############### Test suite events

    def log_testsuite_started(self, fromlevel='', tolevel='', tid='000', alias='', testInfo={}):
        """
        Log testsuite started event
        """
        self.to_notif({ 'event': EVENT_TESTSUITE_STARTED, 'timestamp': self.get_timestamp(),
                        'from-level': fromlevel, 'to-level': tolevel, 'test-internal-id': tid,
                        'alias': alias }, testInfo=testInfo)

    def log_testsuite_stopped(self, result, duration=0, nbTc=0, prjId=0, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite stopped event
        """
        self.setResult(result)
        self.to_notif( { 
                        'event': EVENT_TESTSUITE_STOPPED,  'timestamp': self.get_timestamp(), 'result': str(result),
                         'duration': str(duration), 'nb-tc': nbTc, 'user-id': self.__userid, 'prj-id': prjId,
                         'from-level': fromlevel, 'to-level': tolevel
                       }, testInfo=testInfo)
    
    def log_testsuite_info(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}, flagEnd=False, flagBegin=False):
        """
        Log testsuite info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testsuite',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'color': self.INFO_TS, 'color-text': self.INFO_TS_TEXT,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel,
                'flag-end': flagEnd, 'flag-begin': flagBegin
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif( tpl, testInfo=testInfo )

    def log_testsuite_trace(self, message, component, color = None, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log testsuite trace event

        @param message:
        @type message:

        @param component:
        @type component:

        @param color:
        @type color:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 
                'event': 'testsuite',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                'from-component': component, 'level': 'info', 'from-level': fromlevel, 'to-level': tolevel,
                'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
              } 
        if color is not None:
            tpl.update({'color': color})
        self.to_notif(tpl, testInfo=testInfo )

    def log_testsuite_warning(self, message, component, font="normal", bold = False, italic=False,
                                    multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testsuite',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'warning', 'color': self.WARNING_TC, 'color-text': self.WARNING_TC_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'msg-multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
        }, testInfo=testInfo )

    def log_testsuite_error(self, message, component, font="normal", bold = False, italic=False, 
                                multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testsuite error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( { 
                        'event': 'testsuite',  'timestamp': self.get_timestamp(), 'short-msg': str(message), 
                        'from-component': component, 'level': 'error', 'color': self.ERROR_TS, 'color-text': self.ERROR_TS_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
        }, testInfo=testInfo )

    def log_testsuite_internal(self, message, component, font="normal", bold = False, italic=False,
                                    multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testsuite', 'level': 'section','from-component': component, 
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT,
                        'font': font, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
        }, testInfo=testInfo )

    ############### Test case events
    def log_testcase_started(self, id_, name, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testcase started event

        @param id_:
        @type id_:

        @param name:
        @type name:
        """
        self.to_notif({  
                            'event': EVENT_TESTCASE_STARTED, 'timestamp': self.get_timestamp(),
                            'tc_id': id_ , 'name': name, 'from-level': fromlevel, 'to-level': tolevel
        }, testInfo=testInfo)

    def log_testcase_stopped(self, id_, result, duration=0, prjId=0, fromlevel='', tolevel='', testInfo={} ):
        """
        Log testcase stopped event

        @param id_:
        @type id_:

        @param result:
        @type result:

        @param duration:
        @type duration:
        """
        self.setResult(result)
        self.to_notif( { 
                        'event': EVENT_TESTCASE_STOPPED,  'timestamp': self.get_timestamp(),
                        'tc_id': id_, 'result': str(result), 'duration': str(duration),
                        'user-id': self.__userid, 'prj-id': prjId, 'from-level': fromlevel, 'to-level': tolevel
        }, testInfo=testInfo)
    
    def log_testcase_info(self, message, component, tcid, type_ = None, color_ = None, font="normal", 
                            bold = False, italic=False, multiline=False, typeMsg='', fromlevel='', tolevel='',
                            testInfo={}, flagEnd=False, flagBegin=False ):
        """
        Log testcase info event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param address:
        @type address:

        @param address:
        @type address:

        @param address:
        @type address:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        tpl = { 'event': 'testcase', 'level': 'info', 'from-component': component, 'type-msg': typeMsg,
                'timestamp': self.get_timestamp(), 'short-msg': str(message), 'tc_id': tcid, 'color': self.INFO_TC, 
                'bold': bold , 'font': font, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 
                'to-level': tolevel, 'flag-end': flagEnd, 'flag-begin': flagBegin }
        if type_ is not None:
            tpl.update( {'type':type_} )
        if color_ is not None:
            tpl.update( {'color':color_} )
        self.to_notif( tpl, testInfo=testInfo)
    
    def log_testcase_error(self, message, component, tcid, type_ = None, font="normal", bold = False, italic=False, 
                                multiline=False, typeMsg='', fromlevel='', tolevel='', testInfo={}  ):
        """
        Log testcase error event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'error','from-component': component, 'type': type_,
                        'timestamp': self.get_timestamp(), 'short-msg': str(message), 'type-msg': typeMsg,
                        'color': self.ERROR_TC, 'color-text': self.ERROR_TC_TEXT, 'tc_id': tcid, 
                        'bold': bold, 'font': font, 'italic': italic, 'multiline': multiline,
                        'from-level': fromlevel, 'to-level': tolevel 
        }, testInfo=testInfo )

    def log_testcase_warning(self, message, component, tcid, type_ = None, font="normal", bold = False, italic=False,
                                    multiline=False, typeMsg='', fromlevel='', tolevel='', testInfo={}  ):
        """
        Log testcase warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'warning','from-component': component, 'type': type_,
                        'timestamp': self.get_timestamp(), 'short-msg': str(message), 'type-msg': typeMsg,
                        'bold': bold, 'color': self.WARNING_TC, 'color-text': self.WARNING_TC_TEXT,
                        'tc_id': tcid, 'font': font, 'italic': italic, 'multiline': multiline,
                        'from-level': fromlevel, 'to-level': tolevel 
        }, testInfo=testInfo )

    def log_testcase_trace(self, message, component, tcid, type_ = None, font="normal", bold = False, italic=False,
                                multiline=False, typeMsg='', fromlevel='', tolevel='', testInfo={}  ):
        """
        Log testcase trace event 

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'debug','from-component': component, 'type': type_,
                        'timestamp': self.get_timestamp(), 'short-msg': str(message), 'type-msg': typeMsg,
                        'bold': bold, 'tc_id': tcid, 'font': font, 'italic': italic, 'multiline': multiline,
                        'from-level': fromlevel, 'to-level': tolevel 
        }, testInfo=testInfo )

    ####
    def log_testcase_internal(self, message, component, tcid, type_ = None, font="normal", bold = False,
                                    italic=False, multiline=False, fromlevel='', tolevel='', testInfo={} ):
        """
        Log internal warning event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'section', 'from-component': component, 'type': type_,
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.INTERNAL, 'color-text': self.INTERNAL_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
                        'tc_id': tcid, 'font': font, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )

    ############### State events
    def log_state(self, message, component, tcid, font="normal", bold = False, italic=False, multiline=False, fromlevel='', 
                        tolevel='', testInfo={} ):
        """
        Log state event

        @param message:
        @type message:

        @param component:
        @type component:

        @param tcid:
        @type tcid:

        @param type_:
        @type type_:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'state', 'from-component': component, 'type-msg': 'state',
                        'timestamp': self.get_timestamp(), 'short-msg': str(message),
                        'bold': bold, 'color': self.STATE, 'color-text': self.STATE_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
                        'tc_id': tcid, 'font': font, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )

    ############### rcv/snd events
    def log_rcv (self, shortMsg, dataMsg, typeMsg, fromComponent, tcid, font="normal", bold = False, italic=False, multiline=False, 
                    fromlevel='', tolevel='', testInfo={}):
        """
        Log received event

        @param shortMsg:
        @type shortMsg:

        @param dataMsg:
        @type dataMsg:

        @param typeMsg:
        @type typeMsg:

        @param fromComponent:
        @type fromComponent:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                    'event': 'testcase', 'level': 'received', 'short-msg': shortMsg, 
                    'from-component': fromComponent, 'timestamp': self.get_timestamp(),
                    'data-msg': dataMsg, 'type-msg': typeMsg, 'tc_id': tcid,
                    'color': self.PAYLOAD, 'color-text': self.PAYLOAD_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
                    'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo)
    
    def log_snd (self, shortMsg, dataMsg, typeMsg, fromComponent, tcid, font="normal", bold = False, italic=False, 
                    multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log send event

        @param shortMsg:
        @type shortMsg:

        @param dataMsg:
        @type dataMsg:

        @param typeMsg:
        @type typeMsg:

        @param fromComponent:
        @type fromComponent:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                        'event': 'testcase', 'level': 'send', 'from-component': fromComponent, 'short-msg': shortMsg, 
                        'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': typeMsg,  'tc_id': tcid,
                        'color': self.PAYLOAD, 'color-text': self.PAYLOAD_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )
    
    ############### Steps events
    def log_step_started (self, fromComponent, dataMsg, shortMsg, tcid, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log step started event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                    'event': 'testcase', 'level': 'step-started', 'from-component': fromComponent,
                    'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'step', 'from-level': fromlevel, 'to-level': tolevel,
                    'short-msg': shortMsg, 'tc_id': tcid, 'color': self.STEP_STARTED, 'color-text': self.STEP_STARTED_TEXT,
                    'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )

    def log_step_failed (self, fromComponent, dataMsg, shortMsg, tcid, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log step failed event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                    'event': 'testcase', 'level': 'step-failed', 'from-component': fromComponent,
                    'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'step', 'from-level': fromlevel, 'to-level': tolevel,
                    'short-msg': shortMsg, 'tc_id': tcid, 'color': self.STEP_FAILED, 'color-text': self.STEP_FAILED_TEXT,
                    'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo )

    def log_step_passed (self, fromComponent, dataMsg, shortMsg, tcid, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log step passed event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
                    'event': 'testcase', 'level': 'step-passed', 'from-component': fromComponent,
                    'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'step', 'from-level': fromlevel, 'to-level': tolevel,
                    'short-msg': shortMsg, 'tc_id': tcid, 'color': self.STEP_PASSED, 'color-text': self.STEP_PASSED_TEXT, 
                    'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo )

    ############### Timers events
    def log_timer_started (self, fromComponent, dataMsg, tcid, expire, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log timer started event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        try:
            sec = "second"
            if int(expire) > 1:
                sec = "seconds"
        except Exception as e:
            raise TestLoggerException("timer initialization: integer or float expected")

        shortmsg ="Timer started, expires in %s %s" % (expire,sec)
        self.to_notif( {
                    'event': 'testcase', 'level': 'timer-started', 'from-component': fromComponent,
                    'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'timer', 'from-level': fromlevel, 'to-level': tolevel,
                    'short-msg': shortmsg, 'tc_id': tcid, 'color': self.TIMER, 'color-text': self.TIMER_TEXT,
                    'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo )

    def log_timer_restarted (self, fromComponent, dataMsg, tcid, expire, font="normal", bold = False, italic=False,
                                    multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log timer restarted event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        try:
            sec = "second"
            if int(expire) > 1:
                sec = "seconds"
        except Exception as e:
            raise TestLoggerException("timer initialization: integer or float expected")

        shortmsg ="Timer re-started, expires in %s %s" % (expire,sec)
        self.to_notif( {
                    'event': 'testcase', 'level': 'timer-started', 'from-component': fromComponent,
                    'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'timer', 'from-level': fromlevel, 'to-level': tolevel,
                    'short-msg': shortmsg, 'tc_id': tcid, 'color': self.TIMER, 'color-text': self.TIMER_TEXT,
                    'font': font, 'bold': bold, 'italic': italic , 'multiline': multiline
        }, testInfo=testInfo )

    def log_timer_exceeded (self, fromComponent, dataMsg, tcid, font="normal", bold = False, italic=False, 
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log timer exceeded event

        @param fromComponent:
        @type fromComponent:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'timer-exceeded', 'from-component': fromComponent, 
            'timestamp': self.get_timestamp(), 'short-msg': 'Timer exceeded', 'data-msg': dataMsg, 'type-msg': 'timer',
            'tc_id': tcid, 'color': self.TIMER, 'color-text': self.TIMER_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )

    def log_timer_stopped (self, fromComponent, dataMsg, tcid, font="normal", bold = False, italic=False,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log timer stopped event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'timer-stopped', 'from-component': fromComponent,  'type-msg': 'timer',
            'timestamp': self.get_timestamp(), 'short-msg': 'Timer stopped', 'data-msg': dataMsg, 'tc_id': tcid,
            'color': self.TIMER, 'color-text': self.TIMER_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo)

    def log_timer_info(self, fromComponent, dataMsg, tcid, font="normal", bold = False, italic=False,
                            multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log timer info event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'timer-info', 'from-component': fromComponent,  'type-msg': 'timer',
            'timestamp': self.get_timestamp(), 'short-msg': 'Timer info', 'data-msg': dataMsg, 'tc_id': tcid,
            'color': self.TIMER, 'color-text': self.TIMER_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo)

    ############### Match events
    def log_match_started (self, fromComponent, dataMsg, tcid, expire, font="normal", bold = False, italic=False, index=0,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log match started event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param expire:
        @type expire:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        try:
            sec = "second"
            if int(expire) > 1:
                sec = "seconds"
        except Exception as e:
            raise TestLoggerException("match initialization: integer or float expected")

        #shortmsg = 'Timer started, expires in %s %s' % (expire,sec)
        shortmsg ="Wait the expected template(%s) for %s %s" % (index, expire,sec)
        self.to_notif( {
                        'event': 'testcase', 'level': 'match-started', 'from-component': fromComponent,
                        'timestamp': self.get_timestamp(), 'data-msg': dataMsg, 'type-msg': 'match',
                        'short-msg': shortmsg, 'tc_id': tcid, 'color': self.MATCH, 'color-text': self.MATCH_TEXT,
                        'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline, 'from-level': fromlevel, 'to-level': tolevel
                        }, testInfo=testInfo )

    def log_match_exceeded (self, fromComponent, tcid, font="normal", bold = False, italic=False,
                                    multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log match exceeded event

        @param fromComponent:
        @type fromComponent:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'match-exceeded', 'from-component': fromComponent, 
            'timestamp': self.get_timestamp(), 'short-msg': 'Waiting time exceeded', 'type-msg': 'match',
            'tc_id': tcid, 'color': self.MATCH, 'color-text': self.MATCH_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline 
        }, testInfo=testInfo )

    def log_match_stopped (self, fromComponent, dataMsg, tcid, font="normal", bold = False, italic=False, index=0,
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log match stopped event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'match-stopped', 'from-component': fromComponent,  'type-msg': 'match-received',
            'timestamp': self.get_timestamp(), 'short-msg': 'Template(%s) match' % index, 'data-msg': dataMsg, 'tc_id': tcid,
            'color': self.MATCH, 'color-text': self.MATCH_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo)

    def log_match_info(self, fromComponent, dataMsg, tcid, font="normal", bold = False, italic=False, index=0, 
                                multiline=False, fromlevel='', tolevel='', testInfo={}):
        """
        Log match info event

        @param fromComponent:
        @type fromComponent:

        @param dataMsg:
        @type dataMsg:

        @param tcid:
        @type tcid:

        @param font:
        @type font:

        @param bold:
        @type bold:

        @param italic:
        @type italic:
        """
        self.to_notif( {
            'event': 'testcase', 'level': 'match-info', 'from-component': fromComponent,  'type-msg': 'match-received',
            'timestamp': self.get_timestamp(), 'short-msg': 'Template(%s) mismatch, continues waiting' % index, 'data-msg': dataMsg, 'tc_id': tcid,
            'color': self.MISMATCH, 'color-text': self.MISMATCH_TEXT, 'from-level': fromlevel, 'to-level': tolevel,
            'font': font, 'bold': bold, 'italic': italic, 'multiline': multiline
        }, testInfo=testInfo)

    def error (self, err):
        """
        Log error

        @param err:
        @type err:
        """
        timestamp = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time())) + ".%4.4d" % int((time.time() * 10000) % 10000)
        sys.stderr.write( "%s - ERROR - %s - %s\n" % ( timestamp, self.__class__.__name__, err) )

    def trace (self, msg):
        """
        Trace message

        @param err:
        @type err:
        """
        timestamp = time.strftime( "%Y-%m-%d %H:%M:%S", time.localtime(time.time())) + ".%4.4d" % int((time.time() * 10000) % 10000)
        sys.stdout.write( "%s - TRACE - %s - %s\n" % ( timestamp, self.__class__.__name__, msg) )

###########################################################
TestLogger = None

def instance():
    """
    Return the instance

    @return:
    @rtype:
    """
    if TestLogger:
        return TestLogger

def initialize( path, name, user_ , testname_, id_, replay_id_, task_id_, userid_, channelid_=False):
    """
    Initialize

    @param path:
    @type path:

    @param name:
    @type name:

    @param user_:
    @type user_:

    @param testname_:
    @type testname_:

    @param id_:
    @type id_:

    @param replay_id_:
    @type replay_id_:

    @param task_id_:
    @type task_id_:
    """
    TestSettings.initialize()
    global TestLogger
    TestLogger = TestLoggerXml(path = path, name = name, user_ = user_, 
                    testname_ = testname_, id_ = id_, replay_id_ = replay_id_ ,
                        task_id_ = task_id_, userid_ = userid_, channelid_=channelid_)

def finalize():
    """
    Finalize
    """
    global TestLogger
    if TestLogger:
        TestLogger = None
    TestSettings.finalize()
        
