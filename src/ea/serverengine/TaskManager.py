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

import time
import datetime
import pickle
import subprocess
import threading
import os
import parser
try:
    import ConfigParser
except ImportError:  # python3 support
    import configparser as ConfigParser
import uuid
import sys
import zlib
import signal
import base64
import shutil
import copy
import hashlib
import json
import platform
import traceback
try:
    import cStringIO
except ImportError:  # support python 3
    import io as cStringIO
try:
    xrange
except NameError:  # support python3
    xrange = range

from ea.serverengine import DbManager
from ea.serverengine import StorageDataAdapters
from ea.serverengine import UsersManager
from ea.serverengine import ProjectsManager
from ea.serverengine import AgentsManager
from ea.libs import Scheduler, Settings, Logger
from ea.libs.FileModels import TestResult as TestResult
from ea.serverinterfaces import EventServerInterface as ESI
from ea.serverinterfaces import TestServerInterface as TSI
from ea.serverrepositories import (RepoArchives,
                                   RepoManager)
from ea.testcreatorlib import (TestModel, TestModelDesign,
                               TestModelCommon, TestModelSub)

TASKS_RUNNING = 0
TASKS_WAITING = 1
TASKS_HISTORY = 2

STATE_INIT = 'INIT'
STATE_WAITING = 'WAITING'
STATE_DISABLED = 'DISABLED'
STATE_RUNNING = 'RUNNING'
STATE_COMPLETE = 'COMPLETE'
STATE_ERROR = 'ERROR'
STATE_FINISHED = 'FINISHED'

STATE_KILLING = 'KILLING'
STATE_KILLED = 'KILLED'

STATE_CANCELLING = 'CANCELLING'
STATE_CANCELLED = 'CANCELLED'

STATE_UPDATING = 'UPDATING'


SIGNAL_KILL = 9

SCHED_TYPE_UNDEFINED = -1
SCHED_EVERY_X = 7
SCHED_WEEKLY = 8
SCHED_NOW_MORE = 9
SCHED_QUEUE = 10
SCHED_QUEUE_AT = 11

SCHEDULE_TYPES = {
    "daily": 6,
    "hourly": 5,
    "weekly": 8,
    "every": 7,
    "at": 1,
    "in": 2,
    "now": 0
}

MONDAY = 0
TUESDAY = 1
WEDNESDAY = 2
THURSDAY = 3
FRIDAY = 4
SATURDAY = 5
SUNDAY = 6


EMPTY_VALUE = ''

GenBaseId = 0
GenBaseIdMutex = threading.RLock()


def getGroupId():
    """
    Generates a new unique ID.
    """
    global GenBaseId
    GenBaseIdMutex.acquire()
    GenBaseId += 1
    ret = GenBaseId
    GenBaseIdMutex.release()
    return ret


def getBackTrace():
    """
    Returns the current backtrace.
    """
    backtrace = cStringIO.StringIO()
    traceback.print_exc(None, backtrace)
    ret = backtrace.getvalue()
    backtrace.close()
    return ret


class Task(Logger.ClassLogger):
    def __init__(self, testData, testName, testPath, testUser, testId,
                 testBackground, taskEnabled=True, withoutProbes=False,
                 debugActivated=False, withoutNotif=False, noKeepTr=False,
                 testUserId=0, testProjectId=0, stepByStep=False,
                 breakpoint=False, runSimultaneous=False, channelId=False,
                 context=None):
        """
        Construc test class
        """
        self.ctx = context

        self.mutex = threading.RLock()

        self.channelId = channelId
        self.schedId = None
        self.testName = testName
        self.testPath = testPath

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
        if self.dataTest['test-extension'] == 'tgx':
            self.testType = 'TestGlobal'
        if self.dataTest['test-extension'] == 'tpx':
            self.testType = 'TestPlan'
        if self.dataTest['test-extension'] == 'tux':
            self.testType = 'TestUnit'

        self.replayId = 0
        self.recurId = 0

        self.schedAt = 0
        self.schedType = SCHED_TYPE_UNDEFINED
        self.schedArgs = (0, 0, 0, 0, 0, 0)  # Y,M,D,H,M,S
        self.schedFrom = (0, 0, 0, 0, 0, 0)  # Y,M,D,H,M,S
        self.schedTo = (0, 0, 0, 0, 0, 0)  # Y,M,D,H,M,S
        self.schedNb = -1

        self.resultsStats = {"passed": 0, "failed": 0, "undefined": 0}

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

        test = {"name": self.testName, "start-at": self.startTime}
        statistics = {"total": "%s" % maxRun, 'count': "%s" % (self.recurId + 1),
                      'passed': "%s" % self.resultsStats["passed"],
                      'failed': "%s" % self.resultsStats["failed"],
                      'undefined': "%s" % self.resultsStats["undefined"]}
        testDescr = {
            "test": test,
            "user": self.userName,
            "statistics": statistics}
        f = open("%s/DESCRIPTION" % self.getPath(envTmp=envTmp), 'w')
        f.write("%s" % json.dumps(testDescr))
        f.close()

    def setGroupId(self, groupId):
        """
        Set the id of tasks group in queue
        """
        self.groupId = groupId

    def setSyntaxOK(self):
        """
        set syntax as ok
        """
        self.trace("Syntax OK")
        self.syntaxOK = True
        return self.syntaxOK

    def runAgain(self):
        """
        Check the counter of run
        """
        if self.schedNb == -1:
            return True
        elif self.recurId < (self.schedNb - 1):
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
                now_dt = datetime.datetime(cur_dt.tm_year,
                                           cur_dt.tm_mon,
                                           cur_dt.tm_mday,
                                           cur_dt.tm_hour,
                                           cur_dt.tm_min,
                                           0,
                                           0)

                toY, toM, toD, toH, toMn, _ = self.schedTo
                to_dt = datetime.datetime(toY,
                                          toM,
                                          toD,
                                          toH,
                                          toMn,
                                          0,
                                          0)

                if now_dt >= to_dt:
                    _, _, _, h, mn, s = self.schedArgs
                    fromY, fromM, fromD, fromH, fromMn, _ = self.schedFrom

                    # drift the interval on one day
                    from_dt = datetime.datetime(fromY, fromM, fromD, fromH, fromMn, 0, 0) + \
                        datetime.timedelta(hours=24, minutes=0, seconds=0)
                    to_dt = to_dt + \
                        datetime.timedelta(hours=24, minutes=0, seconds=0)

                    next_dt = from_dt
                    self.schedAt = time.mktime(
                        next_dt.timetuple()) - 60 * 60 * h - 60 * mn - s
                    self.schedFrom = (from_dt.year, from_dt.month,
                                      from_dt.day, from_dt.hour,
                                      from_dt.minute, 0)
                    self.schedTo = (to_dt.year, to_dt.month,
                                    to_dt.day, to_dt.hour,
                                    to_dt.minute, 0)

                    self.trace('Next from: %s' % str(self.schedFrom))
                    self.trace('Next to: %s' % str(self.schedTo))
                    return False
                else:
                    return True
        else:
            return True

    def setEventReg(self, event):
        """
        Save the event created by the scheduler
        """
        self.eventReg = event

    def toTuple(self, withId=False, withGroupId=False):
        """
        Return the task as tuple
        """
        if withId:
            if withGroupId:
                return (self.schedId, self.schedType, str(self.schedArgs), str(self.schedAt),
                        self.getTaskName(), str(self.userName),
                        str(self.startTime), str(self.duration), str(
                            self.state), self.schedNb,
                        self.recurId, self.enabled, self.withoutProbes,
                        self.withoutNotif, self.noKeepTr, self.userId, self.projectId,
                        str(self.schedFrom), str(self.schedTo), self.groupId)
            else:
                # Called to add in backup
                return (self.schedId, self.schedType, str(self.schedArgs), str(self.schedAt),
                        self.getTaskName(), str(self.userName),
                        str(self.startTime), str(self.duration), str(
                            self.state), self.schedNb,
                        self.recurId, self.enabled, self.withoutProbes,
                        self.withoutNotif, self.noKeepTr, self.userId, self.projectId,
                        str(self.schedFrom), str(self.schedTo))
        else:
            # Called to add in the history
            return (self.schedType, str(self.schedArgs), str(self.schedAt), self.getTaskName(),
                    str(self.userName), str(
                        self.startTime), str(self.duration),
                    str(self.state), self.projectId)

    def getId(self):
        """
        Get the scheduler event id
        """
        return self.schedId

    def setId(self, taskId):
        """
        Set the scheduler event id
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
            ret = self.testPath
        else:
            ret = self.testName
        return ret

    def setReplayId(self):
        """
        Set the replay id
        """
        self.removeFinishedFile()
        self.replayId += 1

    def initialize(self, runAt, runType, runNb, runEnabled, withoutProbes,
                   debugActivated, withoutNotif, noKeepTr,
                   runFrom=(0, 0, 0, 0, 0, 0),
                   runTo=(0, 0, 0, 0, 0, 0)):
        """
        Initialize the task start time
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
        self.schedArgs = (0, 0, 0, 0, 0, 0)
        self.schedFrom = runFrom
        self.schedTo = runTo

        if runType == Scheduler.SCHED_DAILY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon,
                                        cur_dt.tm_mday, h, mn, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (0, 0, 0, h, mn, s)

        elif runType == Scheduler.SCHED_HOURLY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday,
                                        cur_dt.tm_hour, mn, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (0, 0, 0, 0, mn, s)

        elif runType == Scheduler.SCHED_EVERY_MIN:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday,
                                        cur_dt.tm_hour, cur_dt.tm_min, s, 0)
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (0, 0, 0, 0, 0, s)

        elif runType == Scheduler.SCHED_EVERY_SEC:
            self.error('not implemented')

        elif runType == Scheduler.SCHED_AT:
            dt = datetime.datetime(y, m, d, h, mn, s, 0)
            timestamp = time.mktime(dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (y, m, d, h, mn, s)

        elif runType == Scheduler.SCHED_IN:
            timestamp = time.time() + s
            self.schedAt = timestamp
            self.schedArgs = (0, 0, 0, 0, 0, s)

        elif runType == Scheduler.SCHED_NOW:
            self.trace('init start time: nothing todo')

        elif runType == SCHED_QUEUE:
            self.trace('init start time in queue: nothing todo')

        elif runType == SCHED_QUEUE_AT:
            dt = datetime.datetime(y, m, d, h, mn, s, 0)
            timestamp = time.mktime(dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (y, m, d, h, mn, s)

        # BEGIN new schedulation type in 5.0.0
        elif runType == SCHED_NOW_MORE:
            if sum(runFrom):
                dt = datetime.datetime(
                    fromY, fromM, fromD, fromH, fromMn, fromS, 0)
                timestamp = time.mktime(dt.timetuple())
                self.schedAt = timestamp
            else:
                pass
        # END

        # BEGIN new schedulation type in 3.1.0
        elif runType == SCHED_EVERY_X:
            cur_dt = time.localtime()

            from_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon,
                                        cur_dt.tm_mday, fromH, fromMn, 0, 0)
            if fromH > toH:  # fix in v12, sched from 23:00 to 07:00 not working
                to_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon,
                                          cur_dt.tm_mday + 1, toH, toMn, 0, 0)
            else:
                to_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon,
                                          cur_dt.tm_mday, toH, toMn, 0, 0)

            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon, cur_dt.tm_mday,
                                        cur_dt.tm_hour, cur_dt.tm_min, cur_dt.tm_sec, 0)
            self.trace("Current next time: %s" % next_dt.isoformat())

            if from_dt == to_dt:
                if not Settings.getInt(
                        'TaskManager', 'everyminx-run-immediately'):
                    next_dt += datetime.timedelta(hours=h,
                                                  minutes=mn, seconds=s)
                self.trace(
                    "No interval, new next time: %s" %
                    next_dt.isoformat())
            else:
                self.trace("Ajust next time according to the interval")
                # start greather than current date ?
                if from_dt > next_dt:
                    next_dt = from_dt
                # shit the interval of one day
                else:
                    from_dt += datetime.timedelta(hours=24,
                                                  minutes=0, seconds=0)
                    to_dt += datetime.timedelta(hours=24, minutes=0, seconds=0)
                    next_dt = from_dt

            self.trace("Final next time at: %s" % next_dt.isoformat())
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (0, 0, 0, h, mn, s)
            self.schedFrom = (from_dt.year, from_dt.month,
                              from_dt.day, from_dt.hour,
                              from_dt.minute, 0)
            self.schedTo = (to_dt.year, to_dt.month,
                            to_dt.day, to_dt.hour,
                            to_dt.minute, 0)

            self.trace("Interval begin at: %s" % str(self.schedFrom))
            self.trace("Interval ending at: %s" % str(self.schedTo))

        elif runType == SCHED_WEEKLY:
            cur_dt = time.localtime()
            next_dt = datetime.datetime(cur_dt.tm_year, cur_dt.tm_mon,
                                        cur_dt.tm_mday, h, mn, s, 0)
            delta = datetime.timedelta(days=1)
            while next_dt.weekday() != d:
                next_dt = next_dt + delta
            timestamp = time.mktime(next_dt.timetuple())
            self.schedAt = timestamp
            self.schedArgs = (0, 0, d, h, mn, s)

        else:
            self.error('[Run Type=%s] not supported' % str(runType))
        return timestamp

    def isSuccessive(self):
        """
        Returns True if the task is successive, False otherwise
        """
        if self.schedType == SCHED_NOW_MORE:
            return True
        else:
            return False

    def isRecursive(self):
        """
        Returns True if the task is recursive, False otherwise
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
        """
        if self.schedType == Scheduler.SCHED_AT or self.schedType == Scheduler.SCHED_IN:
            return True
        else:
            return False

    def completeId(self, withTestPath=False):
        """
        Returns complete identifier
        Concatenation of variables: self.initTime,
        base64(self.testName) and self.userName
        With the following separator: .
        Example: 123622.770.dG1wMw==.admin
        """
        sep = "."

        testidentifier = self.testName
        if withTestPath:
            if self.testPath != "":
                testidentifier = self.testPath  # remove in v16

        # prepare a unique id for the test
        ret = []
        ret.append(
            time.strftime(
                "%Y-%m-%d_%H-%M-%S",
                time.localtime(
                    self.prepareTime)))
        ret.append(self.taskUuid)
        if sys.version_info > (3,):
            encoded = base64.b64encode(testidentifier.encode("utf8"))
            ret.append(encoded.decode("utf8"))
        else:
            ret.append(base64.b64encode(testidentifier.encode("utf8")))
        ret.append(self.userName)

        # join with . separator and return it
        return sep.join(ret)

    def toDict(self):
        """
        To dict data type
        """
        ret = {}
        ret['id'] = self.schedId
        if self.testPath != "":
            ret['name'] = self.testPath
        else:
            ret['name'] = self.testName
        ret['name'] = os.path.normpath(ret['name'])
        ret['user'] = self.userName
        ret['state'] = self.state
        ret['sched-id'] = self.schedType
        ret['sched-args'] = self.schedArgs
        ret['sched-nb'] = self.schedNb
        ret['sched-at'] = self.schedAt
        ret['start-at'] = self.startTime
        ret['stop-at'] = self.stopTime
        ret['duration'] = self.duration
        ret['recursive'] = self.isRecursive()
        ret['project-id'] = self.projectId
        ret['test-id'] = self.getTestID()
        ret['replay-id'] = self.replayId
        return ret

    def removeFinishedFile(self, envTmp=False):
        """
        Remove FINISHED file
        """
        self.trace('removing finished file')
        try:
            fp = "%s/%s" % (self.getPath(envTmp=envTmp), STATE_FINISHED)
            res = os.path.exists(os.path.normpath(fp))
            if res:
                os.remove(os.path.normpath(fp))
        except OSError as e:
            self.trace('Unable to remove finished file: %s' % str(e))
        except Exception as e:
            self.error('Unable to remove finished file: %s' % str(e))

    def setFINISHED(self, envTmp=False):
        """
        Called when the task is finished
        """
        if self.state != STATE_CANCELLED:
            self.trace('adding finished file')
            try:
                f = open(
                    "%s/%s" %
                    (self.getPath(
                        envTmp=envTmp),
                        STATE_FINISHED),
                    'w')
                f.close()
            except Exception as e:
                self.error(e)

        # Add the task on the history db and notify all connected users
        if Settings.getInt('Database', 'insert-test-history'):
            ret, lastinsertid = TaskMngr.addToHistory(task=self)
            toSend = list(self.toTuple())
            if ret is None:
                toSend.insert(0, 999999)  # error
            else:
                toSend.insert(0, lastinsertid)  # insert ok

            # new in v10, return only history task according to the user
            connected = self.ctx.instance().getUsersConnectedCopy()
            for cur_user in connected:
                prjs = ProjectsManager.instance().getProjects(user=cur_user)
                prjsDict = {}
                for prj in prjs:
                    prjsDict[prj['project_id']] = True
                if self.projectId in prjsDict:
                    data = ('task-history', ("add", [toSend]))
                    ESI.instance().notify(body=data, toUser=cur_user)
            del connected
            # end of new in v10

        if self.prepared:
            TaskMngr.onTaskFinished(self)

    def setState(self, state, envTmp=False):
        """
        Set the state: INIT, WAITING, RUNNING, COMPLETE, ERROR, KILLED, CANCELLED
        """
        self.mutex.acquire()
        self.state = state

        if state not in [STATE_INIT, STATE_WAITING]:
            try:
                f = open("%s/STATE" % self.getPath(envTmp=envTmp), 'w')
                f.write(state)
                f.close()
            except Exception as e:
                self.error("unable to write state file %s" % e)

        if self.schedId is not None:
            self.trace('task %s state: %s' % (self.schedId, state))
        else:
            self.trace('task state: %s' % state)

        # disable the task according to the state
        if state == STATE_DISABLED:
            self.enabled = False
        else:
            self.enabled = True

        if state == STATE_RUNNING:
            self.startTime = time.time()

            # save json test for rest api
            self.saveTestDescr()

            # Notify all connected users to remove event from the waiting list
            # on the client interface
            connected = self.ctx.instance().getUsersConnectedCopy()
            for cur_user in connected:
                self.trace("updating task waiting: %s" % cur_user)
                data = (
                    'task-waiting',
                    ("update",
                     TaskMngr.getWaiting(
                         user=cur_user)))
                ESI.instance().notify(body=data, toUser=cur_user)
            del connected

            # Notify all connected users to add event to running list on the client interface
            # new in v10
            connected = self.ctx.instance().getUsersConnectedCopy()
            for cur_user in connected:
                self.trace("updating task running: %s" % cur_user)
                data = (
                    'task-running',
                    ("update",
                     TaskMngr.getRunning(
                         user=cur_user)))
                ESI.instance().notify(body=data, toUser=cur_user)
            del connected
            # end of new in v10

        elif state in [STATE_CANCELLED, STATE_COMPLETE, STATE_ERROR, STATE_KILLED]:
            if self.startTime != "N/A":
                self.stopTime = time.time()
                self.duration = self.stopTime - self.startTime
                # notify all connected users to remove event to running list
                connected = self.ctx.instance().getUsersConnectedCopy()
                for cur_user in connected:
                    data = (
                        'task-running',
                        ("update",
                         TaskMngr.getRunning(
                             user=cur_user)))
                    ESI.instance().notify(body=data, toUser=cur_user)
                del connected
            self.setFINISHED(envTmp=envTmp)
        self.mutex.release()

    def cancelTest(self, removeFromContext=True):
        """
        Cancel the test
        """
        self.removeFromContext = removeFromContext
        if self.state == STATE_DISABLED:
            self.setState(state=STATE_CANCELLING)
            self.setState(state=STATE_CANCELLED)
            ret = True
        else:
            self.setState(state=STATE_CANCELLING)
            ret = TaskMngr.unregisterEvent(event=self.eventReg)
            if ret:
                self.setState(state=STATE_CANCELLED)
            else:
                self.setState(state=STATE_ERROR)
        return ret

    def getTestsPath(self):
        """
        Get the path of all tests
        """
        testsResultPath = '%s%s' % (Settings.getDirExec(),
                                    Settings.get('Paths', 'testsresults'))
        return os.path.normpath(testsResultPath)

    def generateTestID(self):
        """
        deprecated
        """
        ret = ''
        try:
            self.trace(self.getTestPath(withDate=True))
            hash = hashlib.md5()
            hash.update(self.getTestPath(withDate=True))
            ret = hash.hexdigest()
        except Exception as e:
            self.error("Unable to make hash for test id: %s" % str(e))
        return ret

    def getTestID(self):
        """
        """
        return self.taskUuid

    def getTestPath(self, withDate=True):
        """
        Get the path of the test
        """
        if withDate:
            return os.path.normpath("/%s/%s/%s" % (self.projectId,
                                                   time.strftime(
                                                       "%Y-%m-%d", time.localtime(self.prepareTime)),
                                                   self.completeId()))
        else:
            return self.completeId()

    def getPath(self, envTmp=False, fullPath=True, noDate=False):
        """
        Returns the complete path of the test
        """
        testsResultPath = '%s%s' % (Settings.getDirExec(),
                                    Settings.get('Paths', 'testsresults'))
        if envTmp:
            testsResultPath = '%s%s' % (Settings.getDirExec(),
                                        Settings.get('Paths', 'testsresults-tmp'))
        if fullPath:
            if noDate:
                return os.path.normpath(
                    "%s/%s" % (testsResultPath, self.completeId()))
            else:
                return os.path.normpath("%s/%s/%s/%s" % (testsResultPath,
                                                         self.projectId,
                                                         time.strftime(
                                                             "%Y-%m-%d", time.localtime(self.prepareTime)),
                                                         self.completeId()))
        else:
            if noDate:
                return "%s" % (self.completeId())
            else:
                return os.path.normpath("%s/%s/%s" % (self.projectId,
                                                      time.strftime(
                                                          "%Y-%m-%d", time.localtime(self.prepareTime)),
                                                      self.completeId()))

    def getDirToday(self, envTmp=False, fullPath=True):
        """
        Get the path of today directory
        """
        testResultPath = '%s%s' % (Settings.getDirExec(),
                                   Settings.get('Paths', 'testsresults'))
        if envTmp:
            testResultPath = '%s%s' % (Settings.getDirExec(),
                                       Settings.get('Paths', 'testsresults-tmp'))
        if fullPath:
            return os.path.normpath("%s/%s/%s" % (testResultPath,
                                                  self.projectId,
                                                  time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)))
                                    )
        else:
            return os.path.normpath("%s/%s" % (self.projectId,
                                               time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)))
                                    )

    def getDirProject(self, envTmp=False, fullPath=True):
        """
        Get the path of project directory
        """
        testResultPath = '%s%s' % (Settings.getDirExec(),
                                   Settings.get('Paths', 'testsresults'))
        if envTmp:
            testResultPath = '%s%s' % (Settings.getDirExec(),
                                       Settings.get('Paths', 'testsresults-tmp'))
        if fullPath:
            return os.path.normpath("%s/%s" % (testResultPath, self.projectId))
        else:
            return self.projectId

    def wrongParseToFile(self, te, subTest=False):
        """
        Called when the file to parse is invalid
        This file is saved on the tmp storage
        """
        try:
            tmpPath = '%s%s/Parsed' % (Settings.getDirExec(),
                                       Settings.get('Paths', 'tmp'))
            tmpPath = os.path.normpath(tmpPath)
            os.mkdir(tmpPath, 0o755)
        except Exception:
            pass
        # write wrong test
        fileName = '%s%s/Parsed/%s_%s_%s.BAD' % (Settings.getDirExec(),
                                                 Settings.get('Paths', 'tmp'),
                                                 self.testName,
                                                 self.userName,
                                                 self.getTestID())
        if subTest:
            fileName = '%s%s/Parsed/SubTE_%s_%s_%s.BAD' % (Settings.getDirExec(),
                                                           Settings.get(
                                                               'Paths', 'tmp'),
                                                           self.testName,
                                                           self.userName,
                                                           self.getTestID())

        fileName = os.path.normpath(fileName)

        f = open(fileName, 'wb')

        if sys.version_info > (3,):  # python3 support
            te = te.encode("utf8")

        f.write(te)
        f.close()

    def parseTestDesign(self):
        """
        """
        self.prepareTime = time.time()
        ret = {}
        ret["error"] = False
        ret["error-details"] = ""
        ret['design'] = ''
        ret['design-xml'] = ''
        envTmp = True
        cleanupTmp = True
        try:
            # Prepare the destination storage result
            self.trace(
                "Parse test design: preparing the destination storage result")
            try:
                # create project folder
                try:
                    prjFolder = self.getDirProject(envTmp=envTmp)
                    if not os.path.exists(prjFolder):
                        os.mkdir(prjFolder, 0o755)
                except Exception as e:
                    self.trace(
                        "folder %s already exist: %s" %
                        (prjFolder, str(e)))
                else:

                    # create date folder
                    try:
                        mainDir = self.getDirToday(envTmp=envTmp)
                        if not os.path.exists(mainDir):
                            os.mkdir(mainDir, 0o755)
                    except Exception as e:
                        self.trace(
                            "dir %s already exist: %s" %
                            (mainDir, str(e)))
                    else:
                        os.mkdir(
                            self.getPath(
                                envTmp=envTmp,
                                noDate=False),
                            0o755)
            except OSError as e:
                cleanupTmp = False
                self.error(
                    'Parse test design: unable to prepare the directory, system error: %s' %
                    str(e))
                ret["error"] = True
                ret["error-details"] = "Server"
            else:

                # Creation te
                self.trace(
                    "Parse test design: creating the test executable for test design check")
                try:
                    te = TestModelDesign.createTestDesign(
                        dataTest=self.dataTest,
                        userName=self.userName,
                        testName=self.testName,
                        trPath=self.getTestPath(withDate=True),
                        logFilename=self.completeId(),
                        userId=self.userId,
                        projectId=self.projectId,
                        testId=self.testId,
                        runningAgents=AgentsManager.instance().getRunning(),
                        testLocation=self.getTestLocation(),
                        parametersShared=self.ctx.instance().getTestEnvironment(user=self.userName,
                                                                                ),
                        var_path=Settings.get('Paths', 'testsresults-tmp')
                    )
                except Exception as e:
                    cleanupTmp = False
                    self.error(
                        'Parse test design: unable to create te: %s' %
                        str(e))
                    ret["error"] = True
                    ret["error-details"] = "Server"
                else:

                    # Saving
                    self.trace(
                        "Parse test design: saving the test executable on the disk")
                    try:
                        # write test
                        f = open("%s/%s" % (self.getPath(envTmp=envTmp, noDate=False),
                                            self.completeId()), 'wb')
                        f.write(te)
                        f.close()

                        # write log
                        f = open("%s/test.log" % self.getPath(envTmp=envTmp,
                                                              noDate=False), 'w')
                        f.close()

                        # write tests settings
                        shutil.copy('%s/test.ini' % Settings.getDirExec(),
                                    "%s/test.ini" % self.getPath(envTmp=envTmp,
                                                                 noDate=False))

                        # tunning settings
                        cfgtest_path = "%s/test.ini" % self.getPath(envTmp=envTmp,
                                                                    noDate=False)
                        cfgparser = ConfigParser.RawConfigParser()
                        cfgparser.read(cfgtest_path)
                        cfgparser.set('Paths', 'templates', "%s/%s/" % (Settings.getDirExec(),
                                                                        Settings.get('Paths', 'templates')))

                        cfgtest = open(cfgtest_path, 'w')
                        cfgparser.write(cfgtest)
                        cfgtest.close()
                    except OSError as e:
                        cleanupTmp = False
                        self.error(
                            'Parse test design: unable to save te, system error: %s' %
                            str(e))
                        ret["error"] = True
                        ret["error-details"] = "Server"
                    except Exception as e:
                        cleanupTmp = False
                        self.error(
                            'Parse test design: unable to save te: %s' %
                            str(e))
                        ret["error"] = True
                        ret["error-details"] = "Server"
                    else:

                        # Compilation
                        self.trace(
                            "Parse test design: compile the test executable")
                        try:
                            if sys.version_info > (3,):
                                te = te.decode("utf8")
                            parser.suite(te).compile()
                        except SyntaxError as e:
                            cleanupTmp = False
                            self.trace(
                                'Parse test design: unable to compile syntax te: %s' % e)
                            ret["error"] = True
                            ret["error-details"] = "Syntax"
                        except Exception:
                            cleanupTmp = False
                            self.error(
                                'Parse test design: unable to compile te: %s' %
                                getBackTrace())
                            ret["error"] = True
                            ret["error-details"] = "Server"
                        else:
                            self.trace("Parse test design: fork and executing")
                            # Execute
                            if platform.system() == "Windows":
                                executable = Settings.get('Bin', 'python-win')
                            else:
                                executable = Settings.get('Bin', 'python')
                            cmdOptions = [str(self.schedId), str(
                                self.testId), str(self.replayId)]

                            # Construct the final execution line
                            args = [executable]
                            exec_path = "%s/%s" % (self.getPath(envTmp=envTmp, noDate=False),
                                                   self.completeId())
                            args.append(os.path.normpath(exec_path))
                            args = args + cmdOptions

                            # create sh file
                            if platform.system() == "Windows":
                                launch_cmd = "launch.bat"
                            else:
                                launch_cmd = "launch.sh"
                            launch_path = "%s/%s" % (self.getPath(envTmp=envTmp, noDate=False),
                                                     launch_cmd)

                            f = open(os.path.normpath(launch_path), 'w')
                            f.write(" ".join(args))
                            f.close()

                            # Fork and run it
                            try:
                                p = subprocess.Popen(args)
                                self.tpid = p.pid
                                TaskMngr.addChildPid(pid=p.pid)
                            except Exception:
                                self.error('unable to fork te')
                                ret["error"] = True
                                ret["error-details"] = "Fork"
                            else:
                                p.wait()
                                retcode = p.returncode

                                if retcode == 0:
                                    self.trace("Parse test design: fork ok")
                                    # read result
                                    ret['design'] = self.getTestDesign(
                                        returnXml=False, envTmp=True)
                                    ret['design-xml'] = self.getTestDesign(
                                        returnXml=True, envTmp=True)
                                else:
                                    cleanupTmp = False
                                    self.error(
                                        'unknown return code received: %s' %
                                        str(retcode))
                                    ret["error"] = True
                                    ret["error-details"] = "Return"

        except Exception as e:
            self.error("unable to parse test design: %s" % str(e))
            ret["error"] = True
            ret["error-details"] = "Global"

        # Remove the test from temp storage
        if cleanupTmp:
            try:
                if os.path.exists(self.getPath(envTmp=envTmp, noDate=False)):
                    shutil.rmtree(self.getPath(envTmp=envTmp, noDate=False))
            except Exception as e:
                self.error(
                    "Parse test design: unable to delete the tmp test: %s" %
                    str(e))

        return ret

    def parseTest(self):
        """
        Parse the test
        Return False if the syntax is wrong
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

            if self.dataTest["test-extension"] == "tux":
                isTu = True
            if self.dataTest["test-extension"] == "tsx":
                isTs = True
            if self.dataTest["test-extension"] == "tpx":
                isTp = True
            if self.dataTest["test-extension"] == "tgx":
                isTg = True

            if isTu or isTs or isTa:
                sub_descr = self.dataTest['test-properties']['descriptions']['description']
                subte = TestModelSub.createSubTest(dataTest=self.dataTest,
                                                   trPath=self.getTestPath(),
                                                   descriptions=sub_descr,
                                                   isTestUnit=isTu
                                                   )
                sub_tes.append((isTu, isTa, self.testName, subte, ''))

            if isTp or isTg:
                insideTp = ''
                for ts in self.dataTest['test-execution']:
                    isSubTu = False
                    isSubTa = False
                    if 'extension' in ts:
                        if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                            isSubTu = True
                        if ts['extension'] == RepoManager.TEST_PLAN_EXT and ts['separator'] == 'started':
                            while ts['testpath'][:1] == '/':
                                ts['testpath'] = ts['testpath'][1:]
                            insideTp = '%s:/%s/%s.%s' % (
                                ts['testproject'],
                                ts['testpath'],
                                ts['testname'],
                                ts['extension'],
                            )

                        if ts['extension'] == RepoManager.TEST_PLAN_EXT and ts['separator'] == 'terminated':
                            insideTp = ''
                    if ts['enable'] == TestModelCommon.TS_ENABLED:
                        sub_descr = self.dataTest['test-properties']['descriptions']['description']
                        subte = TestModelSub.createSubTest(dataTest=ts,
                                                           trPath=self.getTestPath(),
                                                           descriptions=sub_descr,
                                                           isTestUnit=isSubTu,
                                                           isTestPlan=isTp,
                                                           isTestGlobal=isTg)
                        sub_tes.append(
                            (isSubTu, isSubTa, ts['file'], subte, insideTp))
        except Exception as e:
            self.error("parse test - unable to prepare sub te: %s" % str(e))
            return (False, {'msg': str(e)})
        else:
            self.trace("Parse test: creating the main te")
            startTestLine = 0
            te = ''
            try:
                te_shared = self.ctx.instance().getTestEnvironment(user=self.userName)
                te = TestModel.createTestExecutable(dataTest=self.dataTest,
                                                    userName=self.userName,
                                                    testName=self.testName,
                                                    trPath=self.getTestPath(),
                                                    logFilename=self.completeId(),
                                                    userId=self.userId,
                                                    projectId=self.projectId,
                                                    subTEs=len(sub_tes),
                                                    channelId=self.channelId,
                                                    parametersShared=te_shared,
                                                    stepByStep=self.stepByStep,
                                                    breakpoint=self.breakpoint,
                                                    testId=self.testId,
                                                    testLocation=self.getTestLocation(),
                                                    runningAgents=AgentsManager.instance().getRunning(),
                                                    taskUuid=self.taskUuid,
                                                    var_path=Settings.get(
                                                        'Paths', 'testsresults')
                                                    )
                if sys.version_info > (3,):
                    te = te.decode("utf8")
            except Exception as e:
                self.error("parse test - unable to prepare te: %s" % str(e))
                self.wrongParseToFile(te=te)
                return (False, {'msg': str(e)})
            else:
                self.trace("compile all sub test executable")
                for i in xrange(len(sub_tes)):
                    issub_tu, issub_ta, subtest_name, subtest_val, inside_tp = sub_tes[i]

                    if sys.version_info > (3,):
                        subtest_val = subtest_val.decode("utf8")

                    # find startline of the test
                    if issub_tu or issub_ta:
                        beginTe, leftTe = subtest_val.split(
                            'class TESTCASE(TestCase):')
                    else:
                        beginTe, leftTe = subtest_val.split(
                            '# !! test injection')

                    startTestLine = len(beginTe.splitlines()) + 1

                    # compile
                    try:
                        parser.suite(subtest_val).compile()
                    except SyntaxError as e:
                        self.trace("sub test (id=%s, testname=%s) syntax error: %s" % (i,
                                                                                       subtest_name,
                                                                                       str(e)))
                        line_err = (e.lineno - startTestLine) + 1
                        # set the lineno to None to remove it from exception
                        # text
                        e.lineno = None
                        self.wrongParseToFile(te=subtest_val, subTest=True)
                        return (False, {'msg': str(e),
                                        'line': line_err,
                                        'testname': subtest_name,
                                        'parent-testname': inside_tp})

                    except SystemError as e:
                        self.error(
                            "sub test server limitation raised: %s" %
                            str(e))
                        return (
                            False, {'msg': "Limitation: the test (%s) is too big!" % subtest_name})
                    except Exception as e:
                        self.error(
                            'unable to parse sub test %s' %
                            getBackTrace())
                        e.lineno = None
                        self.wrongParseToFile(te=subtest_val, subTest=True)
                        return (False, {'msg': str(e),
                                        'testname': subtest_name})

                self.trace('Parse test: compiling main te')
                try:
                    parser.suite(te).compile()
                except SyntaxError as e:
                    self.trace("syntax error: %s" % str(e))
                    self.wrongParseToFile(te=te)
                    return (False, {'msg': str(e), 'line': e.lineno})

                except SystemError as e:
                    self.error("server limitation raised: %s" % str(e))
                    return (
                        False, {'msg': "Limitation: this test is too big!"})
                except Exception as e:
                    self.error('unable to parse test %s' % getBackTrace())
                    e.lineno = None
                    self.wrongParseToFile(te=te)
                    return (False, {'msg': str(e)})

            return (True, {})

    def getTestLocation(self):
        """
        """
        return os.path.dirname(os.path.normpath(self.testPath))

    def initPrepare(self):
        """
        """
        self.prepareTime = time.time()
        self.prepared = False
        self.trace("Prepare time: %s" % self.prepareTime)
        self.trace(
            "Human prepare time: %s" %
            time.strftime(
                "%Y-%m-%d",
                time.localtime(
                    self.prepareTime)))
        return True

    def prepare(self, envTmp=False):
        """
        Prepare the test
        - Prepare storage
        - Creation
        - Saving
        - Compilation
        """
        self.initPrepare()

        # Prepare the destination storage result
        self.trace("Preparing the destination storage result")
        try:
            if envTmp:
                try:
                    tmpPath = '%s%s' % (Settings.getDirExec(),
                                        Settings.get('Paths', 'testsresults-tmp'))
                    tmpPath = os.path.normpath(tmpPath)
                    if not os.path.exists(tmpPath):
                        os.mkdir(tmpPath, 0o755)
                except Exception as e:
                    self.trace("dir %s already exist: %s" % (tmpPath, str(e)))
            # create main dir
            try:
                mainDir = self.getDirProject(envTmp=envTmp)
                if not os.path.exists(mainDir):
                    os.mkdir(mainDir, 0o755)
            except Exception as e:
                self.trace(
                    "dir project %s already exist: %s" %
                    (mainDir, str(e)))
            try:
                mainDir = self.getDirToday(envTmp=envTmp)
                if not os.path.exists(mainDir):
                    os.mkdir(mainDir, 0o755)
            except Exception as e:
                self.trace("dir date %s already exist: %s" % (mainDir, str(e)))

            # create specific folder
            os.mkdir(self.getPath(envTmp=envTmp), 0o755)

        except OSError as e:
            self.error(
                'unable to prepare the directory, system error: %s' %
                str(e))
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(e.strerror)
        except Exception as e:
            self.error('unable to prepare the directory: %s' % e)
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(getBackTrace())

        # Creation
        self.trace("Create all sub test executable")
        sub_tes = []
        try:
            dataTest = self.dataTest
            if envTmp:  # not alter data in tmp env
                dataTest = copy.deepcopy(self.dataTest)

            # detect the type of test
            isTu = False
            isTp = False
            isTg = False
            isTs = False

            if self.dataTest["test-extension"] == "tux":
                isTu = True
            if self.dataTest["test-extension"] == "tsx":
                isTs = True
            if self.dataTest["test-extension"] == "tpx":
                isTp = True
            if self.dataTest["test-extension"] == "tgx":
                isTg = True

            if isTu or isTs:
                subte_descr = dataTest['test-properties']['descriptions']['description']
                subte = TestModelSub.createSubTest(dataTest=dataTest,
                                                   trPath=self.getTestPath(),
                                                   descriptions=subte_descr,
                                                   isTestUnit=isTu
                                                   )
                sub_tes.append(subte)

            if isTp or isTg:
                for ts in dataTest['test-execution']:
                    isSubTu = False
                    if 'extension' in ts:
                        if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                            isSubTu = True

                    if ts['enable'] == TestModelCommon.TS_ENABLED:
                        subte_descr = dataTest['test-properties']['descriptions']['description']
                        subte = TestModelSub.createSubTest(dataTest=ts,
                                                           descriptions=subte_descr,
                                                           trPath=self.getTestPath(),
                                                           isTestUnit=isSubTu,
                                                           isTestPlan=isTp,
                                                           isTestGlobal=isTg)
                        sub_tes.append(subte)

        except Exception:
            self.error('unable to create sub te')
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(getBackTrace())

        self.trace("nb sub test: %s" % len(sub_tes))
        self.trace("Create the main test executable")
        try:
            dataTest = self.dataTest
            if envTmp:  # not alter data in tmp env
                dataTest = copy.deepcopy(self.dataTest)

            te = TestModel.createTestExecutable(
                dataTest=dataTest,
                userName=self.userName,
                testName=self.testName,
                trPath=self.getTestPath(),
                logFilename=self.completeId(),
                userId=self.userId,
                projectId=self.projectId,
                subTEs=len(sub_tes),
                channelId=self.channelId,
                parametersShared=self.ctx.instance().getTestEnvironment(user=self.userName),
                stepByStep=self.stepByStep,
                breakpoint=self.breakpoint,
                testId=self.testId,
                testLocation=self.getTestLocation(),
                runningAgents=AgentsManager.instance().getRunning(),
                taskUuid=self.taskUuid,
                var_path=Settings.get('Paths', 'testsresults')
            )
        except Exception as e:
            self.error('unable to create the main te: %s' % e)
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(getBackTrace())

        # Saving
        self.trace("Save the test executable on the disk")
        try:
            self.trace("Writing init file for test executable")
            # write test
            f = open("%s/__init__.py" % self.getPath(envTmp=envTmp), 'w')
            f.write("")
            f.close()

            self.trace("Writing all sub te")
            for i in xrange(len(sub_tes)):
                f = open("%s/SubTE%s.py" %
                         (self.getPath(envTmp=envTmp), i), 'wb')
                f.write(sub_tes[i])
                f.close()

            self.trace("Writing main path of the te")
            # write test path
            f = open(
                "%s/TESTPATH" %
                self.getPath(
                    envTmp=envTmp),
                'w')  # change in v16
            f.write("%s" % self.testPath)
            f.close()

            self.trace("Writing main te")
            # write test
            f = open(
                "%s/MainTE.py" %
                self.getPath(
                    envTmp=envTmp),
                'wb')  # change in v16
            f.write(te)
            f.close()

            self.trace("Writing task uuid")
            # write log
            f = open("%s/TASKID" % self.getPath(envTmp=envTmp), 'w')
            f.write("%s" % self.taskUuid)
            f.close()
            if not envTmp:
                self.saveTestDescr()
                RepoArchives.instance().cacheUuid(taskId=self.taskUuid,
                                                  testPath=self.getPath(envTmp=False, fullPath=False))

            self.trace("Writing log file")
            # write log
            f = open("%s/test.log" % self.getPath(envTmp=envTmp), 'wb')
            f.close()

            # write tests settings
            shutil.copy('%s/test.ini' % Settings.getDirExec(),
                        "%s/test.ini" % self.getPath(envTmp=envTmp))

            # tunning settings
            cfgtest_path = "%s/test.ini" % self.getPath(envTmp=envTmp)
            cfgparser = ConfigParser.RawConfigParser()
            cfgparser.read(cfgtest_path)

            path_storage = "%s/%s/" % (StorageDataAdapters.instance().getStoragePath(),
                                       self.getPath(fullPath=False))
            cfgparser.set('Paths', 'tmp', os.path.normpath(path_storage))

            path_template = "%s/%s/" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'templates'))
            cfgparser.set(
                'Paths',
                'templates',
                os.path.normpath(path_template))

            cfgparser.set(
                'Paths',
                'result',
                "%s" %
                self.getPath(
                    envTmp=envTmp))

            path_adapters = "%s/%s/" % (Settings.getDirExec(),
                                        Settings.get('Paths', 'packages-sutadapters'))
            cfgparser.set(
                'Paths',
                'sut-adapters',
                os.path.normpath(path_adapters))

            path_public = "%s/%s/" % (Settings.getDirExec(),
                                      Settings.get('Paths', 'public'))
            cfgparser.set('Paths', 'public', os.path.normpath(path_public))

            cfgparser.set(
                'Tests_Framework',
                'test-in-background',
                "%s" % int(
                    self.background))

            if self.debugActivated:
                cfgparser.set('Trace', 'level', "DEBUG")
            cfgtest = open(cfgtest_path, 'w')
            cfgparser.write(cfgtest)
            cfgtest.close()
        except OSError as e:
            self.error('unable to save te, system error: %s' % str(e))
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(e.strerror)
        except Exception:
            self.error('unable to save te')
            self.setState(state=STATE_ERROR, envTmp=envTmp)
            raise Exception(getBackTrace())

        # Notify all connected users to update archives
        # if it is not a run in the temporary env or
        # if it is not necessary to keep test result
        if not envTmp:
            if Settings.getInt('Notifications', 'archives'):
                if not self.noKeepTr:
                    # msg (dest, (action, data))
                    m = [{"type": "folder", "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                          "project": "%s" % self.projectId,
                          "content": [{"project": "%s" % self.projectId,
                                       "type": "folder",
                                       "name": self.completeId(),
                                       "virtual-name": self.completeId(withTestPath=True),
                                       "content": []}]}]
                    notif = {}
                    notif['archive'] = m
                    data = ('archive', (None, notif))
                    ESI.instance().notifyByUserAndProject(body=data,
                                                          admin=True,
                                                          monitor=False,
                                                          tester=True,
                                                          projectId="%s" % self.projectId)

        # Compilation
        if self.syntaxOK:
            self.trace(
                "Task[Tmp=%s] parse/compile: already done before" %
                envTmp)
        else:
            self.trace(
                "Task[Tmp=%s] parse/compile all sub test executable" %
                envTmp)
            t0 = time.time()
            for i in xrange(len(sub_tes)):
                try:
                    if sys.version_info > (3,):
                        parser.suite(sub_tes[i].decode("utf8")).compile()
                    else:
                        parser.suite(sub_tes[i]).compile()
                except SyntaxError as e:
                    e.lineno = None
                    self.trace('unable to compile sub te syntax: %s' % e)
                    self.setState(state=STATE_ERROR, envTmp=envTmp)
                    raise Exception(e)
                except SystemError as e:
                    self.error("Sub te server limitation raised: %s" % str(e))
                    self.setState(state=STATE_ERROR, envTmp=envTmp)
                    raise Exception("Limitation: this test is too big!")
                except Exception as e:
                    self.error('unable to compile sub te: %s' % getBackTrace())
                    self.setState(state=STATE_ERROR, envTmp=envTmp)
                    raise Exception(e)

            self.trace("Compile the main test executable")
            try:
                if sys.version_info > (3,):
                    parser.suite(te.decode("utf8")).compile()
                else:
                    parser.suite(te).compile()
            except SyntaxError as e:
                e.lineno = None
                self.trace('unable to compile syntax te: %s' % e)
                self.setState(state=STATE_ERROR, envTmp=envTmp)
                raise Exception(e)
            except SystemError as e:
                self.error("server limitation raised: %s" % str(e))
                self.setState(state=STATE_ERROR, envTmp=envTmp)
                raise Exception("Limitation: this test is too big!")
            except Exception as e:
                self.error('unable to compile te: %s' % getBackTrace())
                self.setState(state=STATE_ERROR, envTmp=envTmp)
                raise Exception(e)
            self.trace(
                "Task[Tmp=%s] parse/compile test terminated in %s sec." %
                (envTmp, (time.time() - t0)))

        # Remove the test from temp storage
        if envTmp:
            try:
                if os.path.exists(self.getPath(envTmp=envTmp)):
                    shutil.rmtree(self.getPath(envTmp=envTmp))
            except Exception as e:
                self.error("unable to delete the tmp test: %s" % str(e))

        self.setPrepared()
        self.trace(
            "Task[Tmp=%s] prepared in %s sec." %
            (envTmp, (time.time() - self.prepareTime)))
        return self.prepared

    def getTestDesign(self, returnXml=False, envTmp=False):
        """
        Return the report of the task
        """
        designs = ''
        if envTmp:
            testResultPath = '%s%s' % (Settings.getDirExec(),
                                       Settings.get('Paths', 'testsresults-tmp'))
        else:
            testResultPath = '%s%s' % (Settings.getDirExec(),
                                       Settings.get('Paths', 'testsresults'))
        testResultPath = os.path.normpath(testResultPath)

        fileName = "%s/%s/%s/%s/%s_%s" % (testResultPath,
                                          self.projectId,
                                          time.strftime(
                                              "%Y-%m-%d",
                                              time.localtime(
                                                  self.prepareTime)),
                                          self.completeId(),
                                          self.testName,
                                          str(self.replayId))
        fileName = os.path.normpath(fileName)

        try:
            if returnXml:
                f = open(
                    '%s.%s' %
                    (fileName, RepoManager.TEST_RESULT_DESIGN_XML_EXT), 'r')
            else:
                f = open(
                    '%s.%s' %
                    (fileName, RepoManager.TEST_RESULT_DESIGN_EXT), 'r')
            designs = f.read()
            if sys.version_info > (3,):
                pass
            else:
                designs = designs.decode('utf8')
            f.close()
        except Exception as e:
            self.error("open test result design failed: %s" % str(e))

        return designs

    def getTestReport(self, returnXml=False, basicReport=False):
        """
        Return the report of the task
        """
        reports = ''
        testResultPath = '%s%s' % (Settings.getDirExec(),
                                   Settings.get('Paths', 'testsresults'))
        testResultPath = os.path.normpath(testResultPath)

        fileName = "%s/%s/%s/%s/%s_%s" % (testResultPath,
                                          self.projectId,
                                          time.strftime(
                                              "%Y-%m-%d",
                                              time.localtime(
                                                  self.prepareTime)),
                                          self.completeId(),
                                          self.testName,
                                          str(self.replayId))
        fileName = os.path.normpath(fileName)

        try:

            if returnXml:
                reportExt = RepoManager.TEST_RESULT_REPORT_XML_EXT
                f = open('%s.%s' % (fileName, reportExt), 'r')
            else:
                reportExt = RepoManager.TEST_RESULT_REPORT_EXT
                if basicReport:
                    reportExt = RepoManager.TEST_RESULT_BASIC_REPORT_EXT
                f = open('%s.%s' % (fileName, reportExt), 'r')
            reports = f.read()
            if sys.version_info > (3,):
                pass
            else:
                reports = reports.decode('utf8')
            f.close()
        except Exception as e:
            self.error("open test result report failed: %s" % str(e))

        return reports

    def getTestVerdict(self, returnXml=False):
        """
        Return the verdict of the task
        """
        verdict = ''
        testResultPath = '%s%s' % (Settings.getDirExec(),
                                   Settings.get('Paths', 'testsresults'))
        testResultPath = os.path.normpath(testResultPath)

        fileName = "%s/%s/%s/%s/%s_%s" % (testResultPath,
                                          self.projectId,
                                          time.strftime(
                                              "%Y-%m-%d",
                                              time.localtime(
                                                  self.prepareTime)),
                                          self.completeId(),
                                          self.testName,
                                          str(self.replayId))
        fileName = os.path.normpath(fileName)

        try:
            if returnXml:
                f = open(
                    '%s.%s' %
                    (fileName, RepoManager.TEST_RESULT_VERDICT_XML_EXT), 'r')
            else:
                f = open(
                    '%s.%s' %
                    (fileName, RepoManager.TEST_RESULT_VERDICT_EXT), 'r')
            verdict = f.read()
            if sys.version_info > (3,):
                pass
            else:
                verdict = verdict.decode('utf8')
            f.close()
        except Exception as e:
            self.error("open test result verdict failed: %s" % str(e))

        return verdict

    def getFileResultPath(self):
        """
        This function is used to add a comment on a test result
        """
        testResultPath = '%s%s' % (
            Settings.getDirExec(), Settings.get('Paths', 'testsresults'))
        testResultPath = os.path.normpath(testResultPath)

        dirTask = "%s/%s/%s/" % (self.projectId,
                                 time.strftime(
                                     "%Y-%m-%d",
                                     time.localtime(
                                         self.prepareTime)),
                                 self.completeId())
        dirTask = os.path.normpath(dirTask)

        # Search the file on the disk because
        # the number of current comment can
        # be different that the value known by the user
        trxFile = 'undefined'
        for f in os.listdir(os.path.normpath("%s/%s" %
                                             (testResultPath, dirTask))):
            if f.startswith("%s_%s" % (self.testName, str(
                    self.replayId))) and f.endswith('trx'):
                trxFile = "%s%s" % (dirTask, f)
        return trxFile

    def notifResultLog(self):
        """
        Notify all users if new file is available
        Compress txt log to gzip
        filename = testname_replayid_nbcomments_verdict.testresult
        """
        testResultPath = '%s%s' % (Settings.getDirExec(),
                                   Settings.get('Paths', 'testsresults'))
        testResultPath = os.path.normpath(testResultPath)

        dirTask = "%s/%s/%s/" % (self.projectId,
                                 time.strftime(
                                     "%Y-%m-%d",
                                     time.localtime(
                                         self.prepareTime)),
                                 self.completeId())
        dirTask = os.path.normpath(dirTask)

        fileName = "%s/%s/%s/%s/%s_%s" % (testResultPath,
                                          self.projectId,
                                          time.strftime(
                                              "%Y-%m-%d",
                                              time.localtime(
                                                  self.prepareTime)),
                                          self.completeId(),
                                          self.testName,
                                          str(self.replayId))
        fileName = os.path.normpath(fileName)

        try:
            os.path.getsize("%s.log" % fileName)
        except Exception as e:
            self.error(e)
            return

        # read events from log
        f = open("%s.log" % fileName, 'r')
        read_data = f.read()
        f.close()

        # read events from log
        f2 = open("%s.hdr" % fileName, 'r')
        read_header = f2.read()
        f2.close()

        # get final result
        # this file "VERDICT" is created
        # by the test library throught
        # the function "log_script_stopped"
        verdict = 'UNDEFINED'
        path_verdict = "%s/%s/%s/%s/" % (testResultPath,
                                         self.projectId,
                                         time.strftime(
                                             "%Y-%m-%d",
                                             time.localtime(
                                                 self.prepareTime)),
                                         self.completeId())
        path_verdict = os.path.normpath(path_verdict)
        if os.path.exists(os.path.normpath("%s/VERDICT_PASS" % path_verdict)):
            verdict = 'PASS'
        if os.path.exists(os.path.normpath("%s/VERDICT_FAIL" % path_verdict)):
            verdict = 'FAIL'

        # fix issue remove global verdict on verdict, fix in v11.2
        try:
            os.remove(
                os.path.normpath(
                    "%s/VERDICT_%s" %
                    (path_verdict, verdict)))
        except Exception:
            pass

        try:
            f = open(os.path.normpath("%s/RESULT" % path_verdict), 'w')
            f.write(verdict)
            f.close()

            if verdict == "PASS":
                self.resultsStats["passed"] += 1
            if verdict == "FAIL":
                self.resultsStats["failed"] += 1
            if verdict == "UNDEFINED":
                self.resultsStats["undefined"] += 1

            self.saveTestDescr()
        except Exception as e:
            self.error("unable to write result file %s" % e)
        # end of new

        self.verdict = verdict

        # construct data model
        dataModel = TestResult.DataModel(testResult=read_data,
                                         testHeader=read_header)
        nbComments = 0
        filenameTrx = "%s_%s_%s.%s" % (fileName,
                                       verdict,
                                       str(nbComments),
                                       RepoManager.TEST_RESULT_EXT)
        f = open(os.path.normpath(filenameTrx), 'wb')
        raw_data = dataModel.toXml()
        if raw_data is not None:
            if sys.version_info > (3,):  # python3 support
                raw_data = bytes(raw_data, "utf8")
            f.write(zlib.compress(raw_data))
        f.close()

        # optimization remove log file in v12
        try:
            os.remove(os.path.normpath("%s.log" % fileName))
        except Exception:
            pass
        # end of new

        if Settings.getInt('Notifications', 'archives'):
            if self.noKeepTr and self.verdict != 'PASS':
                self.trace(
                    'no keep test result activated: notify because the result is not pass')
                # msg (dest, (action, data))
                m = [{"type": "folder",
                      "project": "%s" % self.projectId,
                      "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                      "content": [{"project": "%s" % self.projectId,
                                   "type": "folder",
                                   "name": self.completeId(),
                                   "content": [],
                                   "virtual-name": self.completeId(withTestPath=True)}]}]
                notif = {}
                notif['archive'] = m
                data = ('archive', (None, notif))

                ESI.instance().notifyByUserAndProject(body=data,
                                                      admin=True,
                                                      monitor=False,
                                                      tester=True,
                                                      projectId="%s" % self.projectId)

            if self.noKeepTr and self.verdict == 'PASS':
                self.trace(
                    'no keep test result activated: do not notify because the result is pass')
            else:
                size_ = os.path.getsize(filenameTrx)
                notif = {}
                m = [{"type": "folder",
                      "name": time.strftime("%Y-%m-%d", time.localtime(self.prepareTime)),
                      "project": "%s" % self.projectId,
                      "content": [{"type": "folder",
                                   "name": self.completeId(),
                                   "project": "%s" % self.projectId,
                                   "virtual-name": self.completeId(withTestPath=True),
                                   "content": [{"type": "file", "project": "%s" % self.projectId,
                                                "name": "%s_%s_%s_%s.%s" % (self.testName,
                                                                            str(self.replayId),
                                                                            verdict,
                                                                            str(nbComments),
                                                                            RepoManager.TEST_RESULT_EXT),
                                                'size': str(size_)}]}]}]
                notif['archive'] = m
                notif['stats-repo-archives'] = {'nb-zip': 0, 'nb-trx': 1, 'nb-tot': 1,
                                                'mb-used': RepoArchives.instance().getSizeRepoV2(folder=RepoArchives.instance().testsPath),
                                                'mb-free': RepoArchives.instance().freeSpace(p=RepoArchives.instance().testsPath)}
                data = ('archive', (None, notif))

                ESI.instance().notifyByUserAndProject(body=data,
                                                      admin=True,
                                                      monitor=False,
                                                      tester=True,
                                                      projectId="%s" % self.projectId)

        # not necessary to keep test results logs, delete it
        if self.noKeepTr:
            if self.verdict == 'PASS':
                try:
                    trPath = os.path.normpath(
                        '%s/%s' %
                        (testResultPath, dirTask))
                    if os.path.exists(trPath):
                        shutil.rmtree(trPath)
                except Exception as e:
                    self.error(
                        "unable to delete the test result (no keep tr option on result pass) %s" %
                        str(e))

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
        """
        # this run is a replay is greater than zero, then the test is already
        # ready
        if self.replayId > 0:
            testready = True
        else:
            if not needPrepare:
                testready = True
            else:
                # first run, prepare test on final environment
                try:
                    testready = self.prepare(envTmp=False)
                except Exception:
                    self.error('unable to prepare test')
                    self.setState(state=STATE_ERROR)
                    raise Exception(getBackTrace())

        # create temp adapters data storage
        StorageDataAdapters.instance().initStorage()

        # folder "completeid" is removed if already exists
        StorageDataAdapters.instance().initSubStorage(dirProject=self.projectId,
                                                      dirToday=time.strftime(
                                                          "%Y-%m-%d", time.localtime(self.prepareTime)),
                                                      dirTest=self.completeId())

        if testready:
            self.setState(state=STATE_RUNNING)
            # Prepare arguments
            if platform.system() == "Windows":
                executable = Settings.get('Bin', 'python-win')
            else:
                executable = Settings.get('Bin', 'python')
            cmdOptions = [str(self.schedId), str(
                self.testId), str(self.replayId)]

            # Construct the final execution line
            args = [executable]
            args.append(os.path.normpath("%s/MainTE.py" % self.getPath()))
            args = args + cmdOptions

            # create sh file
            if platform.system() == "Windows":
                launch_cmd = "launch.bat"
            else:
                launch_cmd = "launch.sh"
            launch_path = "%s/%s" % (self.getPath(), launch_cmd)

            f = open(os.path.normpath(launch_path), 'w')
            f.write(" ".join(args))
            f.close()

            # Run the test as an independant process
            try:
                p = subprocess.Popen(args)
                self.tpid = p.pid
                TaskMngr.addChildPid(pid=p.pid)
            except Exception as e:
                self.error('unable to fork te: %s' % e)
                self.setState(state=STATE_ERROR)
            else:
                p.wait()
                retcode = p.returncode

                if retcode == 0:
                    self.setState(state=STATE_COMPLETE)
                else:
                    self.error(
                        'unknown return code received: %s' %
                        str(retcode))
                    self.setState(state=STATE_ERROR)

            if self.tpid is not None:
                TaskMngr.delChildPid(pid=p.pid)

            # notify result log and by mail
            self.notifResultLog()
            if not self.withoutNotif:
                self.notifResultMail()

            if not self.noKeepTr:
                # Inspect the data storage adapters, zip data if present
                # and notify users connected
                zipped = StorageDataAdapters.instance().zipDataV2(
                    dirToday=time.strftime(
                        "%Y-%m-%d",
                        time.localtime(
                            self.prepareTime)),
                    dirTest=self.completeId(),
                    destPathZip=self.getPath(),
                    replayId=str(self.replayId),
                    projectId=self.projectId,
                    virtualName=self.completeId(withTestPath=True)
                )

                if zipped:
                    self.trace('Storage zipped for task')

            # delete temp adapters data storage
            StorageDataAdapters.instance().removeSubStorage(
                projectId=self.projectId,
                dirToday=time.strftime(
                    "%Y-%m-%d",
                    time.localtime(
                        self.prepareTime)),
                dirTest=self.completeId()
            )

            return self.state

    def notifResultMail(self):
        """
        """
        if platform.system() == "Windows":
            self.trace('Emails notifications not supported on Windows')
            return

        if not Settings.getInt('Notifications', 'emails'):
            self.trace('Emails notifications disabled')
            return

        if self.userName not in UsersManager.instance().cache():
            self.error('User=%s not found, send mail failed' % self.userName)
        else:
            user_profile = UsersManager.instance().cache()[self.userName]

            # PASS,FAIL,UNDEF,COMPLETE,ERROR,KILLED,CANCELLED
            # false;false;false;false;false;false;false
            notifications = user_profile['notifications'].split(';')
            self.trace(
                'notifications options for user %s: %s' %
                (self.userName, notifications))
            #  ['true', 'false', 'false', 'false', 'false', 'false', 'false', '']
            notifs_bool = [eval(x.title()) for x in notifications[:-1]]

            if self.state == STATE_COMPLETE and notifs_bool[3]:
                self.trace(
                    'task state [%s]: user notify enabled, mail to sent' %
                    self.state)
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_ERROR and notifs_bool[4]:
                self.trace(
                    'task state [%s]: user notify enabled, mail to sent' %
                    self.state)
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_KILLED and notifs_bool[5]:
                self.trace(
                    'task state [%s]: user notify enabled, mail to sent' %
                    self.state)
                self.sendMail(userTo=user_profile['email'])
            elif self.state == STATE_CANCELLED and notifs_bool[6]:
                self.trace(
                    'task state [%s]: user notify enabled, mail to sent' %
                    self.state)
                self.sendMail(userTo=user_profile['email'])
            else:
                self.trace(
                    'task state: notify on this state denied: %s' %
                    self.state)

            if self.verdict == "PASS" and notifs_bool[0]:
                self.trace(
                    'test verdict [%s]: user notify enabled, mail to sent' %
                    self.verdict)
                self.sendMail(userTo=user_profile['email'])
            elif self.verdict == "FAIL" and notifs_bool[1]:
                self.trace(
                    'test verdict [%s]: user notify enabled, mail to sent' %
                    self.verdict)
                self.sendMail(userTo=user_profile['email'])
            elif self.verdict == "UNDEFINED" and notifs_bool[2]:
                self.trace(
                    'test verdict [%s]: user notify enabled, mail to sent' %
                    self.verdict)
                self.sendMail(userTo=user_profile['email'])
            else:
                self.trace(
                    'test verdict: notify with this verdict denied: %s' %
                    self.verdict)

    def sendMail(self, userTo):
        """
        """
        self.trace('send mail to %s' % userTo)

        # new in v16
        basicReport = True
        if Settings.getInt('Notifications', 'advanced-report-by-email'):
            basicReport = False
        # end of new

        mailBody = self.getTestReport(basicReport=basicReport)
        appAcronym = Settings.get('Server', 'name')
        subject = "[%s] %s %s: %s" % (appAcronym.upper(),
                                      self.testType,
                                      self.verdict,
                                      self.testName)
        self.trace("Mail to sent(subject): %s" % subject)

        TaskMngr.sendMail(to=userTo,
                          subject=subject,
                          body=mailBody
                          )

    def killTest(self, removeFromContext=True):
        """
        Kill the test
        """
        self.removeFromContext = removeFromContext

        # reset all agents  before to kill the test
        # some threads can be running
        for _, details in TSI.instance().testsConnected.items():
            # test detected: {'task-id': '4', 'agents': [],
            # 'connected-at': 1446189597.512704, 'probes': []}
            if "task-id" in details:
                if int(details["task-id"]) == int(self.getId()):
                    self.trace(
                        "nb agents to reset before to kill: %s" % len(
                            details["agents"]))
                    TSI.instance().resetRunningAgent(client=details)
                    break

        # send kill signal
        if platform.system() == "Windows":
            if self.tpid is not None:
                kill_cmd = ["taskkill"]
                kill_cmd.append("/PID")
                kill_cmd.append("%s" % self.tpid)
                kill_cmd.append("/F")
                p = subprocess.Popen(kill_cmd, stdout=subprocess.PIPE)
                p.wait()
                if not p.returncode:
                    killed = True
                else:
                    killed = False
        else:
            killed = self.handleSignal(sig=SIGNAL_KILL)

        return killed

    def handleSignal(self, sig):
        """
        Handle unix signal
        """
        success = True
        if sig == SIGNAL_KILL and self.tpid is not None:
            try:
                os.kill(self.tpid, signal.SIGKILL)
            except Exception as e:
                self.error("Unable to kill %d: %s" % (self.tpid, str(e)))
                success = False
        return success


class TaskManager(Scheduler.SchedulerThread, Logger.ClassLogger):
    def __init__(self, context):
        """
        Construct Task Manager
        """
        Scheduler.SchedulerThread.__init__(
            self, out=self.trace, err=self.error)

        # self.statsmgr = statsmgr
        self.ctx = context

        self.mutex = threading.RLock()
        self.tasks = []
        self.enqueuedTasks = {}
        self.TN_HISTORY = 'tasks-history'
        self.BACKUPS_TASKS = os.path.normpath('%s/%s' % (Settings.getDirExec(),
                                                         Settings.get('Paths', 'backups-tasks')))

    def addChildPid(self, pid):
        """
        Save the PID of the child to kill it on stop if always running
        """
        self.trace("adding child pid %s" % pid)

        fileName = "%s/%s/%s.pid" % (Settings.getDirExec(),
                                     Settings.get('Paths', 'run'),
                                     pid)
        f = open(os.path.normpath(fileName), 'w')
        f.write("%s\n" % pid)
        f.close()

    def delChildPid(self, pid):
        """
        Delete the PID of the child to kill it on stop if always running
        """
        self.trace("removing child pid %s" % pid)
        try:
            fileName = "%s/%s/%s.pid" % (Settings.getDirExec(),
                                         Settings.get('Paths', 'run'),
                                         pid)
            os.remove(os.path.normpath(fileName))
        except IOError:
            pass

    def getEnqueued(self, b64=False):
        """
        Returns all enqueued task
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

                __grpTests.append(str(grpTst))

            enqueuedTasks[grpId[0]] = [grpId[1], __grpTests]

        return enqueuedTasks

    def cancelTaskInQueue(self, groupId, userName):
        """
        Cancel task in queue
        """
        self.trace('Canceling group of test %s' % groupId)
        if (groupId, userName) in self.enqueuedTasks:
            self.enqueuedTasks.pop((groupId, userName))

        # notify user
        data = ('task-enqueued', ("update", self.getEnqueued()))
        ESI.instance().notifyAll(body=data)

    def runQueueNextTask(self, groupId, userName):
        """
        Run next task from the queue
        """
        try:
            if (groupId, userName) in self.enqueuedTasks:
                testsUser = self.enqueuedTasks[(groupId, userName)]
                if len(testsUser):
                    tst = testsUser.pop(0)

                    # re-put in the queue
                    if len(testsUser):
                        self.enqueuedTasks[(groupId, userName)] = testsUser
                    else:
                        # no more tests to run
                        self.enqueuedTasks.pop((groupId, userName))

                    # finally run the test
                    self.runQueueTask(
                        tst=tst, groupId=groupId, userName=userName)
                else:
                    self.enqueuedTasks.pop((groupId, userName))
                    self.trace(
                        'tasks group id %s not exists (a) for user %s' %
                        (groupId, userName))
            else:
                self.trace(
                    'tasks group id %s not exists (b) for user %s' %
                    (groupId, userName))
        except Exception as e:
            self.error('queue run, unable to run the next one: %s' % e)

        # notify user
        data = ('task-enqueued', ("update", self.getEnqueued()))
        ESI.instance().notifyAll(body=data)

    def addTasks(self, userName, tests, runAt=(0, 0, 0, 0, 0, 0),
                 queueAt=False, simultaneous=False):
        """
        Adding tasks on the queue
        """
        self.trace('Nb test to enqueue: %s Login=%s' % (len(tests), userName))

        # enqueue tests to run
        groupId = getGroupId()

        # try to run tasks in simultaneous ?
        if simultaneous:
            self.runTasksInSimultaneous(tests=tests,
                                        groupId=groupId,
                                        userName=userName,
                                        runAt=runAt,
                                        queueAt=queueAt)
        else:

            self.enqueuedTasks[(groupId, userName)] = tests
            # notify user
            data = ('task-enqueued', ("update", self.getEnqueued()))
            ESI.instance().notifyAll(body=data)

            # take the first one
            tst = tests.pop(0)

            # if the list is not yet empty than save it again
            if len(tests):
                self.enqueuedTasks[(groupId, userName)] = tests

            # register the first test
            self.runQueueTask(tst=tst,
                              groupId=groupId,
                              userName=userName,
                              runAt=runAt,
                              queueAt=queueAt)

        return True

    def runTasksInSimultaneous(self, tests, groupId, userName,
                               runAt=(0, 0, 0, 0, 0, 0), queueAt=False):
        """
        Run tasks in simultaneous
        """
        self.trace("run tasks in simultaneous")
        # get user id
        usersDb = UsersManager.instance().cache()
        user_profile = usersDb[userName]

        runType = SCHED_QUEUE
        if queueAt:
            runType = SCHED_QUEUE_AT

        for tst in tests:
            try:
                kwargs = {
                    'testData': tst['test-data'],
                    'testName': tst['test-name'],
                    'testPath': tst['test-path'],
                    'testUserId': user_profile['id'],
                    'testUser': userName,
                    'testId': groupId,
                    'testBackground': True,
                    'runAt': runAt,
                    'runType': runType,
                    'runNb': -1,
                    'withoutProbes': False,
                    'debugActivated': False,
                    'withoutNotif': False,
                    'noKeepTr': False,
                    'testProjectId': tst['prj-id'],
                    'runFrom': (0, 0, 0, 0, 0, 0),
                    'runTo': (0, 0, 0, 0, 0, 0),
                    'groupId': groupId,
                    'runSimultaneous': True}

                testThread = threading.Thread(
                    target=self.registerTask, kwargs=kwargs)
                testThread.start()
            except Exception as e:
                self.error("group simultaneous tasks, error detected: %s" % e)

    def runQueueTask(self, tst, groupId, userName,
                     runAt=(0, 0, 0, 0, 0, 0), queueAt=False):
        """
        Run the task from queue
        """

        # get user id
        usersDb = UsersManager.instance().cache()
        user_profile = usersDb[userName]

        runType = SCHED_QUEUE
        if queueAt:
            runType = SCHED_QUEUE_AT
        try:
            task = self.registerTask(
                testData=tst['test-data'],
                testName=tst['test-name'],
                testPath=tst['test-path'],
                testUserId=user_profile['id'],
                testUser=userName,
                testId=groupId,
                testBackground=True,
                runAt=runAt,
                runType=runType,
                runNb=-1,
                withoutProbes=False,
                debugActivated=False,
                withoutNotif=False,
                noKeepTr=False,
                testProjectId=tst['prj-id'],
                runFrom=(0, 0, 0, 0, 0, 0),
                runTo=(0, 0, 0, 0, 0, 0),
                groupId=groupId
            )
        except Exception as e:
            self.error("group tasks, error detected: %s" % e)
            self.runQueueNextTask(groupId=groupId, userName=userName)
        else:
            if task.lastError is not None:
                self.error(
                    "group tasks: error detected on task: %s" %
                    task.lastError)
                self.runQueueNextTask(groupId=groupId, userName=userName)
        del tst

    def sendMail(self, to, subject, body):
        """
        """
        self.trace('sendmail to %s' % to)
        try:
            sendmail_location = Settings.get('Bin', 'sendmail')
            p = os.popen("%s -t" % sendmail_location, "w")
            email_dest = "noreply@%s" % (
                Settings.get('Server', 'name').replace(" ", ""))
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
            p.write(
                "<html><body>Extensive Automation Report in attachment</body></html>\n")

            p.write("---q1w2e3r4t5\n")
            p.write("Content-Transfer-Encoding: base64\n")
            p.write(
                "Content-Type: application/octet-stream; name=extensive_test_report.html\n")
            p.write(
                "Content-Disposition: attachment; filename=extensive_test_report.html\n")
            p.write("\n")
            p.write(base64.b64encode(body.encode("utf-8")))
            p.write("\n")
            p.write("---q1w2e3r4t5--")

        except Exception as e:
            self.error("unable prepare send mail: %s" % e)

        try:
            status = p.close()
            if status is not None:
                if status != 0:
                    self.error("sendmail status: %s" % status)
                else:
                    self.trace("Mail sent!")
        except Exception as e:
            self.error("unable to send mail: %s" % e)

    def addToHistory(self, task):
        """
        Called when the script is stopped
        """
        ret = None
        try:
            sql = "INSERT INTO `%s`(`eventtype`,`eventargs`,`eventtime`,`eventname`," % self.TN_HISTORY
            sql += "`eventauthor`,`realruntime`,`eventduration`,`eventresult`,`projectid`)"
            sql += "VALUES(%s, \"%s\", %s, \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s)" % task.toTuple()
            ret, lastinsertid = DbManager.instance().querySQL(sql, insertData=True)
        except Exception as e:
            self.error('unable to add task to history: %s' % str(e))
        return ret, lastinsertid

    def loadBackups(self):
        """
        Load backup from the var storage
        Function called on boot
        """
        if not Settings.getInt('Boot', 'reload-tasks'):
            return None

        success = True
        for fb in os.listdir(self.BACKUPS_TASKS):
            # Read backup file
            backup_path = os.path.normpath('%s/%s' % (self.BACKUPS_TASKS, fb))
            taskData = self.readBackup(backupFile=backup_path)
            if taskData is None:
                success = False
            else:
                # Unpack data
                testName, userName, testPath, testName, dataTest, \
                    testId, background, schedType, schedAt, schedNb, \
                    enabled, withoutProbes, withoutNotif, noKeepTr, \
                    userId, projectId, schedFrom, schedTo = taskData
                self.trace("Loading backup 1/3 ... %s %s %s %s" % (schedType,
                                                                   schedAt,
                                                                   schedNb,
                                                                   testName))
                self.trace("Loading backup 2/3 ... %s %s %s %s %s" % (userName,
                                                                      background,
                                                                      enabled,
                                                                      withoutProbes,
                                                                      withoutNotif))
                self.trace("Loading backup 3/3 ... %s %s %s %s %s" % (noKeepTr,
                                                                      userId,
                                                                      projectId,
                                                                      schedFrom,
                                                                      schedTo))

                # Remove backup file
                self.trace('deleting old backup %s' % fb)
                try:
                    os.remove(
                        os.path.normpath(
                            '%s/%s' %
                            (self.BACKUPS_TASKS, fb)))
                except Exception as e:
                    self.error('unable to delete the old backup: %s' % str(e))
                    success = False

                # finally reload the backup
                try:
                    if success:
                        try:
                            task = self.reloadTask(testData=dataTest,
                                                   testName=testName,
                                                   testPath=testPath,
                                                   testUser=userName,
                                                   testId=testId,
                                                   testBackground=background,
                                                   runAt=schedAt,
                                                   runType=schedType,
                                                   runNb=schedNb,
                                                   runEnabled=enabled,
                                                   withoutProbes=withoutProbes,
                                                   withoutNotif=withoutNotif,
                                                   noKeepTr=noKeepTr,
                                                   testUserId=userId,
                                                   testProjectId=projectId,
                                                   runFrom=schedFrom,
                                                   runTo=schedTo)
                            if task is None:
                                success = False
                        except Exception as e:
                            success = False
                            self.error('unable to reload task: %s' % str(e))
                except Exception as e:
                    self.error('unable to reload task: %s' % str(e))
                    success = False
        return success

    def readBackup(self, backupFile):
        """
        Read backup from the var storage
        """
        self.trace('reading backup %s' % backupFile)
        rlt = None
        try:
            fd = open(os.path.normpath(backupFile), "rb")
            data = fd.read()
            fd.close()

            # if sys.version_info > (3,):
            # data = bytes(data, "utf8")
            rlt = pickle.loads(data)
        except Exception as e:
            self.error('unable to read backup: %s' % str(e))
        return rlt

    def backupTask(self, task):
        """
        Backup the task to the var storage
        """
        self.trace('backuping task %s' % task.getId())
        try:
            backup_name = "%s/%s.dat" % (self.BACKUPS_TASKS,
                                         task.taskUuid)
            backup_name = os.path.normpath(backup_name)
            fd = open(backup_name, 'wb')

            schedAt = task.schedAt
            if task.schedType == SCHED_EVERY_X or task.schedType == SCHED_WEEKLY:
                schedAt = task.schedArgs

            data_task = [task.testName, task.userName, task.testPath,
                         task.testName, task.dataTest,
                         task.testId, task.background, task.schedType,
                         schedAt, task.schedNb, task.enabled,
                         task.withoutProbes, task.withoutNotif,
                         task.noKeepTr, task.userId, task.projectId,
                         task.schedFrom, task.schedTo]
            fd.write(pickle.dumps(data_task))
            fd.close()
        except Exception as e:
            self.error(
                'unable to backup the task %s: %s' %
                (task.getId(), str(e)))
            return False
        return True

    def deleteBackup(self, task):
        """
        Delete backup from the var storage
        """
        self.trace('deleting backup task %s' % task.getId())
        try:
            backup_name = "%s/%s.dat" % (self.BACKUPS_TASKS,
                                         task.taskUuid)
            backup_name = os.path.normpath(backup_name)
            os.remove(backup_name)
        except Exception as e:
            self.error(
                'unable to delete the task backup %s: %s' %
                (task.getId(), str(e)))
            return False
        return True

    def getListing(self, user):
        """
        return listing task
        """
        tasks = []

        # return only running task according to the user
        if user is not None:
            if isinstance(user, self.ctx.UserContext):
                prjs = user.getProjects()
            else:
                prjs = ProjectsManager.instance().getProjects(user=user)
            prjsDict = {}
            for prj in prjs:
                prjsDict[int(prj['project_id'])] = True
        for task in self.tasks:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED or task.state == STATE_RUNNING:
                if user is None:
                    tasks.append(task.toDict())
                else:
                    if int(task.projectId) in prjsDict:
                        tasks.append(task.toDict())

        return tasks

    def getHistory(self, Full=False, b64=False, user=None):
        """
        Get the task history from database
        """
        historyTasks = []

        if user is not None:
            if isinstance(user, self.ctx.UserContext):
                prjs = user.getProjects()
            else:
                prjs = ProjectsManager.instance().getProjects(user=user)

        sql = """SELECT `id`, `eventtype`, `eventargs`, `eventtime`, `eventname`, `eventauthor`,"""
        sql += """ `realruntime`, `eventduration`, `eventresult`, `projectid` FROM `%s` """ % self.TN_HISTORY

        if user is not None:
            sql += " WHERE "
            sqlMore = []
            for prj in prjs:
                sqlMore.append("`projectid`=%s" % int(prj['project_id']))
            sql += " OR " .join(sqlMore)

        ret, rows = DbManager.instance().querySQL(query=sql)
        if ret:
            if Settings.getInt('WebServices', 'nb-tasks-history') == -1:
                historyTasks = rows
            else:
                siz = len(rows) - Settings.getInt('WebServices',
                                                  'nb-tasks-history')
                if Full:
                    historyTasks = rows
                else:
                    historyTasks = rows[siz:]
        else:
            self.error('unable to get history event from database')

        return historyTasks

    def getWaiting(self, b64=False, user=None):
        """
        Returns all waiting task
        """
        waitingTasks = []
        # new in v10, return only running task according to the user
        if user is not None:
            if isinstance(user, self.ctx.UserContext):
                prjs = user.getProjects()
            else:
                prjs = ProjectsManager.instance().getProjects(user=user)
            prjsDict = {}
            for prj in prjs:
                prjsDict[int(prj['project_id'])] = True
        # end of new in v10

        for task in self.tasks:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                if user is None:
                    waitingTasks.append(
                        task.toTuple(
                            withId=True,
                            withGroupId=True))
                else:
                    # new in v10
                    if int(task.projectId) in prjsDict:
                        waitingTasks.append(task.toTuple(
                            withId=True, withGroupId=True))
                    # end of new in v10

        return waitingTasks

    def getRunning(self, b64=False, user=None):
        """
        Returns all running tasks
        """
        runningTasks = []
        # new in v10, return only running task according to the user
        if user is not None:
            if isinstance(user, self.ctx.UserContext):
                prjs = user.getProjects()
            else:
                prjs = ProjectsManager.instance().getProjects(user=user)
            prjsDict = {}
            for prj in prjs:
                prjsDict[int(prj['project_id'])] = True
        # end of new in v10

        for task in self.tasks:
            if task.state == STATE_RUNNING:
                if user is None:
                    runningTasks.append(task.toDict())
                else:
                    # new in v10
                    if int(task.projectId) in prjsDict:
                        runningTasks.append(task.toDict())
                    # end of new in v10

        return runningTasks

    def getTask(self, taskId):
        """
        Returns the task corresponding to the id passed as argument, otherwise None
        """
        for task in self.tasks:
            if task.getId() == taskId:
                return task
        return None

    def getTaskBy(self, taskId, userName=None):
        """
        Returns the task corresponding to the id passed as argument, otherwise None
        """
        ret = self.ctx.instance().CODE_NOT_FOUND
        for task in self.tasks:
            if task.getId() == taskId:
                if userName is not None:
                    if task.userName != userName:
                        self.trace(
                            'access to this task is denied %s' %
                            userName)
                        ret = self.ctx.instance().CODE_FORBIDDEN
                    else:
                        ret = task
                        break
                else:
                    ret = task
                    break
        return ret

    def executeTask(self, task, needPrepare=True):
        """
        Execute the task gived on argument
        """
        self.info("Starting test %s" % task.getId())
        testThread = threading.Thread(
            target=lambda: task.run(
                needPrepare=needPrepare))
        testThread.start()

    def replayTask(self, tid, userName=None):
        """
        Replay the task
        """
        self.trace("replaying task")
        task = self.getTask(taskId=tid)
        if task is None:
            self.trace('task %s not found' % tid)
            return self.ctx.instance().CODE_NOT_FOUND

        if userName is not None:
            if task.userName != userName:
                self.trace('access to this task is denied %s' % userName)
                return self.ctx.instance().CODE_FORBIDDEN

        # continue all is ok
        task.setReplayId()
        testRegistered = TSI.instance().registerTest(id=task.getId(),
                                                     background=task.background)
        if not testRegistered:
            msg_err = 'unable to register the task in the system'
            self.error(msg_err)
            return self.ctx.instance().CODE_ERROR

        self.trace("Re-backup the test")
        taskBackuped = self.backupTask(task=task)
        if not taskBackuped:
            msg_err = 'Unable to backup the task in the system'
            self.error(msg_err)
            return self.ctx.instance().CODE_ERROR

        self.executeTask(task=task)
        return self.ctx.instance().CODE_OK

    def reloadTask(self, testData, testName, testPath, testUser,
                   testId, testBackground, runAt,
                   runType, runNb, runEnabled,
                   withoutProbes, withoutNotif, noKeepTr,
                   testUserId, testProjectId,
                   runFrom, runTo):
        """
        Reload a specific task
        """
        self.trace("reloading task")
        toReload = True
        if runType == Scheduler.SCHED_AT or runType == Scheduler.SCHED_IN:
            timeref = time.time()
            if runAt < timeref:
                toReload = False
        if runType > Scheduler.SCHED_IN:
            toReload = True
        if runType == Scheduler.SCHED_NOW:
            toReload = False
        if runType == SCHED_QUEUE:
            toReload = False
        if runType == SCHED_QUEUE_AT:
            toReload = False
        if toReload:
            return self.registerTask(testData=testData,
                                     testName=testName,
                                     testPath=testPath,
                                     testUserId=testUserId,
                                     testUser=testUser,
                                     testId=testId,
                                     testBackground=testBackground,
                                     runAt=runAt,
                                     runType=runType,
                                     runNb=runNb,
                                     runEnabled=runEnabled,
                                     withoutProbes=withoutProbes,
                                     withoutNotif=withoutNotif,
                                     noKeepTr=noKeepTr,
                                     testProjectId=testProjectId,
                                     runFrom=runFrom, runTo=runTo
                                     )
        else:
            return None

    def noMoreLeftSpace(self):
        """
        Checking left space before running the test
        """
        # ignore this feature on windows
        if platform.system() == "Windows":
            return False

        mbUsed = RepoArchives.instance().getSizeRepoV2(
            folder=RepoArchives.instance().testsPath)
        mbFree = RepoArchives.instance().freeSpace(p=RepoArchives.instance().testsPath)

        mbMax = int(mbUsed) + int(mbFree)
        mbUsedPercent = (mbUsed * 100) / mbMax
        mbMaxSettings = Settings.getInt('Supervision', 'usage-testresult-max')

        self.trace("MB used/free: %s/%s" % (mbUsed, mbFree))
        self.trace(
            "MB used in percent/max: %s/%s" %
            (mbUsedPercent, mbMaxSettings))
        if mbUsedPercent >= mbMaxSettings:
            return True
        else:
            return False

    def registerTask(self, testData, testName, testPath,
                     testUser, testId, testBackground,
                     runAt, runType, runNb, runEnabled=True,
                     withoutProbes=False, debugActivated=False, withoutNotif=False,
                     noKeepTr=False, testUserId=0, testProjectId=0,
                     runFrom=(0, 0, 0, 0, 0, 0), runTo=(0, 0, 0, 0, 0, 0),
                     groupId=None, stepByStep=False,
                     breakpoint=False, runSimultaneous=False,
                     channelId=False):
        """
        - Get id from the scheduler
        - Check the syntax of test on the temp environment
        - Register the test in the TSI
        - Change the task's state from INIT to WAITING
        - Register the task in the scheduler
        - Save the task in the list and notify all connected users
        """
        self.mutex.acquire()

        self.trace("Register task [Type=%s] [At=%s] [Nb=%s] [Name=%s] [User=%s]" % (runType,
                                                                                    runAt,
                                                                                    runNb,
                                                                                    testName,
                                                                                    testUser))
        self.trace("Register task. [Back=%s] [Enabled=%s] [Debug=%s] " % (testBackground,
                                                                          runEnabled,
                                                                          debugActivated))
        self.trace("Register task. [Notif=%s]" % (withoutNotif))
        self.trace("Register task.. [NoKeepTr=%s] [UserId=%s] [PID=%s] [Run-From=%s]" % (noKeepTr,
                                                                                         testUserId,
                                                                                         testProjectId,
                                                                                         runFrom))
        self.trace("Register task... [Run-To=%s] [Step=%s] [Break=%s] [ChannId=%s]" % (runTo,
                                                                                       stepByStep,
                                                                                       breakpoint,
                                                                                       channelId))

        task = Task(testData=testData,
                    testName=testName,
                    testPath=testPath,
                    testUser=testUser,
                    testId=testId,
                    testUserId=testUserId,
                    testBackground=testBackground,
                    taskEnabled=runEnabled,
                    withoutProbes=withoutProbes,
                    debugActivated=debugActivated,
                    withoutNotif=withoutNotif,
                    noKeepTr=noKeepTr,
                    testProjectId=testProjectId,
                    stepByStep=stepByStep,
                    breakpoint=breakpoint,
                    runSimultaneous=runSimultaneous,
                    channelId=channelId,
                    context=self.ctx)
        task.setId(self.getEventId())

        if groupId is not None:
            self.trace("Group tasks id=%s" % groupId)
            task.setGroupId(groupId=groupId)

        self.trace("Checking left space on test results folder")
        if self.noMoreLeftSpace():
            self.error('No more space left on test results folder')
            task.lastError = 'No more space left on test results'
            self.mutex.release()
            return task
        else:
            self.trace("disk usage ok? yes, continue")

        self.trace("Prepare the task=%s and check the syntax" % task.getId())
        # Prepare the test and check if the syntax is correct
        try:
            task.initPrepare()
            task.prepare(envTmp=True)
        except Exception as e:  # task state is changed to ERROR
            task.lastError = 'Unable to prepare: %s' % str(e)
            self.mutex.release()
            return task
        else:
            task.setSyntaxOK()

        self.trace("Register the task %s on the TSI" % task.getId())
        # Register the test in the TSI
        testRegistered = TSI.instance().registerTest(id=task.getId(),
                                                     background=task.background)
        if not testRegistered:
            task.lastError = 'Unable to register the task in the system'
            self.error(task.lastError)
            self.mutex.release()
            return task

        self.trace("Initialize the start time of task %s" % task.getId())
        task.schedNb = runNb
        # Initialize the task with the start time
        if isinstance(runAt, tuple) or isinstance(runAt, list):
            self.trace("Task %s init" % task.getId())
            timesec = task.initialize(runAt=runAt,
                                      runType=runType,
                                      runNb=runNb,
                                      runEnabled=runEnabled,
                                      withoutProbes=withoutProbes,
                                      debugActivated=debugActivated,
                                      withoutNotif=withoutNotif,
                                      noKeepTr=noKeepTr,
                                      runFrom=runFrom,
                                      runTo=runTo)
            self.trace("Task %s should run at %s" % (task.getId(), timesec))
        else:
            self.trace("Task %s init manual" % task.getId())
            task.schedAt = runAt
            task.schedType = runType
            task.schedArgs = self.getTimeToTuple(task.schedAt)
            timesec = task.schedAt

        if task.isRecursive():
            self.trace("Task %s is recursive" % task.getId())
            schedExceptions = [SCHED_NOW_MORE]
            if Settings.getInt('TaskManager', 'everyminx-run-immediately'):
                schedExceptions.append(SCHED_EVERY_X)
            if task.schedType not in schedExceptions:
                timeref = time.time()
                while timesec < timeref:
                    self.trace(
                        "Catches up the late for the task %s" %
                        task.getId())
                    timesec = self.getNextTime(schedType=task.schedType,
                                               shedAt=task.schedAt,
                                               schedArgs=task.schedArgs,
                                               schedFrom=runFrom,
                                               schedTo=runTo)
                    task.schedAt = timesec
                    # BEGIN new in 3.2.0
                    if task.schedType == SCHED_WEEKLY:
                        pass
                    # END
                    else:
                        task.schedArgs = self.getTimeToTuple(task.schedAt)

        # Change the state from INIT to WAITING
        task.setState(state=STATE_WAITING)

        self.trace("Backup the task %s" % task.getId())
        # Backup the task on the disk
        taskBackuped = self.backupTask(task=task)
        if not taskBackuped:
            task.lastError = 'Unable to:\n\n - Backup the task in the system'
            self.error(task.lastError)
            self.mutex.release()
            return task

        needPrepare = True
        if runType == Scheduler.SCHED_NOW:
            self.trace(
                "Prepare the task %s in the prod environment" %
                task.getId())
            prep = task.prepare(envTmp=False)
            needPrepare = False
            self.trace("Prepare the task %s ok ? %s" % (task.getId(), prep))

        self.trace("Register the task %s on the scheduler" % task.getId())
        # Register the task on the scheduler
        EventReg = self.registerEvent(id=task.getId(),
                                      author=task.userName,
                                      name=task.getTaskName(),
                                      weekly=None,
                                      daily=None,
                                      hourly=None,
                                      everyMin=None,
                                      everySec=None,
                                      at=None,
                                      delay=None,
                                      timesec=timesec,
                                      callback=self.executeTask,
                                      task=task,
                                      needPrepare=needPrepare)
        task.setEventReg(event=EventReg)

        if not runEnabled:
            self.trace(
                'Unregister the task %s from the scheduler' %
                task.getId())
            taskDisabled = TaskMngr.unregisterEvent(event=task.eventReg)
            if not taskDisabled:
                self.error(
                    'unable to unregister the following task %s' %
                    task.getId())
                task.setState(state=STATE_ERROR)
            else:
                task.setState(state=STATE_DISABLED)
                self.info('Task %s disabled' % str(task.getId()))

        #  Save the task on the list and notify all connected users
        self.tasks.append(task)
        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-waiting', ("update", self.getWaiting(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        self.info("Task registered with id %s" % task.getId())

        self.mutex.release()
        return task

    def delTask(self, taskId, userName=None):
        """
        """
        self.trace("removing task %s" % taskId)
        success = self.ctx.instance().CODE_ERROR

        task = self.getTask(taskId=taskId)
        if task is None:
            self.error('task %s not found' % taskId)
            success = self.ctx.instance().CODE_NOT_FOUND
        else:

            if userName is not None:
                if task.userName != userName:
                    self.trace('access to this task is denied %s' % userName)
                    return self.ctx.instance().CODE_FORBIDDEN

            if task.state in [STATE_ERROR, STATE_COMPLETE, STATE_CANCELLED]:
                self.trace("remove tast from list")
                self.tasks.remove(task)

                success = self.ctx.instance().CODE_OK

            else:
                self.trace('task can be removed in this state %s' % task.state)
                return self.ctx.instance().CODE_ERROR

        return success

    def killTask(self, taskId, userName=None):
        """
        Kill a specific running task
        """
        self.trace("killing task %s" % taskId)
        success = self.ctx.instance().CODE_ERROR

        task = self.getTask(taskId=taskId)
        if task is None:
            self.error('task %s not found' % taskId)
            success = self.ctx.instance().CODE_NOT_FOUND
        else:
            if userName is not None:
                if task.userName != userName:
                    self.trace('access to this task is denied %s' % userName)
                    return self.ctx.instance().CODE_FORBIDDEN

            if task.state == STATE_RUNNING:
                task.setState(state=STATE_KILLING)
                killed = task.killTest()
                if killed:
                    success = self.ctx.instance().CODE_OK
                    self.info('Task %s killed' % str(taskId))
        return success

    def killAllTasks(self):
        """
        Kill all running tasks
        """
        self.trace("killing all tasks")
        success = True
        tasksToRemove = []
        for task in self.tasks:
            if task.state == STATE_RUNNING:
                task.setState(state=STATE_KILLING)
                killed = task.killTest(removeFromContext=False)
                if not killed:
                    success = False
                else:
                    tasksToRemove.append(task)
        for task in tasksToRemove:
            self.removeTask(task=task)
        del tasksToRemove
        return success

    def cancelTask(self, taskId, userName=None):
        """
        Cancel a specific waiting task
        """
        self.trace("cancelling task %s" % taskId)
        success = self.ctx.instance().CODE_ERROR

        task = self.getTask(taskId=taskId)
        if task is None:
            self.error('task %s not found' % taskId)
            success = self.ctx.instance().CODE_NOT_FOUND
        else:
            if userName is not None:
                if task.userName != userName:
                    self.trace('access to this task is denied %s' % userName)
                    return self.ctx.instance().CODE_FORBIDDEN

            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                taskCancelled = task.cancelTest()
                if not taskCancelled:
                    self.error(
                        'unable to cancel the following task %s' %
                        task.getId())
                else:
                    success = self.ctx.instance().CODE_OK
                    self.info('Task %s cancelled' % str(taskId))

        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-waiting', ("update", self.getWaiting(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success

    def cancelAllTasks(self):
        """
        Cancel all waiting tasks
        """
        self.trace("cancelling all tasks")
        success = True
        tasksToRemove = []
        for task in self.tasks:
            if task.state == STATE_WAITING or task.state == STATE_DISABLED:
                taskCancelled = task.cancelTest(removeFromContext=False)
                if not taskCancelled:
                    self.error(
                        'unable to cancel the following task %s' %
                        task.getId())
                    success = False
                else:
                    tasksToRemove.append(task)
        for task in tasksToRemove:
            self.removeTask(task=task)
        del tasksToRemove

        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-waiting', ("update", self.getWaiting(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success

    def clearHistory(self):
        """
        Clear history from database
        """
        self.trace("clearing task history")
        try:
            sql = "DELETE FROM `%s`;" % self.TN_HISTORY
            ret, _ = DbManager.instance().querySQL(sql)
            if not ret:
                raise Exception("sql problem: %s" % self.TN_HISTORY)
        except Exception as e:
            self.error('unable to delete all tasks from history: %s' % str(e))
            return False

        # notify all connected users
        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-history', ("update", self.getHistory(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return True

    def onTaskFinished(self, task):
        """
        Called when a task is finished
        """
        self.trace("Re-scheduling task %s..." % task.getId())

        self.trace(
            "Checking left space on %s before to re-schedule the test" %
            Settings.get(
                'Paths',
                'testsresults'))
        if self.noMoreLeftSpace():
            # Remove the task on the list
            self.removeTask(task=task)

            self.error(
                'No more space left on %s' %
                Settings.get(
                    'Paths',
                    'testsresults'))
            # notify user
            data = (
                'supervision',
                ("level-critical",
                 'Test execution stopped!\nNo more space left on %s' %
                 Settings.get(
                     'Paths',
                     'testsresults')))
            ESI.instance().notifyAll(body=data)
        else:
            self.trace("disk usage ok? yes, continue")

        # Remove the task from the disk
        backupDeleted = self.deleteBackup(task=task)
        if not backupDeleted:
            self.trace(
                "unable to delete the backup of the task %s" %
                task.getId())

        # Remove the task from the context if in the following states:
        # cancelled, error and killed
        if task.state in [STATE_CANCELLED, STATE_ERROR, STATE_KILLED]:
            if task.removeFromContext:
                self.removeTask(task=task)

        # Exit if the task going from the queue
        if task.groupId > 0:
            if not task.runSimultaneous:
                self.trace(
                    "Group of tasks %s detected, running the next one? yes" %
                    task.groupId)
                if task.state in [STATE_CANCELLED]:
                    self.cancelTaskInQueue(groupId=task.groupId,
                                           userName=task.userName)
                else:
                    self.runQueueNextTask(groupId=task.groupId,
                                          userName=task.userName)
                return
        else:
            self.trace(
                "No group id %s, running the next one ? no" %
                task.getId())

        # Exit if the task is not recursive
        if not task.isRecursive():
            self.trace("task %s is recursive? no" % task.getId())
            return
        else:
            self.trace("task %s is recursive? yes" % task.getId())

        # Exit if the task is not in the complete state
        if task.state != STATE_COMPLETE:
            self.trace("task %s is completed? no" % task.getId())
            return
        else:
            self.trace("task %s is completed? yes so continue" % task.getId())

        # check the counter of run
        if not task.runAgain():
            self.trace("Run again task %s? no more run" % task.getId())
            return
        else:
            self.trace("Run again task %s? yes" % task.getId())

        # check the interval
        if not task.alwaysRun():
            self.trace("Always run task %s? no more run" % task.getId())
            # return
        else:
            self.trace("Always run task %s? yes" % task.getId())

        # create a new task
        taskNew = Task(
            testData=task.dataTest,
            testName=task.testName,
            testPath=task.testPath,
            testUser=task.userName,
            testId=task.testId,
            testUserId=task.userId,
            testBackground=task.background,
            taskEnabled=task.enabled,
            withoutProbes=task.withoutProbes,
            withoutNotif=task.withoutNotif,
            debugActivated=task.debugActivated,
            noKeepTr=task.noKeepTr,
            testProjectId=task.projectId,
            stepByStep=task.stepByStep,
            breakpoint=task.breakpoint,
            runSimultaneous=task.runSimultaneous,
            channelId=task.channelId,
            context=self.ctx
        )
        # taskNew.taskUuid = task.taskUuid
        taskNew.setId(self.getEventId())
        taskNew.initPrepare()
        taskNew.setPrepared()
        taskNew.recurId = task.recurId + 1
        taskNew.resultsStats = task.resultsStats

        # Register the test on the TSI
        testRegistered = TSI.instance().registerTest(id=taskNew.getId(),
                                                     background=taskNew.background)
        if not testRegistered:
            msg_err = 'unable to re-register the task in the system'
            self.error(msg_err)
            # Remove the task on the list
            self.removeTask(task=task)
            return

        # Initialize the task with the start time
        taskNew.schedNb = task.schedNb
        taskNew.schedType = task.schedType
        taskNew.schedFrom = task.schedFrom
        taskNew.schedTo = task.schedTo
        taskNew.schedAt = self.getNextTime(schedType=task.schedType,
                                           shedAt=task.schedAt,
                                           schedArgs=task.schedArgs,
                                           schedFrom=task.schedFrom,
                                           schedTo=task.schedTo)
        if taskNew.schedType == SCHED_EVERY_X or taskNew.schedType == SCHED_WEEKLY:
            taskNew.schedArgs = task.schedArgs
        else:
            taskNew.schedArgs = self.getTimeToTuple(taskNew.schedAt)

        # Change the state from INIT to WAITING
        taskNew.setState(state=STATE_WAITING)

        # Backup the task on the disk
        taskBackuped = self.backupTask(task=taskNew)
        if not taskBackuped:
            msg_err = 'unable to re-backup the task in the system'
            self.error(msg_err)
            self.mutex.release()
            return msg_err

        # Register the task on the scheduler
        EventReg = self.registerEvent(id=taskNew.getId(),
                                      author=taskNew.userName,
                                      name=taskNew.getTaskName(),
                                      weekly=None,
                                      daily=None,
                                      hourly=None,
                                      everyMin=None,
                                      everySec=None,
                                      at=None,
                                      delay=None,
                                      timesec=taskNew.schedAt,
                                      callback=self.executeTask,
                                      task=taskNew)
        taskNew.setEventReg(event=EventReg)

        # Save the task on the list and notify all connected users
        self.tasks.append(taskNew)
        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-waiting', ("update", self.getWaiting(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        self.info("Task re-scheduled with id %s" % taskNew.getId())

        # Remove the task on the list
        self.removeTask(task=task)

    def getNextTime(self, schedType, shedAt, schedArgs,
                    schedFrom=(0, 0, 0, 0, 0, 0),
                    schedTo=(0, 0, 0, 0, 0, 0)):
        """
        Compute the next timestamp
        """
        self.trace('Computing the next run time')
        _, _, _, h, mn, s = schedArgs
        if schedType == Scheduler.SCHED_DAILY:
            shedAt = shedAt + 60 * 60 * 24
        if schedType == Scheduler.SCHED_HOURLY:
            shedAt = shedAt + 60 * 60
        if schedType == Scheduler.SCHED_EVERY_MIN:
            shedAt = shedAt + 60
        if schedType == SCHED_EVERY_X:
            shedAt = shedAt + 60 * 60 * h + 60 * mn + s
        if schedType == SCHED_WEEKLY:
            shedAt = shedAt + 7 * 24 * 60 * 60
        return shedAt

    def getTimeToTuple(self, timestamp):
        """
        Convert a timestamp to tuple
        """
        dt = datetime.datetime.fromtimestamp(timestamp)
        return (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

    def removeTask(self, task):
        """
        Remove the task from the context
        """
        return

        self.trace('removing task %s' % task.getId())
        try:
            self.tasks.remove(task)
        except Exception as e:
            self.error(
                'Task [Id=%s] no more exists in the list: %s' %
                (task.getId(), str(e)))

    def updateTask(self, taskId, schedType, shedAt, schedNb,
                   schedEnabled=True, withoutProbes=False,
                   debugActivated=False, noKeepTr=False, withoutNotif=False,
                   schedFrom=(0, 0, 0, 0, 0, 0), schedTo=(0, 0, 0, 0, 0, 0), userName=None):
        """
        Update a specific task, change the start time
        """
        self.trace("update task %s" % taskId)
        success = self.ctx.instance().CODE_ERROR

        task = self.getTask(taskId=taskId)
        if task is None:
            self.error('task %s not found' % taskId)
            success = self.ctx.instance().CODE_NOT_FOUND
        else:
            if userName is not None:
                if task.userName != userName:
                    self.trace('access to this task is denied %s' % userName)
                    return self.ctx.instance().CODE_FORBIDDEN

            # Initialize the task with the start time
            timesec = task.initialize(runAt=shedAt,
                                      runType=schedType,
                                      runNb=schedNb,
                                      runEnabled=schedEnabled,
                                      withoutProbes=withoutProbes,
                                      debugActivated=debugActivated,
                                      noKeepTr=noKeepTr,
                                      withoutNotif=withoutNotif,
                                      runFrom=schedFrom, runTo=schedTo)

            if task.isRecursive():
                timeref = time.time()
                while timesec < timeref:
                    self.trace("catches up the late")
                    timesec = self.getNextTime(schedType=task.schedType,
                                               shedAt=task.schedAt,
                                               schedArgs=task.schedArgs,
                                               schedFrom=schedFrom,
                                               schedTo=schedTo)
                    task.schedAt = timesec

            if task.state == STATE_DISABLED:
                task.setState(state=STATE_UPDATING)
                EventReg = self.registerEvent(id=task.getId(),
                                              author=task.userName,
                                              name=task.getTaskName(),
                                              weekly=None,
                                              daily=None,
                                              hourly=None,
                                              everyMin=None,
                                              everySec=None,
                                              at=None,
                                              delay=None,
                                              timesec=task.schedAt,
                                              callback=self.executeTask,
                                              task=task)
                task.setState(state=STATE_WAITING)
                task.setEventReg(event=EventReg)
                self.info('Task %s enabled' % str(taskId))
                success = self.ctx.instance().CODE_OK

                # Backup the task on the disk
                self.trace("Backup the test")
                taskBackuped = self.backupTask(task=task)
                if not taskBackuped:
                    self.error('Unable to backup the task in the system')

            elif task.state == STATE_WAITING:
                task.setState(state=STATE_UPDATING)
                if not schedEnabled:
                    taskDisabled = TaskMngr.unregisterEvent(
                        event=task.eventReg)
                    if not taskDisabled:
                        self.error(
                            'unable to unregister the following task %s' %
                            task.getId())
                        task.setState(state=STATE_ERROR)
                    else:
                        success = self.ctx.instance().CODE_OK
                        task.setState(state=STATE_DISABLED)
                        self.info('Task %s disabled' % str(taskId))
                else:
                    # Update event in the scheduler
                    taskRescheduled = TaskMngr.updateEvent(event=task.eventReg,
                                                           weekly=None,
                                                           daily=None,
                                                           hourly=None,
                                                           everyMin=None,
                                                           everySec=None,
                                                           at=None,
                                                           delay=None,
                                                           timesec=timesec)
                    if not taskRescheduled:
                        self.error(
                            'unable to update the following task %s' %
                            task.getId())
                        task.setState(state=STATE_ERROR)
                    else:
                        success = self.ctx.instance().CODE_OK
                        task.setState(state=STATE_WAITING)
                        self.info('Task %s updated' % str(taskId))

                # Backup the task on the disk
                self.trace("Backup the test")
                taskBackuped = self.backupTask(task=task)
                if not taskBackuped:
                    self.error('Unable to backup the task in the system')

            else:
                self.error(
                    'invalid state during the update of the task [current state=%s]' %
                    task.state)

        # notify all connected users
        connected = self.ctx.instance().getUsersConnectedCopy()
        for cur_user in connected:
            data = ('task-waiting', ("update", self.getWaiting(user=cur_user)))
            ESI.instance().notify(body=data, toUser=cur_user)
        del connected
        return success


def getObjectTask(testData, testName, testPath,
                  testUser, testId, testBackground,
                  projectId=0, context=None):
    """
    """
    task = Task(testData,
                testName,
                testPath,
                testUser,
                testId,
                testBackground,
                testProjectId=projectId,
                context=context)
    return task


TaskMngr = None


def instance():
    """
    Returns the singleton
    """
    return TaskMngr


def initialize(context):
    """
    Instance creation
    """
    global TaskMngr
    TaskMngr = TaskManager(context=context)
    TaskMngr.start()


def finalize():
    """
    Destruction of the singleton
    """
    global TaskMngr
    if TaskMngr:
        TaskMngr.stop()
        TaskMngr.join()
        TaskMngr = None
