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

import MySQLdb
import time
import datetime
import pickle

import threading 
import os
import parser
import compiler
import ConfigParser

import uuid
import sys
import zlib
import signal
import base64
import shutil
import copy
import hashlib

try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json

import Common
import TestModel
import SubTestModel
import EventServerInterface as ESI
import TestServerInterface as TSI
import StatsManager
import RepoManager
import RepoArchives
import RepoLibraries
import RepoAdapters
import DbManager
import StorageDataAdapters
import UsersManager
import Context
import ProjectsManager
# new in v10.1
import AgentsManager
import ProbesManager
# end of new

from Libs import Scheduler, Settings, Logger
import Libs.FileModels.TestResult as TestResult


TASKS_RUNNING           = 0
TASKS_WAITING           = 1
TASKS_HISTORY           = 2

STATE_INIT              = 'INIT'
STATE_WAITING           = 'WAITING'
STATE_DISABLED          = 'DISABLED'
STATE_RUNNING           = 'RUNNING'
STATE_COMPLETE          = 'COMPLETE'
STATE_ERROR             = 'ERROR'
STATE_FINISHED          = 'FINISHED'

STATE_KILLING           = 'KILLING'
STATE_KILLED            = 'KILLED'

STATE_CANCELLING        = 'CANCELLING'
STATE_CANCELLED         = 'CANCELLED'

STATE_UPDATING          = 'UPDATING'


SIGNAL_KILL=9

SCHED_TYPE_UNDEFINED    =   -2
SCHED_EVERY_X           =   6
SCHED_WEEKLY            =   7
SCHED_NOW_MORE          =   8
SCHED_QUEUE             =   9
SCHED_QUEUE_AT          =   10

MONDAY                  =   0
TUESDAY                 =   1
WEDNESDAY               =   2
THURSDAY                =   3
FRIDAY                  =   4
SATURDAY                =   5
SUNDAY                  =   6

#                                                          ERROR   <----------------------------------------------------------------|
#                                                            ^                                                                      |
#                                                            |                                                                      |
#    ---------------                      -- enable -->   ------------                                                              |
#   | enable   task | ----> DISABLED <--->|              | update task |-|                                                          |
#    ---------------                      <- disable --   ------------   |                                                          |   
#                                                            ^           |                                                          |
#                                                            |           |                                                          |
#                                                         UPDATING       |                                                          |
#                                                            ^           |  updated                                                 |
#                                                            |           |                                                          |
#                                                            |           |                                                          |
#                                                         ---------      |                                                          |
#                                                       |  update |      |                                                          |
#                                                         ---------      |                                                          |
#                                                            ^   ________|                                                          |
#                                                            |  |                                                                   |
#    ---------------                -----------------        |  v             ---------         ----------                   ----------------
#   | schedule task | --> INIT --> | prepare env tmp | --> WAITING ---------> | prepare | -----| add task |---> RUNNING --> | test execution | -----> COMPLETE
#    ---------------                -----------------        |                ---------         ----------                   ----------------
#                                   |                        |                  |                                                   | 
#                                   |                        v                  |                                                   |
#                                   |                    ---------              |                                                   v
#                                   |                   |  cancel |             |                                                --------   
#                                   |                    ---------              |                                               |  kill  |
#                                   |                        |                  |                                                -------- 
#                                   |                        |                  |                                                   |
#                                   |                        v                  |                                                   v
#                                   |                    CANCELLING             |                                                 KILLING
#                                   |                        |                  |                                                   |
#                                   |                        v                  |                                                   v
#                                   |                    -------------          |                                             ----------------
#                                   |             |-----| remove task |         |                                            | kill processes |-----> KILLED
#                                   |             |      -------------          |                                             ----------------
#                                   |             |         |                   |                                                   |
#                                   |             |         |                   |                                                   |
#                                   |             |         |-> CANCELLED       |                                                   |
#                                   |             v                             |                                                   |
#                                   |                                           |                                                   |
#                                   |------->   ERROR   <-----------------------|---------------------------------------------------|
#                                                                                                                                   
#                                                                                                                                   

EMPTY_VALUE = ''

GenBaseId = 0
GenBaseIdMutex = threading.RLock()

def getGroupId():
    """
    Generates a new unique ID.

    @return:
    @rtype:
    """
    global GenBaseId
    GenBaseIdMutex.acquire()
    GenBaseId += 1
    ret = GenBaseId
    GenBaseIdMutex.release()
    return ret


class Task(Logger.ClassLogger):
    def __init__(self, testData, testName, testPath, testUser, testId, testBackground, taskEnabled=True, withoutProbes=False,
                    debugActivated=False, withoutNotif=False, noKeepTr=False, testUserId=0, testProjectId=0, stepByStep=False,
                    breakpoint=False, runSimultaneous=False, channelId=False):
        """
        Construc test class

        @param testData:
        @type testData:

        @param testName:
        @type testName:

        @param testPath:
        @type testPath:

        @param testUser:
        @type testUser:

        @param testId:
        @type testId:

        @param testBackground:
        @type testBackground:
        """
        self.mutex = threading.RLock()

        self.channelId = channelId
        self.schedId = None
        self.testName = testName
        self.testPath = testPath
        if len(self.testPath):
            if not self.testPath.startswith("/"):
                self.testPath = "/%s" % self.testPath
            
        self.userName = testUser
        self.userId = testUserId
        self.projectId = testProjectId

        self.dataTest = testData
        self.testId = testId
        self.background = testBackground
        self.verdict = 'UNDEFINED'
        self.enabled = taskEnabled
        self.withoutProbes = withoutProbes
        self.noKeepTr = noKeepTr
        self.debugActivated = debugActivated
        self.withoutNotif = withoutNotif
        self.stepByStep = stepByStep
        self.breakpoint = breakpoint
        self.runSimultaneous = runSimultaneous

        self.testType = 'TestSuite'
        if 'testglobal' in self.dataTest:
            self.testType = 'TestGlobal'
        if 'testplan' in self.dataTest:
            self.testType = 'TestPlan'
        if 'testunit' in self.dataTest:
            self.testType = 'TestUnit'

        
        self.replayId = 0
        self.recurId = 0
        
        self.schedAt = 0
        self.schedType = SCHED_TYPE_UNDEFINED
        self.schedArgs = ( 0, 0, 0, 0, 0, 0 ) #Y,M,D,H,M,S
        self.schedFrom = ( 0, 0, 0, 0, 0, 0 ) #Y,M,D,H,M,S
        self.schedTo = ( 0, 0, 0, 0, 0, 0 ) #Y,M,D,H,M,S
        self.schedNb = -1
        
        self.resultsStats = { "passed": 0, "failed": 0, "undefined": 0}
        
        self.prepareTime = 0
        self.prepared = False
        self.syntaxOK = False
        self.startTime = "N/A"
        self.stopTime = "N/A"
        self.duration = "N/A"
        self.lastError = None
        
        self.tpid = None
        self.eventReg = None
        self.removeFromContext = True

        self.groupId = 0
        
        # Universally Unique IDentifiers
        self.taskUuid = "%s" % uuid.uuid4()
        self.state = self.setState(STATE_INIT)
    
    def saveTestDescr(self, envTmp=False):
        """
        """
        maxRun = "unlimited"
        if self.schedType == Scheduler.SCHED_NOW: 
            maxRun = 1
        else:
            if self.schedNb != -1: 
                maxRun = self.schedNb

        test = { "name": self.testName, "start-at": self.startTime }
        statistics = { "total": "%s" % maxRun, 'count': "%s" % (self.recurId+1),
                        'passed': "%s" % self.resultsStats["passed"], 'failed': "%s" % self.resultsStats["failed"], 
                        'undefined': "%s" % self.resultsStats["undefined"] }
        testDescr = { "test":  test, "user": self.userName, "statistics": statistics }
        f = open( "%s/DESCRIPTION" % self.getPath(envTmp=envTmp), 'w' )
        f.write( "%s" % json.dumps(testDescr) )
        f.close()
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="TSK - %s" % txt)

    def setGroupId(self, groupId):
        """
        Set the id of tasks group in queue
        """
        self.groupId = groupId

    def setSyntaxOK(self):
        """
        set syntax as ok
        """
        self.trace( "Syntax OK" )
        self.syntaxOK = True
        return self.syntaxOK
        # return self.initPrepare()

    def runAgain(self):
        """
        Check the counter of run
        """
        if self.schedNb == -1:
            return True
        elif self.recurId < ( self.schedNb - 1 ) :
            return True
        else:
            return False

    def alwaysRun(self):
        """
        Check if always in the interval (from/to)
        """
        if self.schedType == SCHED_EVERY_X:
            if self.schedTo == self.schedFrom:
                return True
            else:
                
                cur_dt = time.localtime()
                now_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, cur_dt.tm_hour, cur_dt.tm_min, 0, 0)

                toY, toM, toD, toH, toMn, toS = self.schedTo
                to_dt = datetime.datetime(toY, toM, toD, toH, toMn, 0, 0)
                
                if now_dt >= to_dt:   
                    y, m, d, h, mn, s = self.schedArgs
                    fromY, fromM, fromD, fromH, fromMn, fromS = self.schedFrom

                    # drift the interval on one day
                    from_dt = datetime.datetime(fromY, fromM, fromD, fromH, fromMn, 0, 0) +  datetime.timedelta(hours=24,minutes=0, seconds=0) 
                    to_dt = to_dt + datetime.timedelta(hours=24,minutes=0, seconds=0) 

                    next_dt = from_dt
                    self.schedAt = time.mktime(next_dt.timetuple())  -  60*60*h - 60*mn - s
                    self.schedFrom = ( from_dt.year, from_dt.month, from_dt.day, from_dt.hour, from_dt.minute, 0 )
                    self.schedTo = ( to_dt.year, to_dt.month, to_dt.day, to_dt.hour, to_dt.minute, 0 )

                    self.trace( 'Next from: %s' % str(self.schedFrom) )
                    self.trace( 'Next to: %s' % str(self.schedTo) )
                    return False
                else:
                    return True
        else:
            return True

    def setEventReg(self, event):
        """
        Save the event created by the scheduler

        @param event:
        @type event:
        """
        self.eventReg = event

    def toTuple(self, withId=False, withGroupId=False):
        """
        Return the task as tuple 

        @param withId:
        @type withId: boolean
        """
        if withId:
            if withGroupId:
                return ( self.schedId, self.schedType, str(self.schedArgs), str(self.schedAt), self.getTaskName(), str(self.userName),
                            str(self.startTime), str(self.duration), str(self.state),  self.schedNb, self.recurId, self.enabled, self.withoutProbes,
                            self.withoutNotif, self.noKeepTr, self.userId, self.projectId,
                                str(self.schedFrom), str(self.schedTo), self.groupId )
            else:
                # Called to add in backup 
                return ( self.schedId, self.schedType, str(self.schedArgs), str(self.schedAt), self.getTaskName(), str(self.userName),
                            str(self.startTime), str(self.duration), str(self.state),  self.schedNb, self.recurId, self.enabled, self.withoutProbes,
                            self.withoutNotif, self.noKeepTr, self.userId, self.projectId,
                                str(self.schedFrom), str(self.schedTo) )
        else:
            # Called to add in the history
            return ( self.schedType, str(self.schedArgs), str(self.schedAt), self.getTaskName(), str(self.userName), str(self.startTime), str(self.duration), 
                    str(self.state), self.projectId )

    def getId(self):
        """
        Get the scheduler event id
        """
        return self.schedId

    def setId(self, taskId):
        """
        Set the scheduler event id

        @param taskId:
        @type taskId:
        """
        self.schedId = taskId

    def setPrepared(self):
        """
        """
        self.prepared = True

    def getSchedTime(self):
        """
        Get the schedulation time
        """
        return self.schedAt

    def getTaskName(self):
        """
        Get the task name
        """
        ret = ''
        if self.testPath != "":
            ret =  self.testPath
        else:
            ret = self.testName
        return ret

    def setReplayId (self):
        """
        Set the replay id
        """
        self.removeFinishedFile()
        self.replayId += 1

    def initialize(self, runAt, runType, runNb, runEnabled, withoutProbes, debugActivated, withoutNotif, noKeepTr,
                        runFrom=( 0, 0, 0, 0, 0, 0 ), runTo=( 0, 0, 0, 0, 0, 0 ) ):
        """
        Initialize the task start time

        @param runAt:
        @type runAt:

        @param runType:
        @type runType:
        """
        runAt = tuple(runAt)
        self.enabled = runEnabled
        self.withoutProbes = withoutProbes
        self.debugActivated = debugActivated
        self.withoutNotif = withoutNotif
        self.noKeepTr = noKeepTr
        timestamp = 0
        y, m, d, h, mn, s = runAt
        fromY, fromM, fromD, fromH, fromMn, fromS = runFrom
        toY, toM, toD, toH, toMn, toS = runTo
        self.schedNb = int(runNb)
        self.schedType = runType
        self.schedArgs = ( 0, 0, 0, 0, 0, 0 )
        self.schedFrom = runFrom
        self.schedTo = runTo
        
        if runType ==  Scheduler.SCHED_DAILY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, h, mn, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, 0, h, mn, s)
            
        elif runType ==  Scheduler.SCHED_HOURLY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, cur_dt.tm_hour, mn, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, 0, 0, mn, s)
            
        elif runType ==  Scheduler.SCHED_EVERY_MIN:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, cur_dt.tm_hour, cur_dt.tm_min, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, 0, 0, 0, s)
            
        elif runType ==  Scheduler.SCHED_EVERY_SEC:
            self.error('not implemented')
            
        elif runType ==  Scheduler.SCHED_AT:
            dt = datetime.datetime(y, m, d, h, mn, s, 0)
            timestamp = time.mktime(dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( y, m, d, h, mn, s)
            
        elif runType ==  Scheduler.SCHED_IN:
            timestamp = time.time() + s
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, 0, 0, 0, s)
            
        elif runType ==  Scheduler.SCHED_NOW:
            self.trace('init start time: nothing todo')
            
        elif runType ==  SCHED_QUEUE:
            self.trace('init start time in queue: nothing todo')
            
        elif runType ==  SCHED_QUEUE_AT:
            dt = datetime.datetime(y, m, d, h, mn, s, 0)
            timestamp = time.mktime(dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( y, m, d, h, mn, s)
            
        # BEGIN new schedulation type in 5.0.0
        elif runType ==  SCHED_NOW_MORE:
            if sum(runFrom):
                dt = datetime.datetime(fromY, fromM, fromD, fromH, fromMn, fromS, 0)
                timestamp = time.mktime(dt.timetuple())
                self.schedAt = timestamp
            else:
                pass
        # END

        # BEGIN new schedulation type in 3.1.0
        elif runType ==  SCHED_EVERY_X:   
            cur_dt = time.localtime()

            from_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, fromH, fromMn, 0, 0)
            if fromH > toH: # fix in v12, sched from 23:00 to 07:00 not working
                to_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday+1, toH, toMn, 0, 0)
            else:
                to_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, toH, toMn, 0, 0)
                
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, cur_dt.tm_hour, cur_dt.tm_min, cur_dt.tm_sec, 0)
            self.trace("Current next time: %s" % next_dt.isoformat() )

            if from_dt == to_dt:
                if not Settings.getInt( 'TaskManager', 'everyminx-run-immediately' ):
                    next_dt += datetime.timedelta(hours=h,minutes=mn, seconds=s)
                self.trace("No interval, new next time: %s" % next_dt.isoformat() )
            else:
                self.trace( "Ajust next time according to the interval" )
                # start greather than current date ?
                if from_dt > next_dt:
                    next_dt = from_dt
                # shit the interval of one day
                else:
                    from_dt += datetime.timedelta(hours=24,minutes=0, seconds=0) 
                    to_dt += datetime.timedelta(hours=24,minutes=0, seconds=0) 
                    next_dt = from_dt
            
            self.trace( "Final next time at: %s" % next_dt.isoformat() )
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, 0, h, mn, s)
            self.schedFrom = ( from_dt.year, from_dt.month, from_dt.day, from_dt.hour, from_dt.minute, 0 )
            self.schedTo = ( to_dt.year, to_dt.month, to_dt.day, to_dt.hour, to_dt.minute, 0 )

            self.trace( "Interval begin at: %s" % str(self.schedFrom) )
            self.trace( "Interval ending at: %s" % str(self.schedTo) )
        # END

        # BEGIN new schedulation type in 3.2.0
        elif runType == SCHED_WEEKLY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday, h, mn, s, 0)
            delta = datetime.timedelta(days=1)
            while next_dt.weekday() != d:
                next_dt = next_dt + delta
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = ( 0, 0, d, h, mn, s)
        # END
        
        else:
            self.error('should not be happen')
        return timestamp

    def isSuccessive(self):
        """
        Returns True if the task is successive, False otherwise

        @return: recursive or not
        @rtype: boolean
        """
        if self.schedType ==  SCHED_NOW_MORE:
            return True
        else:
            return False

    def isRecursive(self):
        """
        Returns True if the task is recursive, False otherwise

        @return: recursive or not
        @rtype: boolean
        """
        if self.schedType == SCHED_QUEUE or self.schedType == SCHED_QUEUE_AT:
            return False
        else:
            if self.schedType > Scheduler.SCHED_IN:
                return True
            else:
                return False

    def isPostponed(self):
        """
        Returns True is postponed, False otherwise

        @return: postponed or no
        @rtype: boolean
        """
        if self.schedType == Scheduler.SCHED_AT or self.schedType == Scheduler.SCHED_IN :
            return True
        else:
            return False

    def completeId(self, withTestPath=False):
        """
        Returns complete identifier
        Concatenation of variables: self.initTime, base64(self.testName) and self.userName
        With the following separator: .
        Example: 123622.770.dG1wMw==.admin

        @return: task id
        @rtype: string
        """
        sep = "."
        
        testidentifier = self.testName
        if withTestPath:
            if self.testPath != "": testidentifier = self.testPath # remove in v16

        # prepare a unique id for the test
        ret = []
        ret.append( time.strftime("%Y-%m-%d_%H:%M:%S", time.localtime(self.prepareTime)) ) #  + \
                    # ".%6.6d" % int((self.prepareTime * 1000000)% 1000000  ) )
        ret.append( self.taskUuid )
        ret.append( base64.b64encode(testidentifier.encode("utf8")) )
        ret.append( self.userName )
        
        # join with . separator and return it
        return sep.join(ret)

    def toDict (self):
        """
        To dict data type

        @return:
        @rtype: dict
        """
        ret = {}
        ret['id'] = self.schedId
        if self.testPath != "":
            ret['name'] =  self.testPath
        else:
            ret['name'] = self.testName
        ret['user'] = self.userName
        ret['state'] = self.state
        ret['sched-at'] = self.schedAt
        ret['start-at'] = self.startTime
        ret['stop-at'] = self.stopTime
        ret['duration'] = self.duration
        ret['recursive'] = self.isRecursive()
        ret['project-id'] = self.projectId
        return ret  
        
    def removeFinishedFile(self, envTmp=False):
        """
        Remove FINISHED file
        """
        self.trace( 'removing finished file' )
        try:
            fp = "%s/%s" % ( self.getPath(envTmp=envTmp), STATE_FINISHED )
            res = os.path.exists( fp )
            if res: os.remove( fp )
        except OSError, e:
            self.trace( 'Unable to remove finished file: %s' % str(e) )
        except Exception as e:
            self.error( 'Unable to remove finished file: %s' % str(e) )

    def setFINISHED (self, envTmp=False):
        """
        Called when the task is finished

        @param envTmp: 
        @type envTmp: boolean
        """
        if self.state != STATE_CANCELLED:
            self.trace( 'adding finished file' )
            try:
                f = open( "%s/%s" % ( self.getPath(envTmp=envTmp), STATE_FINISHED ), 'w' )
                f.close()
            except Exception as e:
                self.error( e )
        
        # Add the task on the history db and notify all connected users
        if Settings.getInt( 'MySql', 'insert-test-history'):
            ret, lastinsertid = TaskMngr.addToHistory(task=self)
            toSend = list(self.toTuple())
            if ret is None:
                toSend.insert(0, 999999 ) # error 
            else:
                toSend.insert(0, lastinsertid ) # insert ok

            # new in v10, return only history task according to the user
            connected = Context.instance().getUsersConnectedCopy()
            for cur_user in connected:
                prjs = ProjectsManager.instance().getProjects( user=cur_user, b64=False)
                prjsDict = {}
                for prj in prjs: prjsDict[prj['project_id']] = True
                if self.projectId in prjsDict:
                    data = ( 'task-history', ( "add", [ toSend ] ) )    
                    ESI.instance().notify(body=data, toUser=cur_user)
            del connected
            # end of new in v10
        
        
        if self.prepared:
            TaskMngr.onTaskFinished(self)

    def setState (self, state, envTmp=False):
        """
        Set the state: INIT, WAITING, RUNNING, COMPLETE, ERROR, KILLED, CANCELLED

        @param state: expected value in INIT, WAITING, RUNNING, COMPLETE, ERROR
        @type state: string

        @param envTmp:
        @type envTmp: boolean
        """ 
        self.mutex.acquire()
        self.state = state
        
        #new in v12.2
        # if state not in [ STATE_RUNNING, STATE_COMPLETE ]:
        if state not in [ STATE_INIT, STATE_WAITING ]:
            try:
                f = open( "%s/STATE" % self.getPath(envTmp=envTmp), 'w' )
                f.write( state )
                f.close()
            except Exception as e:
                self.error( "unable to write state file %s" % e ) 
        #end of new
        
        if self.schedId is not None:
            self.trace( 'task %s state: %s' % ( self.schedId, state) )
        else:
            self.trace( 'task state: %s' % state )

        # disable the task according to the state
        if state == STATE_DISABLED: self.enabled = False
        else: self.enabled = True

        if state == STATE_RUNNING:
            self.startTime = time.time()
            
            # save json test for rest api
            self.saveTestDescr()
            
            # Notify all connected users to remove event from the waiting list on the client interface
            connected = Context.instance().getUsersConnectedCopy()
            for cur_user in connected:
                self.trace("updating task waiting: %s" % cur_user)
                data = ( 'task-waiting', ( "update", TaskMngr.getWaiting(user=cur_user)) )   
                ESI.instance().notify(body=data, toUser=cur_user)
            del connected
        
            # Notify all connected users to add event to running list on the client interface 
            # new in v10
            connected = Context.instance().getUsersConnectedCopy()
            for cur_user in connected:
                self.trace("updating task running: %s" % cur_user)
                data = ( 'task-running', ( "update", TaskMngr.getRunning(user=cur_user) ) ) 
                ESI.instance().notify(body=data, toUser=cur_user)
            del connected
            # end of new in v10
            
        elif state in [ STATE_CANCELLED, STATE_COMPLETE, STATE_ERROR, STATE_KILLED]:
            if self.startTime != "N/A":         
                self.stopTime = time.time()
                self.duration = self.stopTime - self.startTime
                # notify all connected users to remove event to running list
                connected = Context.instance().getUsersConnectedCopy()
                for cur_user in connected:
                    data = ( 'task-running', ( "update", TaskMngr.getRunning(user=cur_user) ) ) 
                    ESI.instance().notify(body=data, toUser=cur_user)
                del connected
            self.setFINISHED(envTmp=envTmp)
        self.mutex.release()

    def cancelTest(self, removeFromContext=True):
        """
        Cancel the test

        @param removeFromContext:
        @type removeFromContext: boolean

        @return:
        @rtype:
        """
        self.removeFromContext = removeFromContext
        if self.state == STATE_DISABLED:
            self.setState( state=STATE_CANCELLING )
            self.setState(state=STATE_CANCELLED)
            ret = True
        else:
            self.setState( state=STATE_CANCELLING )
            ret = TaskMngr.unregisterEvent( event =  self.eventReg )
            if ret:
                self.setState(state=STATE_CANCELLED)
            else:
                self.setState(state=STATE_ERROR)
        return ret

    def getTestsPath(self):
        """
        Get the path of all tests

        @return:
        @rtype: string
        """
        testsResultPath = '%s%s' % (  Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        return testsResultPath

    def generateTestID(self):
        """
        deprecated
        """
        ret = ''
        try:
            self.trace( self.getTestPath(withDate=True) )
            hash =  hashlib.md5()
            hash.update( self.getTestPath(withDate=True) )
            ret = hash.hexdigest()
        except Exception as e:
            self.error( "Unable to make hash for test id: %s" % str(e) )
        return ret
        
    def getTestID(self):
        """
        """
        return self.taskUuid
        
    def getTestPath(self, withDate=True):
        """
        Get the path of the test

        @return:
        @rtype: string
        """
        if withDate:
            return  "/%s/%s/%s" % ( self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), self.completeId() )
        else:
            return  self.completeId()

    def getPath (self, envTmp=False, fullPath=True, noDate=False):
        """
        Returns the complete path of the test
        
        @param envTmp:
        @type envTmp: boolean

        @return:
        @rtype: string
        """
        testsResultPath = '%s%s' % (    Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        if envTmp:
            testsResultPath = '%s%s' % (    Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
        if fullPath:
            if noDate:
                return  "%s/%s" % ( testsResultPath, self.completeId() )
            else:
                return  "%s/%s/%s/%s" % ( testsResultPath, self.projectId,  time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), self.completeId() )
        else:
            if noDate:
                return  "%s" % ( self.completeId() )
            else:
                return  "%s/%s/%s" % ( self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), self.completeId() )

    def getDirToday(self, envTmp=False, fullPath=True):
        """
        Get the path of today directory

        @param envTmp:
        @type envTmp: boolean

        @return:
        @rtype: string
        """
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        if envTmp:
            testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
        if fullPath:
            return  "%s/%s/%s" % ( testResultPath, self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)) )
        else:
            return  "%s/%s" % (self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)))
            
    def getDirProject(self, envTmp=False, fullPath=True):
        """
        Get the path of project directory

        @param envTmp:
        @type envTmp: boolean

        @return:
        @rtype: string
        """
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        if envTmp:
            testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
        if fullPath:
            return  "%s/%s" % ( testResultPath, self.projectId )
        else:
            return  self.projectId
            
    def wrongParseToFile(self, te, subTest=False):
        """
        Called when the file to parse is invalid 
        This file is saved on the tmp storage

        @param te:
        @type te:
        """
        try: 
            tmpPath = '%s%s/Parsed' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tmp' )  )
            os.mkdir( tmpPath, 0755 )
        except Exception as e:
            pass
        # write wrong test
        fileName = '%s%s/Parsed/%s_%s_%s.BAD' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ), self.testName, self.userName, self.testId  )
        if subTest:
            fileName = '%s%s/Parsed/SubTE_%s_%s_%s.BAD' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tmp' ), self.testName, self.userName, self.testId  )
        f = open( fileName ,  'w')
        f.write(te)
        f.close()

    def parseTestDesign (self):
        """
        """
        self.prepareTime = time.time()
        ret = {}
        ret["error"] = False
        ret["error-details"] = ""
        ret['design'] = ''
        ret['design-xml'] = ''
        envTmp = True
        cleanupTmp = Settings.getInt( 'Tests_Framework', 'cleanup-test-design')
        try:
            # Prepare the destination storage result
            self.trace("Parse test design: preparing the destination storage result")
            try:
                # create project folder
                try: 
                    prjFolder = self.getDirProject(envTmp=envTmp)
                    if not os.path.exists( prjFolder ):
                        os.mkdir( prjFolder, 0755 )
                except Exception as e:
                    self.trace( "folder %s already exist: %s" % (prjFolder, str(e)) )
                else:
                
                    # create date folder
                    try: 
                        mainDir = self.getDirToday(envTmp=envTmp)
                        if not os.path.exists( mainDir ):
                            os.mkdir( mainDir, 0755 )
                    except Exception as e:
                        self.trace( "dir %s already exist: %s" % (mainDir, str(e)) )
                    else:
                        os.mkdir( self.getPath(envTmp=envTmp, noDate=False), 0755 )
            except OSError, e:
                cleanupTmp = False
                self.error( 'Parse test design: unable to prepare the directory, system error: %s' % str(e) )
                ret["error"] = True
                ret["error-details"] = "Server"
            else:
                
                # Creation te 
                self.trace("Parse test design: creating the test executable for test design check")
                try:
                    te = TestModel.createTestDesign(    
                                                        dataTest = self.dataTest, userName=self.userName, testName=self.testName, 
                                                        trPath=self.getTestPath(withDate=True), logFilename=self.completeId(), withoutProbes=self.withoutProbes,
                                                        defaultLibrary=RepoLibraries.instance().getDefaultV2(), defaultAdapter=RepoAdapters.instance().getDefaultV2(),
                                                        userId=self.userId, projectId=self.projectId, stepByStep=self.stepByStep, breakpoint=self.breakpoint,
                                                        testId=self.testId, runningAgents=AgentsManager.instance().getRunning(), 
                                                        runningProbes=ProbesManager.instance().getRunning(), testLocation=self.getTestLocation(),
                                                        parametersShared=Context.instance().getTestEnvironment(user=self.userName)
                                                    )
                except Exception as e:
                    cleanupTmp = False
                    self.error( 'Parse test design: unable to create te: %s' % str(e) )
                    ret["error"] = True
                    ret["error-details"] = "Server"
                else:

                    # Saving
                    self.trace("Parse test design: saving the test executable on the disk")
                    try:
                        # write test
                        f = open( "%s/%s" % (self.getPath(envTmp=envTmp, noDate=False), self.completeId() ) ,  'w')
                        f.write(te)
                        f.close()

                        # write log
                        f = open( "%s/test.out" % self.getPath(envTmp=envTmp, noDate=False), 'w' )
                        f.close()

                        # write tests settings 
                        shutil.copy( '%s/Core/test.ini' % Settings.getDirExec(), "%s/test.ini" % self.getPath(envTmp=envTmp, noDate=False) )
                        
                        # tunning settings
                        cfgtest_path = "%s/test.ini" % self.getPath(envTmp=envTmp, noDate=False)
                        cfgparser = ConfigParser.RawConfigParser()
                        cfgparser.read( cfgtest_path )
                        cfgparser.set('Paths', 'templates', "%s/%s/" % ( Settings.getDirExec(), Settings.get( 'Paths', 'templates' ) ) )

                        cfgparser.set('Csv_Tests_Results', 'header', '%s' % Settings.get( 'Csv_Tests_Results', 'header' ) )
                        cfgparser.set('Csv_Tests_Results', 'separator', '%s' % Settings.get( 'Csv_Tests_Results', 'separator' ) )

                        cfgtest = open(cfgtest_path,'w')            
                        cfgparser.write(cfgtest)
                        cfgtest.close()
                    except OSError, e:
                        cleanupTmp = False
                        self.error( 'Parse test design: unable to save te, system error: %s' % str(e) )
                        ret["error"] = True
                        ret["error-details"] = "Server"
                    except Exception as e:
                        cleanupTmp = False
                        self.error( 'Parse test design: unable to save te: %s' % str(e) )
                        ret["error"] = True
                        ret["error-details"] = "Server"
                    else:
                    
                        # Compilation
                        self.trace( "Parse test design: compile the test executable" )
                        try:
                            parser.suite(te).compile()
                            # compiler.parse(te)
                        except SyntaxError, e:
                            cleanupTmp = False
                            self.trace( 'Parse test design: unable to compile syntax te: %s' % e )
                            ret["error"] = True
                            ret["error-details"] = "Syntax"
                        except Exception as e:
                            cleanupTmp = False
                            self.error( 'Parse test design: unable to compile te: %s' % Common.getBackTrace() )
                            ret["error"] = True
                            ret["error-details"] = "Server"
                        else:
                            self.trace( "Parse test design: fork and executing" )
                            # Execute
                            executable = Settings.get( 'Bin', 'python' )
                            cmdOptions = [ str(self.schedId), str(self.testId), str(self.replayId) ]
                            
                            # Construct the final execution line
                            args =  [ executable ]
                            # -O : optimize generated bytecode slightly
                            if Settings.get( 'Bin', 'optimize-test' ) != "True":
                                args.append( "-O" )
                            args.append( "%s/%s" % (self.getPath(envTmp=envTmp, noDate=False), self.completeId() ) )
                            args = args + cmdOptions
                            
                            # create sh file
                            f = open( "%s/launch.sh" % self.getPath(envTmp=envTmp, noDate=False), 'w' )
                            f.write( " ".join(args)  )
                            f.close()

                            # Fork and run it
                            env = {}
                            try:
                                pid = os.fork()
                                if pid:
                                    self.tpid = pid
                                    (retcode, sig) = divmod(os.waitpid(pid, 0)[1], 256)
                                else:
                                    os.execve(executable, args, env)
                            except Exception as e:
                                self.error( 'unable to fork te' )
                                ret["error"] = True
                                ret["error-details"] = "Fork"
                            else:
                                if sig > 0:
                                    cleanupTmp = False
                                    if sig == signal.SIGKILL:
                                        self.error( 'killed sig received: %s' % str(sig) )
                                    else:
                                        self.error( 'unknown sig received: %s' % str(sig) )
                                    ret["error"] = True
                                    ret["error-details"] = "Process"
                                else:
                                    if retcode == 0:
                                        self.trace( "Parse test design: fork ok" )
                                        # read result
                                        ret['design'] = self.getTestDesign(zipped=True, b64encoded=True, returnXml=False, envTmp=True)
                                        ret['design-xml'] = self.getTestDesign(zipped=True, b64encoded=True, returnXml=True, envTmp=True)
                                    else:
                                        cleanupTmp = False
                                        self.error( 'unknown return code received: %s' % str(retcode) )
                                        ret["error"] = True
                                        ret["error-details"] = "Return"


        except Exception as e:
            self.error( "unable to parse test design: %s" % str(e) )
            ret["error"] = True
            ret["error-details"] = "Global"
            
        # Remove the test from temp storage
        if cleanupTmp:
            try:
                if os.path.exists(  self.getPath(envTmp=envTmp, noDate=False) ):
                    shutil.rmtree( self.getPath(envTmp=envTmp, noDate=False) )
            except Exception as e:
                self.error( "Parse test design: unable to delete the tmp test: %s" % str(e) )

        return ret

    def parseTest (self):
        """
        Parse the test
        Return False if the syntax is wrong

        @return: (parse result, syntax error)
        @rtype: tuple of (boolean, str)
        """
        self.trace("Parse test: create all sub test executable")
        sub_tes = []
        try:
            # detect the type of test
            isTu = False
            isTa = False
            isTp = False
            isTg = False
            isTs = False
            if 'testunit' in self.dataTest:
                isTu = True
            elif 'testabstract' in self.dataTest:
                isTa = True
            elif 'testplan' in self.dataTest:
                isTp = True
            elif 'testglobal' in self.dataTest:
                isTg = True
            else:
                isTs = True

            if  isTu or isTs or isTa:
                subte = SubTestModel.createSubTest( dataTest = self.dataTest, trPath=self.getTestPath(),
                                                        descriptions=self.dataTest['properties']['descriptions']['description'],
                                                        defaultLibrary=RepoLibraries.instance().getDefaultV2(),
                                                        defaultAdapter=RepoAdapters.instance().getDefaultV2(), 
                                                        isTestUnit=isTu, isTestAbstract=isTa )
                sub_tes.append( (isTu, isTa, self.testName, subte) )

            if  isTp or isTg:
                if isTg:
                    dataTestGen = self.dataTest['testglobal']
                else:
                    dataTestGen = self.dataTest['testplan']

                for ts in dataTestGen:
                    isSubTu=False
                    isSubTa=False
                    if 'extension' in ts:
                        if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                            isSubTu=True
                        if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                            isSubTa=True
                            
                    if ts['enable'] == TestModel.TS_ENABLED:
                        subte = SubTestModel.createSubTest( dataTest = ts, trPath=self.getTestPath(),
                                                        descriptions=self.dataTest['properties']['descriptions']['description'],
                                                        defaultLibrary=RepoLibraries.instance().getDefaultV2(),
                                                        defaultAdapter=RepoAdapters.instance().getDefaultV2(), 
                                                        isTestUnit=isSubTu, isTestAbstract=isSubTa,
                                                        isTestPlan=isTp, isTestGlobal=isTg )
                        sub_tes.append( ( isSubTu, isSubTa, ts['file'], subte) )
        except Exception as e:
            self.error( "parse test - unable to prepare sub te: %s" % str(e) )
            return ( False, str(e) )
        else:
            self.trace("Parse test: creating the main te")
            startTestLine = 0
            startExecTestLine = 0
            te = ''
            try:
                te = TestModel.createTestExecutable(dataTest = self.dataTest, userName=self.userName, testName=self.testName, 
                                trPath=self.getTestPath(), logFilename=self.completeId(), withoutProbes=self.withoutProbes,
                                defaultLibrary=RepoLibraries.instance().getDefaultV2(), defaultAdapter=RepoAdapters.instance().getDefaultV2(),
                                userId=self.userId, projectId=self.projectId, subTEs=len(sub_tes), channelId=self.channelId,
                                parametersShared=Context.instance().getTestEnvironment(user=self.userName),
                                stepByStep=self.stepByStep, breakpoint=self.breakpoint, testId=self.testId, testLocation=self.getTestLocation(),
                                runningAgents=AgentsManager.instance().getRunning(), runningProbes=ProbesManager.instance().getRunning()
                        )
            except Exception as e:
                self.error( "parse test - unable to prepare te: %s" % str(e) )
                self.wrongParseToFile( te=te)
                return ( False, str(e) )
            else:
                self.trace( "compile all sub test executable" ) 
                for i in xrange(len(sub_tes)):
                    issub_tu, issub_ta, subtest_name, subtest_val = sub_tes[i]
                    # find startline of the test
                    if issub_tu or issub_ta:
                        beginTe, leftTe = subtest_val.split('class TESTCASE(TestCase):')
                    else:
                        beginTe, leftTe = subtest_val.split('# !! test injection')

                    startTestLine = len( beginTe.splitlines() ) + 1

                    # compile
                    try:
                        parser.suite(subtest_val).compile()
                        #compiler.parse(subtest_val)
                    except SyntaxError as e:
                        self.trace( "sub test syntax error: %s" % str(e) )
                        lineno = e.lineno
                        e.lineno = None
                        self.wrongParseToFile( te=subtest_val, subTest=True  )
                        linerr = (lineno-startTestLine) + 1
                        if 'testplan' in self.dataTest or 'testglobal' in self.dataTest:
                            return ( False, "Test %s (line %s): %s" % (subtest_name, linerr, e) )
                        else:
                            return ( False, "Line %s: %s" % (linerr, e) )
                    except SystemError as e:
                        self.error( "sub test server limitation raised: %s" % str(e) )
                        return ( False, "Limitation: this test is too big!" )
                    except Exception as e:
                        self.error( 'unable to parse sub test %s' % Common.getBackTrace() )
                        e.lineno = None
                        self.wrongParseToFile( te=subtest_val, subTest=True  )
                        return ( False, str(e) )

                self.trace('Parse test: compiling main te')
                try:
                    parser.suite(te).compile()
                    #compiler.parse(te)
                except SyntaxError, e:
                    self.trace( "syntax error: %s" % str(e) )
                    lineno = e.lineno
                    e.lineno = None
                    self.wrongParseToFile( te=te )
                    if 'testplan' in self.dataTest or 'testglobal' in self.dataTest:
                        return ( False, str(e) )
                    else:
                        if 'testunit' in self.dataTest:
                            return ( False, "Line %s: %s" % ( (lineno-startTestLine) + 1,str(e)) )
                        elif 'testabstract' in self.dataTest:
                            return ( False, "Line %s: %s" % ( (lineno-startTestLine) + 1,str(e)) )
                        else:              
                            # begin issue 464  
                            beginTeExec, leftTeExec = te.split('# !! test exec injection')
                            startExecTestLine = len( beginTeExec.splitlines() ) + 1
                            if lineno >= startExecTestLine:
                                return ( False, "Line %s: %s" % ( (lineno -startExecTestLine)+1, str(e) ) )
                            # end issue 464  
                            else:
                                return ( False, "Line %s: %s" % ( (lineno-startTestLine) + 1,str(e)) )
                except SystemError as e:
                    self.error( "server limitation raised: %s" % str(e) )
                    return ( False, "Limitation: this test is too big!" )
                except Exception as e:
                    self.error( 'unable to parse test %s' % Common.getBackTrace() )
                    e.lineno = None
                    self.wrongParseToFile( te=te )
                    return ( False, str(e) )
            return ( True, "" )

    def getTestLocation(self):
        """
        """
        test_tmp = self.testPath.rsplit(self.testName, 1)
        return "/%s" % test_tmp[0]
    
    def initPrepare(self):
        """
        """
        self.prepareTime = time.time()
        self.prepared = False
        self.trace( "Prepare time: %s" % self.prepareTime )
        self.trace( "Human prepare time: %s" % time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)) )
        return True
        
    def prepare(self, envTmp=False):
        """
        Prepare the test
        - Prepare storage
        - Creation
        - Saving
        - Compilation

        @param envTmp:
        @type envTmp: boolean

        @return:
        @rtype: boolean
        """
        self.initPrepare()
        
        # self.prepareTime = time.time()
        # self.prepared = False
        
        # Prepare the destination storage result
        self.trace("Preparing the destination storage result")
        try:
            if envTmp:
                try: 
                    tmpPath = '%s%s' % (  Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
                    if not os.path.exists( tmpPath ):
                        os.mkdir( tmpPath, 0755 )
                except Exception as e:
                    self.trace( "dir %s already exist: %s" % (tmpPath, str(e)) )
            # create main dir
            try: 
                mainDir = self.getDirProject(envTmp=envTmp)
                if not os.path.exists( mainDir ):
                    os.mkdir( mainDir, 0755 )
            except Exception as e:
                self.trace( "dir project %s already exist: %s" % (mainDir, str(e)) )
            try: 
                mainDir = self.getDirToday(envTmp=envTmp)
                if not os.path.exists( mainDir ):
                    os.mkdir( mainDir, 0755 )
            except Exception as e:
                self.trace( "dir date %s already exist: %s" % (mainDir, str(e)) )
                
            # create specific folder
            os.mkdir( self.getPath(envTmp=envTmp), 0755 )
            
        except OSError as e:
            self.error( 'unable to prepare the directory, system error: %s' % str(e) )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( e.strerror )
        except Exception as e:
            self.error( 'unable to prepare the directory: %s' % e )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( Common.getBackTrace() )

        # Creation
        self.trace("Create all sub test executable")
        sub_tes = []
        try:
            dataTest = self.dataTest
            if envTmp: # not alter data in tmp env
                dataTest = copy.deepcopy(self.dataTest)
            
            # detect the type of test
            isTa = False
            isTu = False
            isTp = False
            isTg = False
            isTs = False
            if 'testunit' in dataTest:
                isTu = True
            elif 'testabstract' in dataTest:
                isTa = True
            elif 'testplan' in dataTest:
                isTp = True
            elif 'testglobal' in dataTest:
                isTg = True
            else:
                isTs = True

            if  isTu or isTs or isTa:
                subte = SubTestModel.createSubTest( dataTest = dataTest, trPath=self.getTestPath(),
                                                        descriptions=dataTest['properties']['descriptions']['description'],
                                                        defaultLibrary=RepoLibraries.instance().getDefaultV2(),
                                                        defaultAdapter=RepoAdapters.instance().getDefaultV2(),
                                                        isTestUnit=isTu, isTestAbstract=isTa )
                sub_tes.append( subte )

            if  isTp or isTg:
                if isTg:
                    dataTestGen = dataTest['testglobal']
                else:
                    dataTestGen = dataTest['testplan']
                for ts in dataTestGen:
                    isSubTu=False
                    isSubTa=False
                    if 'extension' in ts:
                        if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                            isSubTu=True
                        if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                            isSubTa=True
                            
                    if ts['enable'] == TestModel.TS_ENABLED:
                        subte = SubTestModel.createSubTest( dataTest = ts, descriptions=dataTest['properties']['descriptions']['description'],
                                                                trPath=self.getTestPath(),
                                                        defaultLibrary=RepoLibraries.instance().getDefaultV2(),
                                                        defaultAdapter=RepoAdapters.instance().getDefaultV2(), 
                                                        isTestUnit=isSubTu, isTestAbstract=isSubTa,
                                                        isTestPlan=isTp, isTestGlobal=isTg )
                        sub_tes.append( subte )

        except Exception as e:
            self.error( 'unable to create sub te' )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( Common.getBackTrace() )
        
        self.trace("nb sub test: %s" % len(sub_tes) )
        self.trace("Create the main test executable")
        try:
            dataTest = self.dataTest
            if envTmp: # not alter data in tmp env
                dataTest = copy.deepcopy(self.dataTest)

            te = TestModel.createTestExecutable(    dataTest = dataTest, userName=self.userName, testName=self.testName, 
                                                    trPath=self.getTestPath(), logFilename=self.completeId(), withoutProbes=self.withoutProbes,
                                                    defaultLibrary=RepoLibraries.instance().getDefaultV2(), defaultAdapter=RepoAdapters.instance().getDefaultV2(),
                                                    userId=self.userId, projectId=self.projectId, subTEs=len(sub_tes), channelId=self.channelId,
                                                    parametersShared=Context.instance().getTestEnvironment(user=self.userName),
                                                    stepByStep=self.stepByStep, breakpoint=self.breakpoint, testId=self.testId, testLocation=self.getTestLocation(),
                                                    runningAgents=AgentsManager.instance().getRunning(), runningProbes=ProbesManager.instance().getRunning()
                                                )
        except Exception as e:
            self.error( 'unable to create the main te: %s' % e )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( Common.getBackTrace() )
        
        # Saving
        self.trace("Save the test executable on the disk")
        try:
            self.trace("Writing init file for test executable")
            # write test
            f = open( "%s/__init__.py" % self.getPath(envTmp=envTmp),  'w')
            f.write("")
            f.close()

            self.trace("Writing all sub te")
            for i in xrange(len(sub_tes)):
                f = open( "%s/SubTE%s.py" % (self.getPath(envTmp=envTmp), i ) ,  'w')
                f.write(sub_tes[i])
                f.close()
                
            self.trace("Writing main path of the te")
            # write test path
            f = open( "%s/TESTPATH" % self.getPath(envTmp=envTmp) ,  'w') # change in v16
            f.write("%s" % self.testPath)
            f.close()
            
            self.trace("Writing main te")
            # write test
            f = open( "%s/MainTE.py" % self.getPath(envTmp=envTmp) ,  'w') # change in v16
            f.write(te)
            f.close()
            
            self.trace("Writing task uuid")
            # write log
            f = open( "%s/TASKID" % self.getPath(envTmp=envTmp), 'w' )
            f.write( "%s" % self.taskUuid )
            f.close()
            if not envTmp:
                self.saveTestDescr()
                RepoArchives.instance().cacheUuid(taskId=self.taskUuid, testPath=self.getPath(envTmp=False, fullPath=False))

            self.trace("Writing log file")
            # write log
            f = open( "%s/test.out" % self.getPath(envTmp=envTmp), 'w' )
            f.close()

            # write tests settings 
            shutil.copy( '%s/Core/test.ini' % Settings.getDirExec(), "%s/test.ini" % self.getPath(envTmp=envTmp) )
            
            # tunning settings
            cfgtest_path = "%s/test.ini" % self.getPath(envTmp=envTmp)
            cfgparser = ConfigParser.RawConfigParser()
            cfgparser.read( cfgtest_path )
            cfgparser.set('Paths', 'tmp', "%s/%s/" % ( StorageDataAdapters.instance().getStoragePath(), self.getPath(fullPath=False) ) )
            cfgparser.set('Paths', 'templates', "%s/%s/" % ( Settings.getDirExec(), Settings.get( 'Paths', 'templates' ) ) )
            cfgparser.set('Paths', 'result', "%s" % self.getPath(envTmp=envTmp) )
            cfgparser.set('Paths', 'sut-adapters', "%s/%s/" % ( Settings.getDirExec(), Settings.get( 'Paths', 'adapters' ) ) )
            cfgparser.set('Paths', 'public', "%s/%s/" % ( Settings.getDirExec(), Settings.get( 'Paths', 'public' ) ) )
            
            cfgparser.set('Tests_Framework', 'continue-on-step-error', '%s' % Settings.get( 'Tests_Framework', 'continue-on-step-error' ) )
            cfgparser.set('Tests_Framework', 'header-test-report', '%s' % Settings.get( 'Tests_Framework', 'header-test-report' ) )
            cfgparser.set('Tests_Framework', 'dispatch-events-current-tc', '%s' % Settings.get( 'Tests_Framework', 'dispatch-events-current-tc' ) )
            cfgparser.set('Tests_Framework', 'expand-test-report', '%s' % Settings.get( 'Tests_Framework', 'expand-test-report' ) )
            
            cfgparser.set('Csv_Tests_Results', 'header', '%s' % Settings.get( 'Csv_Tests_Results', 'header' ) )
            cfgparser.set('Csv_Tests_Results', 'separator', '%s' % Settings.get( 'Csv_Tests_Results', 'separator' ) )

            cfgparser.set('Event_Colors', 'state', '%s' % Settings.get( 'Events_Colors', 'state' ) )
            cfgparser.set('Event_Colors', 'state-text', '%s' % Settings.get( 'Events_Colors', 'state-text' ) )
            cfgparser.set('Event_Colors', 'internal', '%s' % Settings.get( 'Events_Colors', 'internal' ) )
            cfgparser.set('Event_Colors', 'internal-text', '%s' % Settings.get( 'Events_Colors', 'internal-text' ) )
            cfgparser.set('Event_Colors', 'timer', '%s' % Settings.get( 'Events_Colors', 'timer' ) )
            cfgparser.set('Event_Colors', 'timer-text', '%s' % Settings.get( 'Events_Colors', 'timer-text' ) )
            cfgparser.set('Event_Colors', 'match', '%s' % Settings.get( 'Events_Colors', 'match' ) )
            cfgparser.set('Event_Colors', 'match-text', '%s' % Settings.get( 'Events_Colors', 'match-text' ) )
            cfgparser.set('Event_Colors', 'mismatch', '%s' % Settings.get( 'Events_Colors', 'mismatch' ) )
            cfgparser.set('Event_Colors', 'mismatch-text', '%s' % Settings.get( 'Events_Colors', 'mismatch-text' ) )
            cfgparser.set('Event_Colors', 'payload', '%s' % Settings.get( 'Events_Colors', 'payload' ) )
            cfgparser.set('Event_Colors', 'payload-text', '%s' % Settings.get( 'Events_Colors', 'payload-text' ) )
            cfgparser.set('Event_Colors', 'info-tg', '%s' % Settings.get( 'Events_Colors', 'info-tg' ) )
            cfgparser.set('Event_Colors', 'info-tg-text', '%s' % Settings.get( 'Events_Colors', 'info-tg-text' ) )
            cfgparser.set('Event_Colors', 'info-tp', '%s' % Settings.get( 'Events_Colors', 'info-tp' ) )
            cfgparser.set('Event_Colors', 'info-tp-text', '%s' % Settings.get( 'Events_Colors', 'info-tp-text' ) )
            cfgparser.set('Event_Colors', 'info-ts', '%s' % Settings.get( 'Events_Colors', 'info-ts' ) )
            cfgparser.set('Event_Colors', 'info-ts-text', '%s' % Settings.get( 'Events_Colors', 'info-ts-text' ) )
            cfgparser.set('Event_Colors', 'info-tc', '%s' % Settings.get( 'Events_Colors', 'info-tc' ) )
            cfgparser.set('Event_Colors', 'info-tc-text', '%s' % Settings.get( 'Events_Colors', 'info-tc-text' ) )
            cfgparser.set('Event_Colors', 'warning-tg', '%s' % Settings.get( 'Events_Colors', 'warning-tg' ) )
            cfgparser.set('Event_Colors', 'warning-tg-text', '%s' % Settings.get( 'Events_Colors', 'warning-tg-text' ) )
            cfgparser.set('Event_Colors', 'warning-tp', '%s' % Settings.get( 'Events_Colors', 'warning-tp' ) )
            cfgparser.set('Event_Colors', 'warning-tp-text', '%s' % Settings.get( 'Events_Colors', 'warning-tp-text' ) )
            cfgparser.set('Event_Colors', 'warning-ts', '%s' % Settings.get( 'Events_Colors', 'warning-ts' ) )
            cfgparser.set('Event_Colors', 'warning-ts-text', '%s' % Settings.get( 'Events_Colors', 'warning-ts-text' ) )
            cfgparser.set('Event_Colors', 'warning-tc', '%s' % Settings.get( 'Events_Colors', 'warning-tc' ) )
            cfgparser.set('Event_Colors', 'warning-tc-text', '%s' % Settings.get( 'Events_Colors', 'warning-tc-text' ) )
            cfgparser.set('Event_Colors', 'error-tg', '%s' % Settings.get( 'Events_Colors', 'error-tg' ) )
            cfgparser.set('Event_Colors', 'error-tg-text', '%s' % Settings.get( 'Events_Colors', 'error-tg-text' ) )
            cfgparser.set('Event_Colors', 'error-tp', '%s' % Settings.get( 'Events_Colors', 'error-tp' ) )
            cfgparser.set('Event_Colors', 'error-tp-text', '%s' % Settings.get( 'Events_Colors', 'error-tp-text' ) )
            cfgparser.set('Event_Colors', 'error-ts', '%s' % Settings.get( 'Events_Colors', 'error-ts' ) )
            cfgparser.set('Event_Colors', 'error-ts-text', '%s' % Settings.get( 'Events_Colors', 'error-ts-text' ) )
            cfgparser.set('Event_Colors', 'error-tc', '%s' % Settings.get( 'Events_Colors', 'error-tc' ) )
            cfgparser.set('Event_Colors', 'error-tc-text', '%s' % Settings.get( 'Events_Colors', 'error-tc-text' ) )
            cfgparser.set('Event_Colors', 'step-started', '%s' % Settings.get( 'Events_Colors', 'step-started' ) )
            cfgparser.set('Event_Colors', 'step-started-text', '%s' % Settings.get( 'Events_Colors', 'step-started-text' ) )
            cfgparser.set('Event_Colors', 'step-passed', '%s' % Settings.get( 'Events_Colors', 'step-passed' ) )
            cfgparser.set('Event_Colors', 'step-passed-text', '%s' % Settings.get( 'Events_Colors', 'step-passed-text' ) )
            cfgparser.set('Event_Colors', 'step-failed', '%s' % Settings.get( 'Events_Colors', 'step-failed' ) )
            cfgparser.set('Event_Colors', 'step-failed-text', '%s' % Settings.get( 'Events_Colors', 'step-failed-text' ) )

            if self.debugActivated:
                cfgparser.set('Trace', 'level', "DEBUG" )
            cfgtest = open(cfgtest_path,'w')            
            cfgparser.write(cfgtest)
            cfgtest.close()
        except OSError as e:
            self.error( 'unable to save te, system error: %s' % str(e) )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( e.strerror )
        except Exception as e:
            self.error( 'unable to save te' )
            self.setState(state = STATE_ERROR, envTmp=envTmp)
            raise Exception( Common.getBackTrace() )
        
        # Notify all connected users to update archives if it is not a run in the temporary env or 
        # if it is not necessary to keep test result
        if not envTmp:
            if Settings.getInt( 'Notifications', 'archives'):
                if not self.noKeepTr:
                    # msg ( dest, ( action, data ) )
                    m = [   {   "type": "folder", "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                                "project": "%s" % self.projectId,
                                "content": [ {  "project": "%s" % self.projectId, "type": "folder", "name": self.completeId(), 
                                                    "virtual-name": self.completeId(withTestPath=True), "content": []} ] }  ]
                    notif = {}
                    notif['archive'] = m 
                    data = ( 'archive', ( None, notif) ) 
                    ESI.instance().notifyByUserAndProject(body = data, admin=True, leader=False, tester=True, developer=False, 
                                                            projectId="%s" % self.projectId)
        
        # Compilation
        if self.syntaxOK:
            self.trace("Task[Tmp=%s] parse/compile: already done before" % envTmp)
        else:
            self.trace( "Task[Tmp=%s] parse/compile all sub test executable" % envTmp)
            t0 = time.time()
            for i in xrange(len(sub_tes)):
                try:
                    parser.suite(sub_tes[i]).compile()
                    #compiler.parse(sub_tes[i])
                except SyntaxError as e:
                    e.lineno = None
                    self.trace( 'unable to compile sub te syntax te: %s' % e )
                    self.setState(state = STATE_ERROR, envTmp=envTmp)
                    raise Exception( e )
                except SystemError as e:
                    self.error( "Sub te server limitation raised: %s" % str(e) )
                    self.setState(state = STATE_ERROR, envTmp=envTmp)
                    raise Exception( "Limitation: this test is too big!" )
                except Exception as e:
                    self.error( 'unable to compile sub te: %s' % Common.getBackTrace() )
                    self.setState(state = STATE_ERROR, envTmp=envTmp)
                    raise Exception( e )

            self.trace( "Compile the main test executable" )
            try:
                parser.suite(te).compile()
            except SyntaxError as e:
                e.lineno = None
                self.trace( 'unable to compile syntax te: %s' % e )
                self.setState(state = STATE_ERROR, envTmp=envTmp)
                raise Exception( e )
            except SystemError as e:
                self.error( "server limitation raised: %s" % str(e) )
                self.setState(state = STATE_ERROR, envTmp=envTmp)
                raise Exception( "Limitation: this test is too big!" )
            except Exception as e:
                self.error( 'unable to compile te: %s' % Common.getBackTrace() )
                self.setState(state = STATE_ERROR, envTmp=envTmp)
                raise Exception( e )
            self.trace("Task[Tmp=%s] parse/compile test terminated in %s sec." % (envTmp, (time.time() - t0)) )

        # Remove the test from temp storage
        if envTmp:
            try:
                if os.path.exists(  self.getPath(envTmp=envTmp) ):
                    shutil.rmtree( self.getPath(envTmp=envTmp) )
            except Exception as e:
                self.error( "unable to delete the tmp test: %s" % str(e) )
        
        self.setPrepared()
        self.trace("Task[Tmp=%s] prepared in %s sec." % (envTmp, (time.time() - self.prepareTime)) )
        return self.prepared

    def getTestDesign(self, zipped=True, b64encoded=True, returnXml=False, envTmp=False):
        """
        Return the report of the task
        """
        designs = ''
        if envTmp:
            testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
        else:
            testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        fileName = "%s/%s/%s/%s/%s_%s" % ( testResultPath,  self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), 
                                            self.completeId(), self.testName, str(self.replayId) )
        try:
            if returnXml:
                f = open( '%s.%s' % (fileName, RepoManager.TEST_RESULT_DESIGN_XML_EXT) , 'r'  )
            else:
                f = open( '%s.%s' % (fileName, RepoManager.TEST_RESULT_DESIGN_EXT) , 'r'  )
            raw_design = f.read()
            f.close()
        except Exception as e:
            self.error( "open test result design failed: %s" % str(e) )
        else:
            if not zipped:
                return raw_design.decode('utf8')
            else:
                try: 
                    zip_design = zlib.compress(raw_design)
                except Exception as e:
                    self.error( "Unable to compress test result design: %s" % str(e) )
                else:
                    if not b64encoded:
                        return zip_design
                    else:
                        try: 
                            designs = base64.b64encode(zip_design)
                        except Exception as e:
                            self.error( "Unable to encode in base 64 test result design: %s" % str(e) )

        return designs

    def getTestReport(self, zipped=True, b64encoded=True, returnXml=False, basicReport=False):
        """
        Return the report of the task
        """
        reports = ''
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        fileName = "%s/%s/%s/%s/%s_%s" % ( testResultPath,  self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), 
                                            self.completeId(), self.testName, str(self.replayId) )
        try:
            
            if returnXml:
                reportExt = RepoManager.TEST_RESULT_REPORT_XML_EXT
                f = open( '%s.%s' % (fileName, reportExt) , 'r'  )
            else:
                reportExt = RepoManager.TEST_RESULT_REPORT_EXT
                if basicReport:
                    reportExt = RepoManager.TEST_RESULT_BASIC_REPORT_EXT
                f = open( '%s.%s' % (fileName, reportExt) , 'r'  )
            raw_report = f.read()
            f.close()
        except Exception as e:
            self.error( "open test result report failed: %s" % str(e) )
        else:
            if not zipped:
                return raw_report.decode('utf8')
            else:
                try: 
                    zip_report = zlib.compress(raw_report)
                except Exception as e:
                    self.error( "Unable to compress test result report: %s" % str(e) )
                else:
                    if not b64encoded:
                        return zip_report
                    else:
                        try: 
                            reports = base64.b64encode(zip_report)
                        except Exception as e:
                            self.error( "Unable to encode in base 64 test result report: %s" % str(e) )

        return reports

    def getTestVerdict(self, zipped=True, b64encoded=True, returnXml=False):
        """
        Return the verdict of the task
        """
        verdict = ''
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        fileName = "%s/%s/%s/%s/%s_%s" % ( testResultPath,  self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), 
                                            self.completeId(), self.testName, str(self.replayId) )
        try:
            if returnXml:
                f = open( '%s.%s' % (fileName, RepoManager.TEST_RESULT_VERDICT_XML_EXT) , 'r'  )
            else:
                f = open( '%s.%s' % (fileName, RepoManager.TEST_RESULT_VERDICT_EXT) , 'r'  )
            raw_verdict = f.read()
            f.close()
        except Exception as e:
            self.error( "open test result verdict failed: %s" % str(e) )
        else:
            if not zipped:
                return raw_verdict.decode('utf8')
            else:
                try: 
                    zip_verdict = zlib.compress(raw_verdict)
                except Exception as e:
                    self.error( "Unable to compress test result verdict: %s" % str(e) )
                else:
                    if not b64encoded:
                        return zip_verdict
                    else:
                        try: 
                            verdict = base64.b64encode(zip_verdict)
                        except Exception as e:
                            self.error( "Unable to encode in base 64 test result verdict: %s" % str(e) )

        return verdict

    def getFileResultPath(self):
        """
        This function is used to add a comment on a test result

        @return:
        @rtype: string
        """
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )

        dirTask = "%s/%s/%s/" % ( self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),  self.completeId() )
        
        # Search the file on the disk because the number of current comment can be different that the value known by the user
        trxFile = 'undefined'
        for f in os.listdir( "%s/%s" % (testResultPath,dirTask) ):
            if f.startswith( "%s_%s" % (self.testName, str(self.replayId)) ) and f.endswith('trx'):
                trxFile = "%s%s" % (dirTask, f)
        return trxFile

    def notifResultLog (self):
        """
        Notify all users if new file is available
        Compress txt log to gzip 
        filename = testname_replayid_nbcomments_verdict.testresult
        """
        testResultPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
        dirTask = "%s/%s/%s/" % ( self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),  self.completeId() )
        fileName = "%s/%s/%s/%s/%s_%s" % ( testResultPath,  self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), 
                                            self.completeId(), self.testName, str(self.replayId) )
        try:
            os.path.getsize( "%s.log" % fileName )
        except Exception as e:
            self.error( e )
            return

        # read events from log
        f = open( "%s.log" % fileName, 'r')
        read_data = f.read()
        f.close()

        # read events from log
        f2 = open( "%s.hdr" % fileName, 'r')
        read_header = f2.read()
        f2.close()
        
        # get final result
        # this file "VERDICT" is created by the test library throught the function "log_script_stopped"
        verdict = 'UNDEFINED'
        path_verdict = "%s/%s/%s/%s/" % ( testResultPath,  self.projectId, time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), self.completeId() )
        if os.path.exists( "%s/VERDICT_PASS" % path_verdict ):
            verdict = 'PASS'
        if os.path.exists( "%s/VERDICT_FAIL" % path_verdict  ):
            verdict = 'FAIL'
        
        # fix issue remove global verdict on verdict, fix in v11.2
        try:
            os.remove( "%s/VERDICT_%s" % (path_verdict,verdict) )
        except Exception as e:
            pass
        # end of fix
        
        # new in v12.2
        try:
            f = open( "%s/RESULT" % path_verdict, 'w' )
            f.write( verdict )
            f.close()
            
            if verdict == "PASS": self.resultsStats["passed"] += 1
            if verdict == "FAIL": self.resultsStats["failed"] += 1
            if verdict == "UNDEFINED": self.resultsStats["undefined"] += 1
            
            self.saveTestDescr()
        except Exception as e:
            self.error( "unable to write result file %s" % e )
        # end of new
        
        
        self.verdict = verdict

        # construct data model
        dataModel = TestResult.DataModel(testResult=read_data, testHeader=read_header)
        nbComments = 0
        filenameTrx = "%s_%s_%s.%s" % (fileName, verdict, str(nbComments), RepoManager.TEST_RESULT_EXT) 
        f = open( filenameTrx, 'wb')
        raw_data = dataModel.toXml()
        f.write( zlib.compress( raw_data ) )
        f.close()
        
        # optimization remove log file in v12
        try:
            os.remove( "%s.log" % fileName )
        except Exception as e:
            pass
        # end of new
            
        if Settings.getInt( 'Notifications', 'archives'):
            if self.noKeepTr and self.verdict != 'PASS':
                self.trace('no keep test result option activated: notify the test result because the result if different of pass')
                # msg ( dest, ( action, data ) )
                m = [   {   "type": "folder", "project": "%s" % self.projectId, "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), 
                            "content": [ { "project": "%s" % self.projectId, "type": "folder", "name": self.completeId(),"content": [], "virtual-name": self.completeId(withTestPath=True)} ] }  ]
                notif = {}
                notif['archive'] = m 
                data = ( 'archive', ( None, notif) ) 

                ESI.instance().notifyByUserAndProject(body = data, admin=True, leader=False, tester=True, developer=False, projectId="%s" % self.projectId)

            if self.noKeepTr and self.verdict == 'PASS':
                self.trace('no keep test result option activated: do not notify the user because the result is pass')
            else:
                size_ = os.path.getsize( filenameTrx )
                notif = {}
                m = [   {   "type": "folder", "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)), "project": "%s" % self.projectId, 
                            "content": [ {  "type": "folder", "name": self.completeId(), "project": "%s" % self.projectId, "virtual-name": self.completeId(withTestPath=True),
                            "content": [ { "type": "file", "project": "%s" % self.projectId, 
                                           "name": "%s_%s_%s_%s.%s" % ( self.testName, str(self.replayId), verdict, str(nbComments), RepoManager.TEST_RESULT_EXT ),
                                           'size': str(size_) } ]} ] }  ]
                notif['archive'] = m 
                notif['stats-repo-archives'] = {    'nb-zip':0, 'nb-trx':1, 'nb-tot': 1,
                                                'mb-used': RepoArchives.instance().getSizeRepoV2(folder=RepoArchives.instance().testsPath),
                                                'mb-free': RepoArchives.instance().freeSpace(p=RepoArchives.instance().testsPath) }
                data = ( 'archive', ( None, notif) )    

                ESI.instance().notifyByUserAndProject(body = data, admin=True, leader=False, tester=True, developer=False, projectId="%s" % self.projectId)
                
        # not necessary to keep test results logs, delete it
        if self.noKeepTr:
            if self.verdict == 'PASS':
                try:
                    trPath = '%s/%s' % (testResultPath, dirTask)
                    if os.path.exists(  trPath ):
                        shutil.rmtree( trPath )
                except Exception as e:
                    self.error( "unable to delete the test result (no keep tr option on result pass) %s" % str(e) )

    def run(self, needPrepare=True):
        """
        Executes Test
        Following arguments are sent to the test executable
            - test directory
            - Complete Test ID (just name)
            - Test Id on server
            - Test Name 
            - Test Id
            - Replay Id

        @return: final state
        @rtype: string
        """
        # this run is a replay is greater than zero, then the test is already ready 
        if self.replayId > 0:
            testready = True
        else:
            if not needPrepare:
                testready = True
            else:
                # first run, prepare test on final environment
                try:
                    testready = self.prepare(envTmp=False)
                except Exception as e:
                    self.error( 'unable to prepare test' )
                    self.setState(state = STATE_ERROR)
                    raise Exception( Common.getBackTrace() )
        
        # create temp adapters data storage
        StorageDataAdapters.instance().initStorage()

        # folder "completeid" is removed if already exists
        StorageDataAdapters.instance().initSubStorage(  dirProject=self.projectId,
                                                        dirToday = time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                                                        dirTest=self.completeId() )

        if testready:
            self.setState(state = STATE_RUNNING)
            # Prepare arguments
            executable = Settings.get( 'Bin', 'python' )
            cmdOptions = [ str(self.schedId), str(self.testId), str(self.replayId) ]
            
            # Construct the final execution line
            args =  [ executable ]
            # -O : optimize generated bytecode slightly
            if Settings.get( 'Bin', 'optimize-test' ) != "True":
                args.append( "-O" )
            #args.append( "%s/%s" % (self.getPath(), self.completeId() ) )
            args.append( "%s/MainTE.py" % self.getPath() ) # change in v16
            args = args + cmdOptions
            
            # create sh file
            f = open( "%s/launch.sh" % self.getPath(), 'w' )
            f.write( " ".join(args)  )
            f.close()

            # Fork and run it
            env = {}
            try:
                pid = os.fork()
                if pid:
                    TaskMngr.addChildPid(pid=pid)
                    self.tpid = pid
                    (retcode, sig) = divmod(os.waitpid(pid, 0)[1], 256)
                else:
                    os.execve(executable, args, env)
            except Exception as e:
                self.error( 'unable to fork te' )
                self.setState(state = STATE_ERROR)
            else:
                if sig > 0:
                    if sig == signal.SIGKILL:
                        self.setState(state = STATE_KILLED)
                    else:
                        self.error( 'unknown sig received: %s' % str(sig) )
                        self.setState(state = STATE_ERROR)
                else:
                    if retcode == 0:
                        self.setState( state = STATE_COMPLETE)
                    else:
                        self.error( 'unknown return code received: %s' % str(retcode) )
                        self.setState(state = STATE_ERROR)
            
            TaskMngr.delChildPid(pid=pid)
            # notify result log and by mail
            self.notifResultLog()
            if not self.withoutNotif:
                self.notifResultMail()

            # Update stats
            StatsManager.instance().addResultScript( self.state, self.userId, 
                                                    self.duration, self.projectId )
            
            if not self.noKeepTr:
                # Inspect the data storage adapters, zip data if present 
                # and notify users connected
                if Settings.getInt( 'Tests_Framework', 'zip-all-adapters'):
                    zipped = StorageDataAdapters.instance().zipDataV2( 
                                                        dirToday=time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                                                        dirTest=self.completeId(),
                                                        destPathZip=self.getPath(),
                                                        replayId = str(self.replayId),
                                                        projectId = self.projectId,
                                                        virtualName = self.completeId(withTestPath=True)
                                                        )
                else:
                    zipped = StorageDataAdapters.instance().zipData( 
                                                        dirToday=time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                                                        dirTest=self.completeId(),
                                                        destPathZip=self.getPath(),
                                                        replayId = str(self.replayId),
                                                        projectId = self.projectId,
                                                        virtualName = self.completeId(withTestPath=True)
                                                        )
                
                if zipped:
                    self.trace('Storage zipped for task')
                    
            # delete temp adapters data storage
            StorageDataAdapters.instance().removeSubStorage(    
                                                                projectId = self.projectId,
                                                                dirToday=time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                                                                dirTest=self.completeId()
                                                            )

            return self.state

    def notifResultMail(self):
        """
        """
        if not Settings.getInt( 'Notifications', 'emails'):
            self.trace('Emails notifications disabled')
            return

        user_profile = UsersManager.instance().getUser(login=self.userName)
        if user_profile is None:
            self.error( 'user not found, send mail failed' )
        else:
            # PASS,FAIL,UNDEF,COMPLETE,ERROR,KILLED,CANCELLED
            # false;false;false;false;false;false;false
            notifications  = user_profile['notifications'].split(';')
            self.trace('notifications options for user %s: %s' % (self.userName, notifications) )
            #  ['true', 'false', 'false', 'false', 'false', 'false', 'false', '']
            notifs_bool = [ eval(x.title()) for x in notifications[:-1] ]

            if self.state == STATE_COMPLETE and notifs_bool[3]:
                self.trace( 'task state [%s]: notification user option activated, mail to sent' % self.state )
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_ERROR and notifs_bool[4]:
                self.trace( 'task state [%s]: notification user option activated, mail to sent' % self.state )
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_KILLED and notifs_bool[5]:
                self.trace( 'task state [%s]: notification user option activated, mail to sent' % self.state )
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_CANCELLED and notifs_bool[6]:
                self.trace( 'task state [%s]: notification user option activated, mail to sent' % self.state )
                self.sendMail(userTo=user_profile['email'])
            else:
                self.trace( 'task state: notification on this state not authorized: %s' % self.state )

            if self.verdict == StatsManager.PASS and notifs_bool[0]:
                self.trace( 'test verdict [%s]: notification user option activated, mail to sent' % self.verdict )
                self.sendMail(userTo=user_profile['email'])
            elif self.verdict == StatsManager.FAIL and notifs_bool[1]:
                self.trace( 'test verdict [%s]: notification user option activated, mail to sent' % self.verdict )
                self.sendMail(userTo=user_profile['email'])
            elif self.verdict == StatsManager.UNDEFINED and notifs_bool[2]:
                self.trace( 'test verdict [%s]: notification user option activated, mail to sent' % self.verdict )
                self.sendMail(userTo=user_profile['email'])
            else:
                self.trace( 'test verdict: notification with this verdict not authorized: %s' % self.verdict )

    def sendMail(self, userTo):
        """
        """
        self.trace( 'send mail to %s' % userTo )

        # new in v16
        basicReport = True
        if Settings.getInt( 'Notifications', 'advanced-report-by-email'):
            basicReport= False
        # end of new
        
        mailBody = self.getTestReport(zipped=False, b64encoded=False, basicReport=basicReport)
        appAcronym = Settings.get( 'Server', 'acronym')
        subject = "[%s] %s %s: %s" % (appAcronym.upper(), self.testType, self.verdict, self.testName)
        self.trace("Mail to sent(subject): %s" % subject)

        TaskMngr.sendMail(  to=userTo, 
                            subject=subject,
                            body=mailBody
                        )

    def killTest(self, removeFromContext=True):
        """
        Kill the test

        @param removeFromContext:
        @type removeFromContext: boolean

        @return:
        @rtype: boolean
        """
        self.removeFromContext = removeFromContext
        
        # reset all agents and probes before to kill the test
        # some threads can be running
        for t, details in TSI.instance().testsConnected.items():
            # test detected: {'task-id': '4', 'agents': [], 'connected-at': 1446189597.512704, 'probes': []}
            if "task-id" in details:
                if int(details["task-id"]) == int(self.getId()):
                    self.trace("nb probes to reset before to kill: %s" % len(details["probes"]))
                    self.trace("nb agents to reset before to kill: %s" % len(details["agents"]))
                    TSI.instance().resetRunningProbe(client=details)
                    TSI.instance().resetRunningAgent(client=details)
                    break
        
        # send kill signal
        killed = self.handleSignal( sig=SIGNAL_KILL )

        return killed
        
    def handleSignal(self, sig):
        """
        Handle unix signal

        @param sig:
        @type sig:

        @return:
        @rtype: boolean
        """
        success = True
        if sig == SIGNAL_KILL and self.tpid is not None:
            try:
                os.kill(self.tpid, signal.SIGKILL)
            except Exception as e:
                self.error( "Unable to kill %d: %s" % (self.tpid, str(e)) )
                success = False
        return success

class TaskManager(Scheduler.SchedulerThread, Logger.ClassLogger):
    def __init__(self):
        """
        Construct Task Manager
        """
        Scheduler.SchedulerThread.__init__(self, out=self.trace, err=self.error)
        self.mutex = threading.RLock()
        self.tasks = []
        self.enqueuedTasks = {}
        self.TN_HISTORY = '%s-tasks-history' % Settings.get( 'MySql', 'table-prefix')
        self.BACKUPS_TASKS = '%s/%s/Tasks/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'backups'))

    def addChildPid(self, pid):
        """
        Save the PID of the child to kill it on stop if always running
        """
        self.trace("adding child pid %s" % pid)
        file("%s/%s/%s.pid" % (Settings.getDirExec(), Settings.get('Paths','run'),pid),'w+').write("%s\n" % pid)

    def delChildPid(self, pid):
        """
        Delete the PID of the child to kill it on stop if always running
        """
        self.trace("removing child pid %s" % pid)
        try:
            os.remove("%s/%s/%s.pid" % (Settings.getDirExec(), Settings.get('Paths','run'),pid) )
        except IOError:
            pass

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="TKM - %s" % txt)

    def getEnqueued(self, b64=False):
        """
        Returns all enqueued task 

        @return: all enqueued events from the database
        @rtype: dict
        """
        enqueuedTasks = {}
        for (grpId, grpTests) in self.enqueuedTasks.items():
            __grpTests = []
            for tst in grpTests:
                grpTst = {}
                grpTst['test-path'] = tst['test-path']
                grpTst['test-name'] = tst['test-name']
                grpTst['test-extension'] = tst['test-extension']
                grpTst['prj-id'] = int(tst['prj-id'])
                
                __grpTests.append( str(grpTst) )

            enqueuedTasks[ grpId[0] ] = [ grpId[1] , __grpTests ]

        if not b64:
            return enqueuedTasks
        else:
            return self.encodeData(data=enqueuedTasks)

    def cancelTaskInQueue(self, groupId, userName):
        """
        Cancel task in queue
        """
        self.trace('Canceling group of test %s' % groupId)
        if (groupId, userName) in self.enqueuedTasks:
            self.enqueuedTasks.pop( (groupId, userName) )

        # notify user
        data = ( 'task-enqueued', ( "update", self.getEnqueued()) )   
        ESI.instance().notifyAll(body = data)

    def runQueueNextTask(self, groupId, userName):
        """
        Run next task from the queue
        """
        try:
            if (groupId, userName) in self.enqueuedTasks:
                testsUser =  self.enqueuedTasks[ (groupId, userName) ]
                if len(testsUser):
                    tst = testsUser.pop(0)
                  
                    # re-put in the queue
                    if len(testsUser):
                        self.enqueuedTasks[ (groupId, userName) ] = testsUser
                    else:
                        # no more tests to run
                        self.enqueuedTasks.pop( (groupId, userName) )

                    # finally run the test
                    self.runQueueTask(tst=tst, groupId=groupId, userName=userName)
                else:
                    self.enqueuedTasks.pop( (groupId, userName) )
                    self.trace('tasks group id %s not exists (a) for user %s' % (groupId, userName) )
            else:
                self.trace('tasks group id %s not exists (b) for user %s' % (groupId, userName) )
        except Exception as e:
            self.error('queue run, unable to run the next one: %s' % e )


        # notify user
        data = ( 'task-enqueued', ( "update", self.getEnqueued()) )   
        ESI.instance().notifyAll(body = data)

    def addTasks(self, userName, tests, runAt=(0,0,0,0,0,0), queueAt=False, simultaneous=False ):
        """
        Adding tasks on the queue
        """
        self.trace('Nb test to enqueue: %s Login=%s' % (len(tests), userName))

        # enqueue tests to run
        groupId =  getGroupId()

        # try to run tasks in simultaneous ?
        if simultaneous:
            self.runTasksInSimultaneous(tests=tests, groupId=groupId, userName=userName,
                                        runAt=runAt, queueAt=queueAt)
        else:

            self.enqueuedTasks[ (groupId, userName) ] = tests
            # notify user
            data = ( 'task-enqueued', ( "update", self.getEnqueued()) )   
            ESI.instance().notifyAll(body = data)

            # take the first one
            tst = tests.pop(0)

            # if the list is not yet empty than save it again
            if len(tests):
                self.enqueuedTasks[ (groupId, userName) ] = tests

            # register the first test
            self.runQueueTask(tst=tst, groupId=groupId, userName=userName, runAt=runAt, queueAt=queueAt)

        return True

    def runTasksInSimultaneous(self, tests, groupId, userName, runAt=(0,0,0,0,0,0), queueAt=False):
        """
        Run tasks in simultaneous
        """
        self.trace("run tasks in simultaneous")
        # get user id
        usersDb = UsersManager.instance().getUsersByLogin()
        user_profile = usersDb[userName]
        
        runType = SCHED_QUEUE
        if queueAt: runType = SCHED_QUEUE_AT
        
        for tst in tests:
            try:
                kwargs = { 'testData': tst['test-data'], 'testName': tst['test-name'], 'testPath': tst['test-path'], 
                        'testUserId': user_profile['id'], 'testUser': userName, 'testId': groupId, 'testBackground': True,
                        'runAt': runAt, 'runType': runType, 'runNb': -1, 'withoutProbes': False,
                        'debugActivated': False, 'withoutNotif': False, 'noKeepTr': False,
                        'testProjectId': tst['prj-id'], 'runFrom': (0,0,0,0,0,0), 'runTo': (0,0,0,0,0,0),
                        'groupId': groupId, 'runSimultaneous': True }

                testThread = threading.Thread(target = self.registerTask, kwargs=kwargs ) 
                testThread.start()
            except Exception as e:
                self.error( "group simultaneous tasks, error detected: %s" % e )
        
    def runQueueTask(self, tst, groupId, userName, runAt=(0,0,0,0,0,0), queueAt=False ):
        """
        Run the task from queue
        """

        # get user id
        usersDb = UsersManager.instance().getUsersByLogin()
        user_profile = usersDb[userName]

        runType = SCHED_QUEUE
        if queueAt:
            runType = SCHED_QUEUE_AT
        try:
            task = self.registerTask( 
                        testData=tst['test-data'], testName=tst['test-name'], testPath=tst['test-path'], testUserId=user_profile['id'],
                        testUser=userName, testId=groupId, testBackground=True,
                        runAt=runAt, runType=runType, runNb=-1, withoutProbes=False,
                        debugActivated=False, withoutNotif=False, noKeepTr=False,
                        testProjectId=tst['prj-id'], runFrom=(0,0,0,0,0,0), runTo=(0,0,0,0,0,0),
                        groupId=groupId
                    )
        except Exception as e:
            self.error( "group tasks, error detected: %s" % e )
            self.runQueueNextTask(groupId=groupId, userName=userName)
        else:
            if task.lastError is not None:
                self.error( "group tasks: error detected on task: %s" % task.lastError )
                self.runQueueNextTask(groupId=groupId, userName=userName)
        del tst

    def sendMail(self, to, subject, body):
        """
        """
        self.trace( 'sendmail to %s' % to )
        try:
            sendmail_location = Settings.get( 'Bin', 'sendmail')
            p = os.popen("%s -t" % sendmail_location, "w")
            email_dest = "%s@%s.com" % ( Settings.get( 'Server', 'acronym'), Settings.get( 'Server', 'acronym') )
            p.write("From: %s\n" % email_dest)
            p.write("To: %s\n" % to)
            p.write("Subject: %s\n" % subject.encode('utf-8'))

            p.write("Content-Type: multipart/mixed; boundary=\"-q1w2e3r4t5\"\n")
            p.write("MIME-Version: 1.0\n")
            p.write("\n")

            p.write("---q1w2e3r4t5\n")
            p.write("Content-Type: text/html\n")
            p.write("Content-Disposition: inline\n")
            p.write("\n")
            p.write("<html><body>Extensive Testing Report in attachment :)</body></html>\n")


            p.write("---q1w2e3r4t5\n")
            p.write("Content-Transfer-Encoding: base64\n")
            p.write("Content-Type: application/octet-stream; name=extensive_test_report.html\n")
            p.write("Content-Disposition: attachment; filename=extensive_test_report.html\n")
            p.write("\n")
            p.write(base64.b64encode(body.encode("utf-8")))
            p.write("\n")
            p.write("---q1w2e3r4t5--")

        except Exception as e:
            self.error( "unable prepare send mail: %s" % e)
            
        try:
            status = p.close()
            if status is not None:
                if status != 0 :
                    self.error( "sendmail status: %s" % status )
                else:
                    self.trace( "Mail sent!" )
        except Exception as e:
            self.error( "unable to send mail: %s" % e)
            
    def addToHistory(self, task):
        """
        Called when the script is stopped

        @type  task:
        @param task:
        """
        ret = None
        try:
            sql = "INSERT INTO `%s`( `eventtype`,`eventargs`,`eventtime`,`eventname`,`eventauthor`,`realruntime`,`eventduration`,`eventresult`,`projectid`)" % self.TN_HISTORY
            sql += "VALUES(%s, \"%s\", %s, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s)" % task.toTuple()
            ret, lastinsertid = DbManager.instance().querySQL(sql, insertData=True)
        except Exception as e:
            self.error('unable to add task to history: %s' % str(e) )
        return ret, lastinsertid
    
    def loadBackups(self):
        """
        Load backup from the var storage
        Function called on boot
        """
        if not Settings.getInt('Boot','reload-tasks'):
            return None
        
        # Rename all backups files to avoid overwrite
        for fb in  os.listdir( self.BACKUPS_TASKS ) :
            try:
                currentName = '%s/%s' % (self.BACKUPS_TASKS,fb)
                newName = '%s/BACKUP_%s' % (self.BACKUPS_TASKS,fb)
                os.rename( currentName, newName  )
            except Exception as e:
                self.error( 'unable to rename backup file %s: %s' % ( fb, str(e)) )

        # Load file prefixed with BACKUP_
        backupsList = os.listdir( self.BACKUPS_TASKS )
        success = True
        for fb in backupsList :
            if not fb.startswith( "BACKUP_" ):
                continue
            if not os.path.isfile( '%s/%s' % (self.BACKUPS_TASKS,fb) ):
                continue
            # Read backup file
            taskData = self.readBackup( backupFile = '%s/%s' % (self.BACKUPS_TASKS,fb) )
            if taskData is None:
                success = False
            else:
                # Unpack data 
                testName, userName, testPath, testName, dataTest, testId, background, schedType, schedAt, schedNb, \
                enabled, withoutProbes, withoutNotif, noKeepTr, userId, projectId, schedFrom, schedTo = taskData
                self.trace( "Loading backup [Sched-Type=%s] [Sched-At=%s] [Sched-Nb=%s] [TestName=%s]" % (schedType, schedAt, schedNb, testName) )
                self.trace( "Loading backup. [UserName=%s] [Background=%s] [Enabled=%s] [WithoutProbes=%s] [WithoutNotif=%s]" % (userName, background, enabled, withoutProbes, withoutNotif) )
                self.trace( "Loading backup.. [NoKeepTr=%s] [UserId=%s] [ProjectId=%s] [Sched-From=%s] [Sched-To=%s]" % (noKeepTr, userId, projectId, schedFrom, schedTo) )

                # Remove backup file
                self.trace( 'deleting old backup %s' % fb )
                try:
                    os.remove( '%s/%s' % (self.BACKUPS_TASKS,fb) )
                except Exception as e:
                    self.error( 'unable to delete the old backup: %s' % str(e) )
                    success = False
                try:
                    if success:
                        try:
                            task = self.reloadTask( testData=dataTest, testName=testName, testPath=testPath, testUser=userName,
                                                    testId=testId, testBackground=background, runAt=schedAt, runType=schedType,
                                                    runNb=schedNb, runEnabled=enabled, withoutProbes=withoutProbes, withoutNotif=withoutNotif,
                                                    noKeepTr=noKeepTr, testUserId=userId, testProjectId=projectId, runFrom=schedFrom, runTo=schedTo )
                            if task is None:
                                success = False
                        except Exception as e:
                            success = False
                            self.error( 'unable to reload task: %s' % str(e) )
                except Exception as e:
                    self.error( 'unable to reload task: %s' % str(e) )
                    success = False
        return success

    def readBackup(self, backupFile):
        """
        Read backup from the var storage

        @type  backupFile:
        @param backupFile:
        """
        self.trace( 'reading backup %s' % backupFile )
        rlt = None
        try:
            fd = open( backupFile , "r")
            data = fd.read()
            fd.close()
            rlt = pickle.loads( data )
        except Exception as e:
            self.error( 'unable to read backup: %s' % str(e) )
        return rlt

    def backupTask(self, task):
        """
        Backup the task to the var storage

        @type  task:
        @param task:

        @return:
        @rtype: boolean
        """
        self.trace( 'backuping task %s' % task.getId() )
        try:
            backup_name = "%s/%s.dat" % ( self.BACKUPS_TASKS, task.getId() ) 
            fd = open( backup_name, 'wb')
            # new in 3.1.0
            schedAt = task.schedAt
            if task.schedType == SCHED_EVERY_X or task.schedType == SCHED_WEEKLY:
                schedAt = task.schedArgs
            # end
            data_task = [ task.testName, task.userName, task.testPath, task.testName, task.dataTest,
                          task.testId, task.background, task.schedType, schedAt, task.schedNb, task.enabled,
                          task.withoutProbes, task.withoutNotif, task.noKeepTr, task.userId, task.projectId,
                          task.schedFrom, task.schedTo]
            fd.write( pickle.dumps( data_task ) )
            fd.close()
        except Exception as e:
            self.error( 'unable to backup the task %s: %s' % (task.getId(), str(e)) )
            return False
        return True

    def deleteBackup(self, task):
        """
        Delete backup from the var storage

        @type  task:
        @param task:

        @return:
        @rtype: boolean
        """
        self.trace( 'deleting backup task %s' % task.getId() )
        try:
            backup_name = "%s/%s.dat" % ( self.BACKUPS_TASKS, task.getId() ) 
            os.remove( backup_name )
        except Exception as e:
            self.error( 'unable to delete the backup of the the task %s: %s' % (task.getId(), str(e)) )
            return False
        return True

    def encodeData(self, data):
        """
        """
        ret = ''
        try:
            #tasks_json = json.dumps(data)
            tasks_json = json.dumps(data, ensure_ascii=False) # change in v12.1
        except Exception as e:
            self.error( "Unable to encode in json: %s" % str(e) )
        else:
            try: 
                tasks_zipped = zlib.compress(tasks_json)
            except Exception as e:
                self.error( "Unable to compress: %s" % str(e) )
            else:
                try: 
                    ret = base64.b64encode(tasks_zipped)
                except Exception as e:
                    self.error( "Unable to encode in base 64: %s" % str(e) )
        return ret

    def getHistory(self, Full=False, b64=False, user=None):
        """
        Get the task history from database

        @return: all history from the database
        @rtype: list
        """
        historyTasks = []
        # new in v10, return only running task according to the user
        if user is not None:
            if isinstance(user, Context.UserContext):
                prjs = user.getProjects(b64=False)
            else:
                prjs = ProjectsManager.instance().getProjects( user=user, b64=False)
        # end of new in v10
        
        sql = """SELECT `id`, `eventtype`, `eventargs`, `eventtime`, `eventname`, `eventauthor`, `realruntime`, `eventduration`, `eventresult`, `projectid` FROM `%s` """ % self.TN_HISTORY
        # new in v10, return only history task according to the user
        if user is not None:
            sql += " WHERE "
            sqlMore = []
            for prj in prjs:
                sqlMore.append( "`projectid`=%s" % int(prj['project_id']) )
            sql += " OR " .join(sqlMore)   
        # end of new in v10
        
        ret, rows = DbManager.instance().querySQL( query = sql)
        if ret:
            if Settings.getInt( 'WebServices', 'nb-tasks-history' ) == -1:
                historyTasks = rows
            else:
                siz = len(rows) - Settings.getInt( 'WebServices', 'nb-tasks-history' )
                if Full:
                    historyTasks = rows
                else:
                    historyTasks = rows[siz:]
        else:
            self.error( 'unable to get history event from database' )
        if b64:
            historyTasks = self.encodeData(data=historyTasks)
        return historyTasks

    def getWaiting(self, b64=False, user=None):
        """
        Returns all waiting task 

        @return: all waiting events from the database
        @rtype: list
        """
        waitingTasks = []
        # new in v10, return only running task according to the user
        if user is not None:
            if isinstance(user, Context.UserContext):
                prjs = user.getProjects(b64=False)
            else:
                prjs = ProjectsManager.instance().getProjects( user=user, b64=False)
            prjsDict = {}
            for prj in prjs: prjsDict[ int(prj['project_id']) ] = True
        # end of new in v10
        
        for task in self.tasks:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                if user is None:
                    waitingTasks.append( task.toTuple(withId=True, withGroupId=True) )
                else:
                    # new in v10
                    if int(task.projectId) in prjsDict: 
                        waitingTasks.append( task.toTuple(withId=True, withGroupId=True) )
                    # end of new in v10
        if b64:
            waitingTasks = self.encodeData(data=waitingTasks)
        return waitingTasks

    def getRunning(self, b64=False, user=None):
        """
        Returns all running tasks

        @return: all running tasks
        @rtype: list
        """
        runningTasks = []
        # new in v10, return only running task according to the user
        if user is not None:
            if isinstance(user, Context.UserContext):
                prjs = user.getProjects(b64=False)
            else:
                prjs = ProjectsManager.instance().getProjects( user=user, b64=False)
            prjsDict = {}
            for prj in prjs: prjsDict[ int(prj['project_id']) ] = True
        # end of new in v10
        
        for task in self.tasks:
            if task.state == STATE_RUNNING:
                if user is None:
                    runningTasks.append( task.toDict() )
                else:
                    # new in v10
                    if int(task.projectId) in prjsDict: 
                        runningTasks.append( task.toDict() )
                    # end of new in v10
        if b64:
            runningTasks = self.encodeData(data=runningTasks)
        return runningTasks
    
    def getTask (self, taskId):
        """
        Returns the task corresponding to the id passed as argument, otherwise None

        @param taskId:
        @type taskId:

        @return:
        @rtype:
        """
        ret = None
        for task in self.tasks:
            if task.getId() == taskId:
                return task
        return None

    def executeTask (self, task, needPrepare=True):
        """
        Execute the task gived on argument

        @param task:
        @type task:
        """
        self.info("Starting test %s" % task.getId() )   
        testThread = threading.Thread(target = lambda: task.run(needPrepare=needPrepare)) 
        testThread.start()
    
    def replayTask (self, tid):
        """
        Replay the task 

        @param tid:
        @type tid:

        @return:
        @rtype: boolean
        """
        self.trace( "replaying task" )
        task = self.getTask( taskId = tid )
        if task is None:
            self.error( 'task %s not found' % tid )
            return False
        task.setReplayId()
        testRegistered = TSI.instance().registerTest( id =  task.getId() , background = task.background )
        if not testRegistered:
            msg_err = 'unable to register the task in the system'
            self.error( msg_err )
            return False
        
        self.trace( "Re-backup the test" )
        taskBackuped = self.backupTask(task=task)
        if not taskBackuped :
            msg_err = 'Unable to backup the task in the system'
            self.error( msg_err )
            return False

        self.executeTask( task = task )
        return True

    def reloadTask(self, testData, testName, testPath, testUser, testId, testBackground, runAt,
                        runType, runNb, runEnabled, withoutProbes, withoutNotif, noKeepTr, testUserId, testProjectId, 
                         runFrom, runTo):
        """
        Reload a specific task

        @param testData:
        @type testData:

        @param testName:
        @type testName:

        @param testPath:
        @type testPath:

        @param testUser:
        @type testUser:

        @param testId:
        @type testId:

        @param testBackground:
        @type testBackground:

        @param runAt:
        @type runAt:

        @param runType:
        @type runType:

        @param runNb:
        @type runNb:
        
        @param runEnabled:
        @type runEnabled:

        @return:
        @rtype: 
        """
        self.trace( "reloading task" )
        toReload=True
        if runType == Scheduler.SCHED_AT or runType == Scheduler.SCHED_IN:
            timeref = time.time()
            if runAt < timeref:
                toReload=False
        if runType > Scheduler.SCHED_IN:
            toReload=True
        if runType == Scheduler.SCHED_NOW:
            toReload=False
        if runType == SCHED_QUEUE:
            toReload=False
        if runType == SCHED_QUEUE_AT:
            toReload=False
        if toReload:
            return self.registerTask(   testData=testData, testName=testName, testPath=testPath, testUserId=testUserId,
                                        testUser=testUser, testId=testId, testBackground=testBackground,
                                        runAt=runAt, runType=runType, runNb=runNb, runEnabled=runEnabled,
                                        withoutProbes=withoutProbes, withoutNotif=withoutNotif, noKeepTr=noKeepTr, 
                                        testProjectId=testProjectId,
                                        runFrom=runFrom, runTo=runTo
                                    )
        else:
            return None

    def noMoreLeftSpace(self):
        """
        Checking left space before running the test
        """
        mbUsed =  RepoArchives.instance().getSizeRepoV2(folder=RepoArchives.instance().testsPath)
        mbFree = RepoArchives.instance().freeSpace(p=RepoArchives.instance().testsPath)
        
        mbMax = int(mbUsed) + int(mbFree)
        mbUsedPercent = (mbUsed * 100) / mbMax  
        mbMaxSettings = Settings.getInt( 'Supervision', 'usage-testresult-max' )
        
        self.trace( "MB used/free: %s/%s" % (mbUsed, mbFree) )
        self.trace( "MB used in percent/max: %s/%s" % (mbUsedPercent,mbMaxSettings) )
        if mbUsedPercent >= mbMaxSettings:
            return True
        else:
            return False

    def registerTask(self, testData, testName, testPath, testUser, testId, testBackground, runAt, runType, runNb, runEnabled=True,
                    withoutProbes=False, debugActivated=False, withoutNotif=False, noKeepTr=False, testUserId=0, testProjectId=0,
                    runFrom=(0,0,0,0,0,0), runTo=(0,0,0,0,0,0), groupId=None, stepByStep=False, breakpoint=False, runSimultaneous=False,
                    channelId=False):
        """
        - Get id from the scheduler
        - Check the syntax of test on the temp environment
        - Register the test in the TSI
        - Change the task's state from INIT to WAITING
        - Register the task in the scheduler
        - Save the task in the list and notify all connected users

        @param testData:
        @type testData:

        @param testName:
        @type testName:

        @param testPath:
        @type testPath:

        @param testUser:
        @type testUser:

        @param testId:
        @type testId:

        @param testBackground:
        @type testBackground:

        @param runAt:
        @type runAt:

        @param runType:
        @type runType:

        @return:
        @rtype:
        """
        self.mutex.acquire()
        self.trace( "Scheduling task" )
        
        self.trace( "Registering task [Run-Type=%s] [Run-At=%s] [Run-Nb=%s] [TestName=%s] [TestUser=%s]" % (runType, runAt, runNb, testName, testUser) )
        self.trace( "Registering task. [InBackground=%s] [Run-Enabled=%s] [WithoutProbes=%s] [Debug=%s] [Notif=%s]" % (testBackground, runEnabled, withoutProbes, debugActivated, withoutNotif) )
        self.trace( "Registering task.. [NoKeepTr=%s] [UserId=%s] [ProjectId=%s] [Run-From=%s]" % (noKeepTr, testUserId, testProjectId, runFrom) )
        self.trace( "Registering task... [Run-To=%s] [StepByStep=%s] [Breakpoint=%s] [ChannelId=%s]" % (runTo, stepByStep, breakpoint, channelId) )

        task = Task(    testData=testData, testName=testName, testPath=testPath, testUser=testUser, testId=testId, testUserId=testUserId,
                        testBackground=testBackground, taskEnabled=runEnabled, withoutProbes=withoutProbes, debugActivated=debugActivated,
                        withoutNotif=withoutNotif, noKeepTr=noKeepTr, testProjectId=testProjectId, stepByStep=stepByStep, breakpoint=breakpoint,
                        runSimultaneous=runSimultaneous, channelId=channelId)
        task.setId( self.getEventId() )

        if groupId is not None:
            self.trace( "Group tasks id=%s" % groupId )
            task.setGroupId(groupId=groupId)
                   
        self.trace( "Checking left space on %s before to schedule the test"  % Settings.get( 'Paths', 'testsresults' ))
        if self.noMoreLeftSpace():
            self.error( 'No more space left on %s' % Settings.get( 'Paths', 'testsresults' )  )
            task.lastError = 'No more space left on %s' % Settings.get( 'Paths', 'testsresults' )
            self.mutex.release()
            return task
        else:
            self.trace("disk usage ok? yes, continue")
            
        self.trace( "Prepare the task %s and check the syntax" % task.getId() )
        # Prepare the test and check if the syntax is correct
        try:
            task.initPrepare()
            task.prepare(envTmp=True)
        except Exception as e: # task state is changed to ERROR
            task.lastError = 'Unable to prepare: %s' % str(e) 
            self.mutex.release()
            return task
        else:
            task.setSyntaxOK()
        
        self.trace( "Register the task %s on the TSI" % task.getId() )
        # Register the test in the TSI
        testRegistered = TSI.instance().registerTest( id =  task.getId() , background = task.background )
        if not testRegistered:
            task.lastError = 'Unable to:\n\ - Register the task in the system'
            self.error( task.lastError )
            self.mutex.release()
            return task
        
        self.trace( "Initialize the start time of task %s" % task.getId() )
        task.schedNb = runNb
        # Initialize the task with the start time 
        if isinstance(runAt, tuple) or isinstance(runAt, list):
            self.trace( "Task %s init" % task.getId() )
            timesec = task.initialize( runAt=runAt, runType=runType, runNb=runNb, runEnabled=runEnabled, withoutProbes=withoutProbes, 
                                        debugActivated=debugActivated, withoutNotif=withoutNotif, noKeepTr=noKeepTr,
                                       runFrom=runFrom, runTo=runTo)
            self.trace( "Task %s should run at %s" % (task.getId(),timesec) )
        else:
            self.trace( "Task %s init manual" % task.getId() )
            task.schedAt = runAt
            task.schedType = runType
            task.schedArgs = self.getTimeToTuple( task.schedAt )
            timesec = task.schedAt

        if task.isRecursive():
            self.trace( "Task %s is recursive" % task.getId() )
            schedExceptions = [SCHED_NOW_MORE]
            if Settings.getInt( 'TaskManager', 'everyminx-run-immediately' ):
                schedExceptions.append(SCHED_EVERY_X)
            if task.schedType not in schedExceptions:
                timeref = time.time()
                while timesec < timeref:
                    self.trace( "Catches up the late for the task %s" % task.getId()  )
                    timesec = self.getNextTime( schedType=task.schedType, shedAt=task.schedAt, schedArgs=task.schedArgs,
                                                schedFrom=runFrom, schedTo=runTo)
                    task.schedAt = timesec
                    # BEGIN new in 3.2.0
                    if task.schedType == SCHED_WEEKLY:
                        pass
                    # END
                    else:
                        task.schedArgs = self.getTimeToTuple( task.schedAt )
        
        # Change the state from INIT to WAITING
        task.setState(state = STATE_WAITING)    
        
        self.trace( "Backup the task %s" % task.getId() )
        # Backup the task on the disk
        taskBackuped = self.backupTask(task=task)
        if not taskBackuped :
            task.lastError = 'Unable to:\n\n - Backup the task in the system'
            self.error( task.lastError )
            self.mutex.release()
            return task

        needPrepare = True
        if runType == Scheduler.SCHED_NOW:
            self.trace( "Prepare the task %s in the prod environment" % task.getId() )
            prep = task.prepare(envTmp=False)
            needPrepare = False
            self.trace( "Prepare the task %s ok ? %s" % (task.getId(),prep) )
            
        self.trace( "Register the task %s on the scheduler" % task.getId() )
        # Register the task on the scheduler
        EventReg = self.registerEvent(  id=task.getId(), author=task.userName, name=task.getTaskName(), 
                                        weekly=None, daily=None, hourly=None, everyMin=None, everySec=None, at=None, 
                                        delay=None, timesec=timesec,
                                        callback = self.executeTask, task = task, needPrepare=needPrepare)
        task.setEventReg( event=EventReg )

        if not runEnabled:
            self.trace('Unregister the task %s from the scheduler' % task.getId())
            taskDisabled = TaskMngr.unregisterEvent( event = task.eventReg)
            if not taskDisabled:
                self.error( 'unable to unregister the following task %s' % task.getId() )
                task.setState( state=STATE_ERROR )
            else:
                task.setState( state=STATE_DISABLED )
                self.info( 'Task %s disabled' % str(task.getId()) ) 

        #  Save the task on the list and notify all connected users
        self.tasks.append(task)     
        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-waiting', ( "update", self.getWaiting(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        self.info( "Task registered with id %s" % task.getId() )

        self.mutex.release()
        return task

    def killTask(self, taskId):
        """
        Kill a specific running task

        @param taskId:
        @type taskId:

        @return:
        @rtype:
        """
        self.trace( "killing task %s" % taskId )
        success = None
        task = self.getTask( taskId = taskId )
        if task is None:
            self.error( 'task %s not found' % taskId )
        else:
            if task.state == STATE_RUNNING:
                task.setState( state=STATE_KILLING )
                killed = task.killTest()
                if killed:
                    success = taskId
                    self.info( 'Task %s killed' % str(taskId) ) 
        return success
    
    def killAllTasks(self):
        """
        Kill all running tasks

        @return:
        @rtype:
        """
        self.trace( "killing all tasks" )
        success = True
        tasksToRemove = []
        for task in self.tasks:
            if task.state == STATE_RUNNING:
                task.setState( state=STATE_KILLING )
                killed = task.killTest(removeFromContext=False)
                if not killed:
                    success = False
                else:
                    tasksToRemove.append(task)
        for task in tasksToRemove:
            self.removeTask(task=task)
        del tasksToRemove
        return success

    def cancelTask(self, taskId):
        """
        Cancel a specific waiting task

        @return:
        @rtype:
        """
        self.trace( "cancelling task %s" % taskId )
        success = None
        task = self.getTask( taskId = taskId )
        if task is None:
            self.error( 'task %s not found' % taskId )
        else:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                taskCancelled = task.cancelTest()
                if not taskCancelled:
                    self.error( 'unable to cancel the following task %s' % task.getId() )
                else:
                    success = taskId
                    self.info( 'Task %s cancelled' % str(taskId) ) 

        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-waiting', ( "update", self.getWaiting(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success

    def cancelAllTasks(self):
        """
        Cancel all waiting tasks

        @return:
        @rtype:
        """
        self.trace( "cancelling all tasks" )
        success = True
        tasksToRemove = []
        for task in self.tasks:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                taskCancelled = task.cancelTest(removeFromContext=False)
                if not taskCancelled:
                    self.error( 'unable to cancel the following task %s' % task.getId() )
                    success = False
                else:
                    tasksToRemove.append(task)
        for task in tasksToRemove:
            self.removeTask(task=task)
        del tasksToRemove       

        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-waiting', ( "update", self.getWaiting(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success

    def clearHistory(self):
        """
        Clear history from database
        """     
        self.trace( "clearing task history" )
        try: 
            sql = "DELETE FROM `%s`;" % self.TN_HISTORY
            ret, rows = DbManager.instance().querySQL(sql)
            if not ret:
                raise Exception("sql problem: %s" % self.TN_HISTORY)
        except Exception as e:
            self.error('unable to delete all tasks from history: %s' % str(e) )
            
        # notify all connected users
        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-history', ( "update", self.getHistory(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        
    def onTaskFinished(self, task):
        """
        Called when a task is finished

        @param task:
        @type task:
        """
        self.trace( "Re-scheduling task %s..." % task.getId() )

        self.trace( "Checking left space on %s before to re-schedule the test"  % Settings.get( 'Paths', 'testsresults' ))
        if self.noMoreLeftSpace():
            # Remove the task on the list
            self.removeTask( task=task )
            
            self.error( 'No more space left on %s' % Settings.get( 'Paths', 'testsresults' )  )
            # notify user
            data = ( 'supervision', ( "level-critical", 'Test execution stopped!\nNo more space left on %s' % Settings.get( 'Paths', 'testsresults' )) )   
            ESI.instance().notifyAll(body = data)
        else:
            self.trace("disk usage ok? yes, continue")
            
        # Remove the task from the disk
        backupDeleted = self.deleteBackup( task=task )
        if not backupDeleted:
            self.trace( "unable to delete the backup of the task %s" % task.getId() )
        
        # Remove the task from the context if in the following states: cancelled, error and killed
        if task.state in [ STATE_CANCELLED, STATE_ERROR, STATE_KILLED ]:
            if task.removeFromContext:
                self.removeTask( task=task )

        # Exit if the task going from the queue
        if task.groupId > 0 :
            if not task.runSimultaneous:
                self.trace( "Group of tasks %s detected, running the next one? yes" % task.groupId )
                if task.state in [STATE_CANCELLED]:
                    self.cancelTaskInQueue(groupId=task.groupId, userName=task.userName)
                else:
                    self.runQueueNextTask(groupId=task.groupId, userName=task.userName)
                return
        else:
            self.trace( "No group id %s, running the next one ? no" % task.getId() )

        # Exit if the task is not recursive
        if not task.isRecursive(): 
            self.trace( "task %s is recursive? no" % task.getId() )
            return
        else:
            self.trace( "task %s is recursive? yes" % task.getId() )

        # Exit if the task is not in the complete state
        if task.state != STATE_COMPLETE:            
            self.trace( "task %s is completed? no" % task.getId()  )
            return
        else:
            self.trace( "task %s is completed? yes so continue" % task.getId() )

        # check the counter of run
        if not task.runAgain():
            self.trace( "Run again task %s? no more run" % task.getId() )
            return
        else:
            self.trace("Run again task %s? yes" % task.getId() )

        # check the interval
        if not task.alwaysRun():
            self.trace( "Always run task %s? no more run" % task.getId() )
            #return
        else:
            self.trace("Always run task %s? yes" % task.getId() )

        # create a new task 
        taskNew = Task(     
                            testData=task.dataTest, testName=task.testName, testPath=task.testPath, testUser=task.userName, 
                            testId=task.testId,  testUserId=task.userId, testBackground=task.background, 
                            taskEnabled=task.enabled, withoutProbes=task.withoutProbes, withoutNotif=task.withoutNotif,
                            debugActivated=task.debugActivated, noKeepTr=task.noKeepTr, testProjectId=task.projectId,
                            stepByStep=task.stepByStep, breakpoint=task.breakpoint,
                            runSimultaneous=task.runSimultaneous, channelId=task.channelId
                        )
        taskNew.taskUuid = task.taskUuid
        taskNew.setId( self.getEventId() )
        taskNew.initPrepare()
        taskNew.setPrepared()
        taskNew.recurId = task.recurId + 1
        taskNew.resultsStats = task.resultsStats
        
        # Register the test on the TSI
        testRegistered = TSI.instance().registerTest( id =  taskNew.getId() , background = taskNew.background )
        if not testRegistered:
            msg_err = 'unable to re-register the task in the system'
            self.error( msg_err )
            # Remove the task on the list
            self.removeTask( task=task )
            return

        # Initialize the task with the start time 
        taskNew.schedNb = task.schedNb
        taskNew.schedType = task.schedType
        taskNew.schedFrom = task.schedFrom
        taskNew.schedTo = task.schedTo
        taskNew.schedAt = self.getNextTime( schedType=task.schedType, shedAt=task.schedAt, schedArgs=task.schedArgs,
                                            schedFrom=task.schedFrom, schedTo=task.schedTo)
        if taskNew.schedType == SCHED_EVERY_X or taskNew.schedType == SCHED_WEEKLY:
            taskNew.schedArgs = task.schedArgs
        else:
            taskNew.schedArgs = self.getTimeToTuple( taskNew.schedAt )

        # Change the state from INIT to WAITING
        taskNew.setState(state = STATE_WAITING)     

        # Backup the task on the disk
        taskBackuped = self.backupTask(task=taskNew)
        if not taskBackuped :
            msg_err = 'unable to re-backup the task in the system'
            self.error( msg_err )
            self.mutex.release()
            return msg_err

        # Register the task on the scheduler
        EventReg = self.registerEvent(  id=taskNew.getId(), author=taskNew.userName, name=taskNew.getTaskName(), 
                                        weekly=None, daily=None, hourly=None, everyMin=None, everySec=None, at=None, delay=None, timesec=taskNew.schedAt,
                                        callback = self.executeTask, task = taskNew )
        taskNew.setEventReg( event=EventReg )

        # Save the task on the list and notify all connected users
        self.tasks.append(taskNew)
        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-waiting', ( "update", self.getWaiting(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        self.info( "Task re-scheduled with id %s" % taskNew.getId() )

        # Remove the task on the list
        self.removeTask( task=task )

    def getNextTime(self, schedType, shedAt, schedArgs, schedFrom=(0,0,0,0,0,0), schedTo=(0,0,0,0,0,0) ):
        """
        Compute the next timestamp

        @param schedType:
        @type schedType:

        @param shedAt:
        @type shedAt:

        @return:
        @rtype:
        """
        self.trace( 'Computing the next run time')
        y, m, d, h, mn, s = schedArgs
        if schedType == Scheduler.SCHED_DAILY:
            shedAt = shedAt + 60*60*24
        if schedType == Scheduler.SCHED_HOURLY:
            shedAt = shedAt + 60*60     
        if schedType == Scheduler.SCHED_EVERY_MIN:
            shedAt = shedAt + 60
        # BEGIN new schedulation type in 3.1.0
        if schedType == SCHED_EVERY_X:
            shedAt = shedAt + 60*60*h + 60*mn + s
        # END
        # BEGIN new schedulation type in 3.2.0
        if schedType == SCHED_WEEKLY:
            shedAt = shedAt + 7*24*60*60
        # END
        return shedAt
    
    def getTimeToTuple(self, timestamp):
        """
        Convert a timestamp to tuple

        @param timestamp:
        @type timestamp:

        @return: time as tuple ( year, month, day, hour, minute, second )
        @rtype: tuple of int
        """
        dt = datetime.datetime.fromtimestamp( timestamp )
        return ( dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second )

    def removeTask(self, task):
        """
        Remove the task from the context

        @param task:
        @type task:
        """
        self.trace( 'removing task %s' % task.getId() )
        try:
            self.tasks.remove(task)
        except Exception as e:
            self.error( 'Task [Id=%s] no more exists in the list: %s' % (task.getId(),str(e)) )
    
    def updateTask(self, taskId, schedType, shedAt, schedNb,  schedEnabled=True, withoutProbes=False, debugActivated=False, noKeepTr=False,
                                withoutNotif=False, schedFrom=(0,0,0,0,0,0), schedTo=(0,0,0,0,0,0) ):
        """
        Update a specific task, change the start time

        @param taskId:
        @type taskId:

        @param schedType:
        @type schedType:

        @param shedAt:
        @type shedAt:
        """
        self.trace( "update task %s" % taskId )
        success = None
        task = self.getTask( taskId = taskId )
        if task is None:
            self.error( 'task %s not found' % taskId )
        else:
            # Initialize the task with the start time 
            timesec = task.initialize( runAt=shedAt, runType=schedType, runNb=schedNb, runEnabled=schedEnabled, withoutProbes=withoutProbes,
                                        debugActivated=debugActivated, noKeepTr=noKeepTr, withoutNotif=withoutNotif, runFrom=schedFrom, runTo=schedTo)

            if task.isRecursive():
                timeref = time.time()
                while timesec < timeref:
                    self.trace( "catches up the late" )
                    timesec = self.getNextTime( schedType=task.schedType, shedAt=task.schedAt, schedArgs=task.schedArgs,
                                                schedFrom=schedFrom, schedTo=schedTo)
                    task.schedAt = timesec

            if task.state == STATE_DISABLED:
                task.setState( state=STATE_UPDATING )
                EventReg = self.registerEvent(  id=task.getId(), author=task.userName, name=task.getTaskName(), 
                                        weekly=None, daily=None, hourly=None, everyMin=None, everySec=None, at=None, delay=None, timesec=task.schedAt,
                                        callback = self.executeTask, task = task )
                task.setState( state=STATE_WAITING )
                task.setEventReg( event=EventReg )
                self.info( 'Task %s enabled' % str(taskId) ) 
                success = taskId

                # Backup the task on the disk
                self.trace( "Backup the test" )
                taskBackuped = self.backupTask(task=task)
                if not taskBackuped :
                    self.error( 'Unable to backup the task in the system' )
            
            elif task.state == STATE_WAITING:
                task.setState( state=STATE_UPDATING )
                if not schedEnabled:
                    taskDisabled = TaskMngr.unregisterEvent( event = task.eventReg)
                    if not taskDisabled:
                        self.error( 'unable to unregister the following task %s' % task.getId() )
                        task.setState( state=STATE_ERROR )
                    else:
                        success = taskId
                        task.setState( state=STATE_DISABLED )
                        self.info( 'Task %s disabled' % str(taskId) ) 
                else:
                    # Update event in the scheduler
                    taskRescheduled = TaskMngr.updateEvent( event = task.eventReg, weekly=None, daily=None, hourly=None, everyMin=None, everySec=None,
                                                            at=None, delay=None, timesec=timesec )
                    if not taskRescheduled:
                        self.error( 'unable to update the following task %s' % task.getId() )
                        task.setState( state=STATE_ERROR )
                    else:
                        success = taskId
                        task.setState( state=STATE_WAITING )
                        self.info( 'Task %s updated' % str(taskId) ) 
            
                # Backup the task on the disk
                self.trace( "Backup the test" )
                taskBackuped = self.backupTask(task=task)
                if not taskBackuped :
                    self.error( 'Unable to backup the task in the system' )

            else:
                self.error( 'invalid state during the update of the task [current state=%s]' % task.state )
                
        # notify all connected users
        connected = Context.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ( 'task-waiting', ( "update", self.getWaiting(user=cur_user)) )   
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success

    def resetHistoryInDb(self):
        """
        """
        # init some shortcut
        escape = MySQLdb.escape_string
        
        sql = "DELETE FROM `%s`;" % self.TN_HISTORY
        dbRet, _ = DbManager.instance().querySQL( query = sql )
        if not dbRet: 
            self.error("unable to reset history tasks table")
            return (Context.CODE_ERROR, "unable to reset history tasks table")
            
        return (Context.CODE_OK, "" )
###############################
def getObjectTask (testData, testName, testPath, testUser, testId, testBackground, projectId=0):
    """
    """
    task = Task(testData, testName, testPath, testUser, testId, testBackground, testProjectId=projectId)
    return task

###############################
TaskMngr = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return TaskMngr

def initialize ():
    """
    Instance creation
    """
    global TaskMngr
    TaskMngr = TaskManager()
    TaskMngr.start()

def finalize ():
    """
    Destruction of the singleton
    """
    global TaskMngr
    if TaskMngr:
        TaskMngr.stop()
        TaskMngr.join()
        TaskMngr = None