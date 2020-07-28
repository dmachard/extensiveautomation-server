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

import sys
import os
try:
    import scandir
except ImportError:  # for python3 support
    scandir = os
import base64
import zlib
import json
import hashlib
import re
import platform
try:
    import cStringIO
    import cPickle
except ImportError:  # support python 3
    import io as cStringIO
    import pickle as cPickle
import pathlib

from ea.serverrepositories import RepoManager
from ea.libs import (Settings, Logger)
from ea.libs.FileModels import TestResult as TestResult
from ea.serverinterfaces import EventServerInterface as ESI


class RepoArchives(RepoManager.RepoManager, Logger.ClassLogger):
    """
    Repository Archives
    """

    def __init__(self, context):
        """
        Repository manager for archives files
        """
        RepoManager.RepoManager.__init__(self,
                                         pathRepo='%s%s' % (Settings.getDirExec(),
                                                            Settings.get('Paths', 'testsresults')),
                                         extensionsSupported=[RepoManager.TEST_RESULT_EXT, RepoManager.TXT_EXT,
                                                              RepoManager.CAP_EXT, RepoManager.ZIP_EXT,
                                                              RepoManager.PNG_EXT, RepoManager.JPG_EXT],
                                         context=context)
        self.context = context

        self.cacheUuids = {}
        self.cachingUuid()
        self.trace("nb entries in testresult cache: %s" % len(self.cacheUuids))

    def getTree(self, b64=False, fullTree=False, project=1):
        """
        Return tree of files
        """
        nb = Settings.getInt('WebServices', 'nb-archives')
        if nb == -1:
            nb = None
        if nb == 0:
            return (0, 0, [], {})

        if fullTree:
            nb = None

        success = os.path.exists("%s/%s" % (self.testsPath, project))
        if not success:
            return (0, 0, [], {})
        else:
            return self.getListingFilesV2(path="%s/%s" % (self.testsPath, project),
                                          nbDirs=nb,
                                          project=project,
                                          archiveMode=True)

    def getLastEventIndex(self, pathEvents):
        """
        Returns the last event index file
        """
        lastIndex = 0
        for f in os.listdir(pathEvents):
            if f.endswith('.log'):
                try:
                    idx = f.rsplit('_', 1)[1].split(".log")[0]
                except Exception:
                    continue
                if int(idx) > lastIndex:
                    lastIndex = idx
        return lastIndex

    def createTrTmp(self, trPath):
        """
        Create a temporary test result file
        """
        trFileName = None
        try:
            pathTest = "%s/%s" % (self.testsPath, trPath)
            pathTest = os.path.normpath(pathTest)

            indexFile = self.getLastEventIndex(pathEvents=pathTest)
            _, trName = self.getTrLogName(trPath,
                                          replayId=indexFile,
                                          withExt=False,
                                          matchExt="log")
            if trName is None:
                raise Exception("no tr founded with replay id=%s" % indexFile)

            # read events from log
            f = open("%s/%s.log" % (pathTest, trName), 'r')
            read_data = f.read()
            f.close()

            # create tmp file
            dataModel = TestResult.DataModel(testResult=read_data)
            trFileName = "%s.tmp" % trName

            # path to new temp file
            tmpPath = "%s/%s" % (pathTest, trFileName)
            f = open(tmpPath, 'wb')
            raw_data = dataModel.toXml()

            if sys.version_info > (3,):
                raw_data = bytes(raw_data, "utf8")
            f.write(zlib.compress(raw_data))
            f.close()
        except Exception as e:
            self.error(e)
            return (self.context.CODE_ERROR, trFileName)
        return (self.context.CODE_OK, trFileName)

    def resetArchives(self, projectId=1):
        """
        Removes all archives from hard disk,
        no way to reverse this call
        """
        ret = self.context.CODE_ERROR
        try:
            # delete all folders and files
            ret = self.emptyRepo(projectId=projectId)

            # reset the cache
            if projectId in self.cacheUuids:
                del self.cacheUuids[projectId]
        except Exception as e:
            self.error("Unable to reset archives %s" % str(e))
        return ret

    def addComment(self, archiveUser, archivePath,
                   archivePost, archiveTimestamp):
        """
        Add comment to the archive gived on argument
        """
        self.trace("add comment in test result")
        comments = False
        newArchivePath = False
        try:
            # prepare path
            completePath = "%s/%s" % (self.testsPath, archivePath)
            completePath = os.path.normpath(completePath)

            # to avoid error, the server try to find the good file by himself
            # just take the name of the name and the replay id to find the test
            # automaticly
            trxPath, rightover = archivePath.rsplit('/', 1)
            trxfile = rightover.rsplit('_', 1)[0]

            for f in os.listdir("%s/%s" % (self.testsPath, trxPath)):
                if f.startswith(trxfile) and f.endswith(
                        RepoManager.TEST_RESULT_EXT):
                    completePath = "%s/%s/%s" % (self.testsPath, trxPath, f)
                    completePath = os.path.normpath(completePath)

            # read test result
            self.trace("read test result")
            dataModel = TestResult.DataModel()
            trLoaded = dataModel.load(absPath=completePath)
            if not trLoaded:
                raise Exception("failed to load test result")

            self.trace("add comment in data model")
            self.trace("username: %s" % archiveUser)
            self.trace("userpost: %s" % archivePost)
            self.trace("post timestamp: %s" % archiveTimestamp)
            archivePost = str(archivePost)
            postAdded = dataModel.addComment(user_name=archiveUser,
                                             user_post=archivePost,
                                             post_timestamp=archiveTimestamp)
            if postAdded is None:
                raise Exception("unable to add comment in test result")
            dataModel.properties['properties']['comments'] = postAdded
            comments = postAdded['comment']

            self.trace("save test result")
            f = open(completePath, 'wb')
            raw_data = dataModel.toXml()

            if sys.version_info > (3,):
                raw_data = bytes(raw_data, "utf8")

            f.write(zlib.compress(raw_data))
            f.close()

            # rename file to update the number of comment in filename
            nbComments = len(postAdded['comment'])
            leftover, _ = archivePath.rsplit('_', 1)
            newArchivePath = "%s_%s.%s" % (leftover, str(
                nbComments), RepoManager.TEST_RESULT_EXT)
            os.rename(completePath, "%s/%s" % (self.testsPath, newArchivePath))
        except Exception as e:
            self.error("exception %s" % str(e))
            return (self.context.CODE_ERROR, archivePath,
                    newArchivePath, comments)
        return (self.context.CODE_OK, archivePath, newArchivePath, comments)

    def delComments(self, archivePath):
        """
        Delete all comment on the archive gived in argument
        """
        self.trace("remove all comments from test result")
        try:
            # prepare path
            completePath = "%s/%s" % (self.testsPath, archivePath)
            completePath = os.path.normpath(completePath)

            # to avoid error, the server try to find the good file by himself
            # just take the name of the name and the replay id to find the test
            # automaticly
            trxPath, rightover = archivePath.rsplit('/', 1)
            trxfile = rightover.rsplit('_', 1)[0]

            for f in os.listdir("%s/%s" % (self.testsPath, trxPath)):
                if f.startswith(trxfile) and f.endswith(
                        RepoManager.TEST_RESULT_EXT):
                    completePath = "%s/%s/%s" % (self.testsPath, trxPath, f)
                    completePath = os.path.normpath(completePath)

            # read test result
            dataModel = TestResult.DataModel()
            trLoaded = dataModel.load(absPath=completePath)
            if not trLoaded:
                raise Exception("unable to load test result")

            # delete all comments in the model
            dataModel.delComments()

            # save test result
            f = open(completePath, 'wb')
            raw_data = dataModel.toXml()

            if sys.version_info > (3,):
                raw_data = bytes(raw_data, "utf8")

            f.write(zlib.compress(raw_data))
            f.close()

            # rename file to update the number of comment in filename
            nbComments = 0
            leftover, _ = archivePath.rsplit('_', 1)
            newArchivePath = "%s_%s.%s" % (leftover, str(
                nbComments), RepoManager.TEST_RESULT_EXT)
            os.rename(completePath, "%s/%s" % (self.testsPath, newArchivePath))

        except Exception as e:
            self.error("exception %s" % str(e))
            return (self.context.CODE_ERROR, archivePath)
        return (self.context.CODE_OK, archivePath)

    def createResultLog(self, testsPath, logPath, logName, logData):
        """
        Create result log
        """
        self.trace("create result log=%s to %s" % (logName, logPath))
        try:
            # write the file
            f = open("%s/%s/%s" % (testsPath, logPath, logName), 'wb')
            f.write(base64.b64decode(logData))
            f.close()

            # notify all users
            size_ = os.path.getsize("%s/%s/%s" % (testsPath, logPath, logName))

            # \1\2019-07-26\2019-07-26_18-31-21.1e05661b-c1a8-429c-aeee-d7646b
            # 87814f.MDNfMDAxIENyZWF0ZSBnb29nbGUgYWNjb3VudCBhbmQgY2FuY2Vs.admin
            _, projectId, mainPathTozip, subPathTozip = logPath.split(os.sep)

            if Settings.getInt('Notifications', 'archives'):
                m = [{"type": "folder", "name": mainPathTozip, "project": "%s" % projectId,
                      "content": [{"type": "folder",
                                   "name": subPathTozip,
                                   "project": "%s" % projectId,
                                   "content": [{"project": "%s" % projectId,
                                                "type": "file",
                                                "name": logName,
                                                'size': str(size_)}]
                                   }
                                  ]
                      }]
                notif = {}
                notif['archive'] = m
                notif['stats-repo-archives'] = {'nb-zip': 1, 'nb-trx': 0, 'nb-tot': 1,
                                                'mb-used': self.getSizeRepoV2(folder=self.testsPath),
                                                'mb-free': self.freeSpace(p=self.testsPath)}
                data = ('archive', (None, notif))
                ESI.instance().notifyByUserAndProject(body=data,
                                                      admin=True,
                                                      monitor=False,
                                                      tester=True,
                                                      projectId="%s" % projectId)

        except Exception as e:
            self.error("unable to create result log: %s" % e)
            return False
        return True

    def findTrByID(self, projectId, testId):
        """
        Find a test result according the test id (md5)

        test id = md5
        """
        ret = ''

        path_prj = "%s/%s/" % (self.testsPath, projectId)
        path_prj = os.path.normpath(path_prj)

        for entry in list(scandir.scandir(path_prj)):
            if entry.is_dir(follow_symlinks=False):
                for entry2 in list(scandir.scandir(entry.path)):
                    fullPath = entry2.path
                    relativePath = fullPath.split(self.testsPath)[1]

                    # compute the md5
                    hash = hashlib.md5()
                    hash.update(relativePath)

                    if hash.hexdigest() == testId:
                        ret = relativePath
                        break
        return ret

    def findTrInCache(self, projectId, testId, returnProject=True):
        """
        Find a test result according the test id (md5) and project id

        test id = md5
        """
        self.trace("Find testresult %s in project %s" % (testId, projectId))

        ret = self.context.CODE_NOT_FOUND
        tr = ''
        if int(projectId) in self.cacheUuids:
            testUuids = self.cacheUuids[int(projectId)]
            if testId in testUuids:
                ret = self.context.CODE_OK
                tr = testUuids[testId]
                if not returnProject:
                    if platform.system() == "Windows":
                        tr = tr.split("\\", 1)[1]
                    else:
                        tr = tr.split("/", 1)[1]

        return (ret, tr)

    def cacheUuid(self, taskId, testPath):
        """
        """
        # extract projet
        try:
            if testPath.startswith("/"):
                testPath = testPath[1:]

            if platform.system() == "Windows":
                prjId = testPath.split("\\", 1)[0]
            else:
                prjId = testPath.split("/", 1)[0]
            prjId = int(prjId)

            # save in cache
            if int(prjId) in self.cacheUuids:
                self.cacheUuids[int(prjId)][taskId] = testPath
            else:
                self.cacheUuids[int(prjId)] = {taskId: testPath}
        except Exception as e:
            self.error("unable to add testid in cache: %s" % e)

    def cachingUuid(self):
        """
        """
        self.trace("caching all testsresults by uuid")
        for entry in list(scandir.scandir("%s/" % (self.testsPath))):
            if entry.is_dir(follow_symlinks=False):  # project
                for entry2 in list(scandir.scandir(entry.path)):
                    if entry2.is_dir(follow_symlinks=False):  # date
                        for entry3 in list(scandir.scandir(entry2.path)):
                            if entry3.is_dir(
                                    follow_symlinks=False):  # test folder
                                fullPath = entry3.path
                                relativePath = fullPath.split(
                                    self.testsPath)[1]
                                try:
                                    f = open("%s/TASKID" % fullPath, 'r')
                                    taskId = f.read().strip()
                                    taskId = taskId.lower()
                                    f.close()

                                    self.cacheUuid(taskId=taskId,
                                                   testPath=relativePath)
                                except Exception:
                                    pass

    def getTrDescription(self, trPath):
        """
        Get the state of the test result passed on argument
        """
        description = {}

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return description
        else:
            try:
                f = open("%s/DESCRIPTION" % fullPath, 'r')
                description_raw = f.read()
                description = json.loads(description_raw)
                f.close()
            except Exception as e:
                self.error("unable to read test description: %s" % e)
        return description

    def getTrState(self, trPath):
        """
        Get the state of the test result passed on argument
        """
        state = ''

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return "not-running"
        else:
            try:
                f = open("%s/STATE" % fullPath, 'r')
                state = f.read().strip()
                f.close()
                return state.lower()
            except Exception:
                return "not-running"
        return state

    def getTrLogs(self, trPath, log_index=0):
        """
        Get the logs of the test result passed on argument
        """
        logs = ''
        index = 0

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return (logs, index)
        else:
            try:
                fh = open("%s/LOGS" % fullPath, 'r')
                fh.seek(log_index)
                logs = fh.read()
                index = fh.tell()
                fh.close()
            except Exception:
                return (logs,index)
        return (logs, index)

    def getTrEndResult(self, trPath):
        """
        Get the result of the test result passed on argument
        """
        result = ''

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return None
        else:
            try:
                f = open("%s/RESULT" % fullPath, 'r')
                result = f.read().strip()
                f.close()
                return result.lower()
            except Exception:
                return None
        return result

    def getTrProgress(self, trPath):
        """
        Get the progress of the test result passed on argument

        """
        p = {"percent": 0, "total": 0}

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return p
        else:
            try:
                f = open("%s/PROGRESS" % fullPath, 'r')
                p_str = f.read().strip()
                p = json.loads(p_str)
                f.close()
            except Exception:
                return p
        return p

    def getTrReportByExtension(self, trPath, replayId=0, trExt="tbrp"):
        """
        Get the report of the test result passed on argument

        review:  trp (html) / tbrp (html)  / trpx (xml)
        verdict: trv (csv) / tvrx (xml)
        design: trd (html) / tdsx (xml)
        """
        report = ''

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return(self.context.CODE_NOT_FOUND, report)
        else:
            try:
                for entry in list(scandir.scandir(fullPath)):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith("_%s.%s" % (replayId, trExt)):
                            f = open("%s/%s" % (fullPath, entry.name), 'r')
                            report = f.read()
                            f.close()
                            break
            except Exception as e:
                self.error(
                    "unable to get the first one html test basic report: %s" %
                    e)
                return (self.context.CODE_ERROR, report)
        return (self.context.CODE_OK, report)

    def getTrName(self, trPath, replayId=0, withExt=True, matchExt="trx"):
        """
        xxxx
        """
        trName = None

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return(self.context.CODE_NOT_FOUND, trName)
        else:
            try:
                for entry in list(scandir.scandir(fullPath)):
                    if not entry.is_dir(follow_symlinks=False):
                        if re.match(r".*_%s_(PASS|FAIL|UNDEFINED)_\d+\.%s$" %
                                    (replayId, matchExt), entry.name):
                            trName = entry.name
                            if not withExt:
                                trName = trName.rsplit(".", 1)[0]
                            break
            except Exception as e:
                self.error("unable to find trx: %s" % e)
                return (self.context.CODE_ERROR, trName)

            if trName is None:
                return(self.context.CODE_NOT_FOUND, trName)
        return (self.context.CODE_OK, trName)

    def getTrLogName(self, trPath, replayId=0, withExt=True, matchExt="log"):
        """
        xxxx
        """
        trName = None

        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        res = os.path.exists(fullPath)
        if not res:
            return(self.context.CODE_NOT_FOUND, trName)
        else:
            try:
                for entry in list(scandir.scandir(fullPath)):
                    if not entry.is_dir(follow_symlinks=False):
                        if re.match(r".*_%s\.%s$" %
                                    (replayId, matchExt), entry.name):
                            trName = entry.name
                            if not withExt:
                                trName = trName.rsplit(".", 1)[0]
                            break
            except Exception as e:
                self.error("unable to find log file: %s" % e)
                return (self.context.CODE_ERROR, trName)

            if trName is None:
                return(self.context.CODE_NOT_FOUND, trName)
        return (self.context.CODE_OK, trName)

    def getListingBasic(self, project_id=1):
        """
        """
        listing = []
        initial_path = "%s/" % (self.testsPath)
        
        if not os.path.exists("%s/%s" % (self.testsPath, project_id)):
            return listing
        
        for entry in reversed(list(scandir.scandir(
                "%s/%s" % (self.testsPath, project_id)))):
            if entry.is_dir(follow_symlinks=False):  # date
                listing.extend(self.__getListingBasic(test_path=entry.path,
                                                      initial_path=initial_path,
                                                      project_id=project_id))
        return listing

    def __getListingBasic(self, test_path, initial_path, project_id):
        """
        """
        listing = []
        for entry in reversed(list(scandir.scandir(test_path))):
            if entry.is_dir(follow_symlinks=False):

                # compute the test id (md5 hash)
                real_path = "/%s" % entry.path.split(initial_path)[1]
                real_path = os.path.normpath(real_path)
                
                # example real path: "/1/2016-04-29/2016-04-29_16-14-
                # 24.293494.TmV3cy9yZXN0X2FwaQ==.admin"
                # extract the username, testname, date
                _timestamp, _, _, _user = real_path.rsplit(".")
                _, _, testdate, _testtime = pathlib.Path(_timestamp).parts
                _, testtime = _testtime.split("_")

                testdate = testdate.replace("-", "/")
                testtime = testtime.replace("-", ":")

                with open("%s/TESTPATH" % entry.path, "r") as fh:
                    testpath = fh.read()

                with open("%s/TASKID" % entry.path, "r") as fh:
                    testid = fh.read()
                    
                testduration = 0
                if os.path.exists( "%s/DURATION" % entry.path):
                    with open("%s/DURATION" % entry.path, "r") as fh:
                        testduration = fh.read()

                run_state = "UNKNOWN"
                if os.path.exists( "%s/RESULT" % entry.path):
                    with open("%s/RESULT" % entry.path, "r") as fh:
                        run_state = fh.read()
                else:
                    with open("%s/STATE" % entry.path, "r") as fh:
                        run_state = fh.read()

                listing.append({'script': testpath,
                                'id': testid,
                                'user': _user,
                                'datetime': "%s %s" % (testdate, testtime),
                                'duration': testduration,
                                'state': run_state})
        return listing

    def getListingFilter(self, projectId=1, dateFilter=None, timeFilter=None):
        """
        Deprecated, will be removed in future
        """
        listing = []
        initialPath = "%s/" % (self.testsPath)
        for entry in reversed(list(scandir.scandir(
                "%s/%s" % (self.testsPath, projectId)))):
            if entry.is_dir(follow_symlinks=False):  # date
                listing.extend(self.__getListingFilter(testPath=entry.path,
                                                      initialPath=initialPath,
                                                      projectId=projectId,
                                                      dateFilter=dateFilter,
                                                      timeFilter=timeFilter)
                               )
        return listing

    def __getListingFilter(self, testPath, initialPath,
                          projectId, dateFilter, timeFilter):
        """
        """
        listing = []
        for entry in reversed(list(scandir.scandir(testPath))):
            if entry.is_dir(follow_symlinks=False):

                # compute the test id (md5 hash)
                realPath = "/%s" % entry.path.split(initialPath)[1]
                hash = hashlib.md5()
                if sys.version_info < (3,):
                    hash.update(realPath)
                else:
                    hash.update(realPath.encode('utf-8'))

                # example real path: "/1/2016-04-29/2016-04-29_16-14-
                # 24.293494.TmV3cy9yZXN0X2FwaQ==.admin"
                # extract the username, testname, date
                _timestamp, _, _testname, _ = realPath.rsplit(".")
                _, _, testdate, _testtime = _timestamp.split("/")
                _, testtime = _testtime.split("_")

                if sys.version_info < (3,):
                    testname = base64.b64decode(_testname)
                else:
                    testname = base64.b64decode(_testname)
                    testname = testname.decode("utf8")

                # append to the list
                appendTest = False
                if dateFilter is not None and timeFilter is not None:
                    if re.match(re.compile(dateFilter, re.S), testdate) is not None and \
                            re.match(re.compile(timeFilter, re.S), testtime) is not None:
                        appendTest = True
                else:
                    if dateFilter is not None:
                        if re.match(re.compile(dateFilter, re.S), testdate):
                            appendTest = True
                    if timeFilter is not None:
                        if re.match(re.compile(timeFilter, re.S),
                                    testtime) is not None:
                            appendTest = True
                    if dateFilter is None and timeFilter is None:
                        appendTest = True

                if appendTest:
                    listing.append({'file': "/%s/%s/%s" % (testdate,
                                                           testtime,
                                                           testname),
                                    'test-id': hash.hexdigest()})
        return listing

    def getTrResume(self, trPath, replayId=0):
        """
        """
        self.trace("get resume from testresult")

        resume = {}
        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        # check if the test result path exists
        res = os.path.exists(fullPath)
        if not res:
            return(self.context.CODE_NOT_FOUND, resume)

        # find the trx file
        trxFile = None
        for entry in list(scandir.scandir(fullPath)):
            if not entry.is_dir(follow_symlinks=False):
                # if entry.name.endswith("_%s.trx" % replayId) :
                if re.match(r".*_%s_(PASS|FAIL|UNDEFINED)_\d+\.trx$" %
                            replayId, entry.name):
                    trxFile = entry.name
                    break
        if trxFile is None:
            return (self.context.CODE_NOT_FOUND, resume)

        # open the trx file
        tr = TestResult.DataModel()
        res = tr.load(absPath="%s/%s" % (fullPath, trxFile))
        if not res:
            self.error("unable to load testresult")
            return (self.context.CODE_ERROR, resume)

        # decode the file
        try:
            f = cStringIO.StringIO(tr.testresult)
        except Exception as e:
            self.error("unable to convert testresult: %s" % e)
            return (self.context.CODE_ERROR, resume)

        try:
            resume = {
                'nb-total': 0, 'nb-info': 0,
                'nb-error': 0, 'nb-warning': 0, 'nb-debug': 0,
                'nb-timer': 0, 'nb-step': 0,
                'nb-adapter': 0, 'nb-match': 0, 'nb-section': 0,
                'nb-others': 0, 'nb-step-failed': 0,
                'nb-step-passed': 0, 'errors': []
            }
            for line in f.readlines():
                resume["nb-total"] += 1

                line_decoded = base64.b64decode(line)
                event = cPickle.loads(line_decoded)

                if "level" in event:
                    if event["level"] == "info":
                        resume["nb-info"] += 1
                    if event["level"] == "warning":
                        resume["nb-warning"] += 1
                    if event["level"] == "error":
                        resume["nb-error"] += 1
                        resume["errors"].append(event)

                    if event["level"] == "debug":
                        resume["nb-debug"] += 1

                    if event["level"] in ["send", "received"]:
                        resume["nb-adapter"] += 1
                    if event["level"].startswith("step"):
                        resume["nb-step"] += 1
                    if event["level"].startswith("step-failed"):
                        resume["nb-step-failed"] += 1
                    if event["level"].startswith("step-passed"):
                        resume["nb-step-passed"] += 1
                    if event["level"].startswith("timer"):
                        resume["nb-timer"] += 1
                    if event["level"].startswith("match"):
                        resume["nb-match"] += 1
                    if event["level"] == "section":
                        resume["nb-section"] += 1
                else:
                    resume["nb-others"] += 1

                del event
            del f
        except Exception as e:
            self.error("unable to get resume: %s" % e)
            return (self.context.CODE_ERROR, resume)

        return (self.context.CODE_OK, resume)

    def getTrComments(self, trPath, replayId=0):
        """
        """
        self.trace("get comments from testresult")

        comments = []
        fullPath = "%s/%s/" % (self.testsPath, trPath)
        fullPath = os.path.normpath(fullPath)

        # check if the test result path exists
        res = os.path.exists(fullPath)
        if not res:
            return(self.context.CODE_NOT_FOUND, comments)

        # find the trx file
        trxFile = None
        for entry in list(scandir.scandir(fullPath)):
            if not entry.is_dir(follow_symlinks=False):
                # if entry.name.endswith("_%s.trx" % replayId) :
                if re.match(r".*_%s_(PASS|FAIL|UNDEFINED)_\d+\.trx$" %
                            replayId, entry.name):
                    trxFile = entry.name
                    break
        if trxFile is None:
            return (self.context.CODE_NOT_FOUND, comments)

        # open the trx file
        tr = TestResult.DataModel()
        res = tr.load(absPath="%s/%s" % (fullPath, trxFile))
        if not res:
            self.error("unable to load testresult")
            return (self.context.CODE_ERROR, comments)

        # and get comments properties
        try:
            comments = tr.properties['properties']['comments']
            if isinstance(comments, dict):
                if isinstance(comments['comment'], list):
                    comments = comments['comment']
                else:
                    comments = [comments['comment']]
        except Exception as e:
            self.error("unable to get comments: %s" % e)
            return (self.context.CODE_ERROR, comments)

        return (self.context.CODE_OK, comments)


RepoArchivesMng = None


def instance():
    """
    Returns the singleton
    """
    return RepoArchivesMng


def initialize(context):
    """
    Instance creation
    """
    global RepoArchivesMng
    RepoArchivesMng = RepoArchives(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global RepoArchivesMng
    if RepoArchivesMng:
        RepoArchivesMng = None
