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

import scandir
import os
import base64
import zlib
try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json
import shutil
import time
import scandir
import hashlib
import re
try:
    import cStringIO
except ImportError: # support python 3
    import io as cStringIO
try:
    import cPickle
except ImportError: # support python 3
    import pickle as cPickle

try:
    import RepoManager
    import EventServerInterface as ESI
    # import Context
    # import TaskManager
except ImportError: # python3 support
    from . import RepoManager
    from . import EventServerInterface as ESI
    # from . import Context
    # from . import TaskManager
    
from Libs import Scheduler, Settings, Logger
import Libs.FileModels.TestResult as TestResult

REPO_TYPE = 4

class RepoArchives(RepoManager.RepoManager, Logger.ClassLogger):
    """
    Repository Archives
    """
    def __init__(self, context, taskmgr):
        """
        Repository manager for archives files
        """
        RepoManager.RepoManager.__init__(self,
                                    pathRepo='%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) ),
                                    extensionsSupported = [ RepoManager.TEST_RESULT_EXT, RepoManager.TXT_EXT, 
                                                            RepoManager.CAP_EXT, RepoManager.ZIP_EXT,
                                                            RepoManager.PNG_EXT, RepoManager.JPG_EXT ],
                                    context=context)
        self.context = context
        self.taskmgr = taskmgr
        
        self.prefixLogs = "logs"
        self.prefixBackup = "backuparchives"
        self.destBackup = "%s%s" % ( Settings.getDirExec(), Settings.get( 'Paths', 'backups-archives' ) )
        
        self.cacheUuids = {}
        self.cachingUuid()
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="RAR - %s" % txt)

    def scheduleBackup(self):
        """
        Schedule an automatic backup on boot
        """
        self.trace('schedule archives tests')
        schedAt = Settings.get( 'Backups', 'archives-at' )
        backupName = Settings.get( 'Backups', 'archives-name' )

        # tests-at=6|1,00,00,00
        schedType = schedAt.split('|')[0]
        schedAt = schedAt.split('|')[1]
        if int(schedType) == Scheduler.SCHED_WEEKLY:
            d, h, m, s = schedAt.split(',')
            self.taskmgr.registerEvent(   id=None, author=None, name=None, weekly=( int(d), int(h), int(m), int(s) ), 
                                                    daily=None, hourly=None, everyMin=None, everySec=None, 
                                                    at=None, delay=None, timesec=None,
                                                    callback=self.createBackup, backupName=backupName )
        elif int(schedType) == Scheduler.SCHED_DAILY:
            h, m, s = schedAt.split(',')
            self.taskmgr.registerEvent(   id=None, author=None, name=None, weekly=None, 
                                                    daily=( int(h), int(m), int(s) ), hourly=None, 
                                                    everyMin=None, everySec=None, at=None, delay=None, timesec=None,
                                                    callback=self.createBackup, backupName=backupName )
        elif int(schedType) == Scheduler.SCHED_HOURLY:
            m, s = schedAt.split(',')
            self.taskmgr.registerEvent(   id=None, author=None, name=None, weekly=None, 
                                                    daily=None, hourly=( int(m), int(s) ), everyMin=None, 
                                                    everySec=None, at=None, delay=None, timesec=None,
                                                    callback=self.createBackup, backupName=backupName )
        else:
            self.error( 'schedulation type not supported: %s' % schedType )

    def deleteBackups(self):
        """
        Delete all backups from storage

        @return: response code
        @rtype: int
        """
        ret = self.context.CODE_ERROR
        try:
            # delete all files 
            files=os.listdir(self.destBackup)
            for x in files:
                fullpath=os.path.join(self.destBackup, x)
                if os.path.isfile(fullpath):
                    os.remove( fullpath )
                else:
                    shutil.rmtree( fullpath )
    
            # update all connected admin users
            notif = {}
            notif['repo-archives'] = {}
            data = ( 'archives', ( 'reset-backups', notif ) )   
            ESI.instance().notifyAll(body = data)
            return self.context.CODE_OK
        except OSError as e:
            self.trace( e )
            return self.context.CODE_FORBIDDEN
        except Exception as e:
            raise Exception( e )
            return ret
        return ret

    def getBackups(self, b64=False):
        """
        Returns the list of backups
    
        @return:
        @rtype: list
        """
        nb, nbf, backups, stats = self.getListingFilesV2(path=self.destBackup, extensionsSupported=[RepoManager.ZIP_EXT])
        backups_ret = self.encodeData(data=backups)
        return backups_ret

    def getTree(self, b64=False, fullTree=False, project=1):
        """
        Return tree of files
        """
        nb = Settings.getInt( 'WebServices', 'nb-archives' )
        if nb == -1: nb=None
        if nb == 0:
            return 0, 0, ''

        if fullTree:
            nb=None
        archs_ret = []
        stats = {}
        res = os.path.exists( "%s/%s" % (self.testsPath, project) )
        if not res:
            nb_archs, nb_archs_f, archs = (0, 0, [])
        else:
            nb_archs, nb_archs_f, archs, stats = self.getListingFilesV2(path="%s/%s" % (self.testsPath, project),
                                                                        nbDirs=nb, project=project, archiveMode=True)
        archs_ret = self.encodeData(data=archs)
        return nb_archs, nb_archs_f, archs_ret, stats

    def getLastEventIndex(self, pathEvents ):
        """
        Returns the last event index file

        @type  pathEvents:
        @param pathEvents:
    
        @return: backup index
        @rtype: int
        """
        lastIndex = 0
        for f in os.listdir( pathEvents ):
            if f.endswith('.log'):
                try:
                    idx = f.rsplit('_', 1)[1].split( ".log" )[0]
                except Exception as e:
                    continue
                if int(idx) > lastIndex:
                    lastIndex = idx
        return lastIndex 

    def getLastBackupIndex(self, pathBackups ):
        """
        Returns the last backup index

        @type  pathBackups:
        @param pathBackups:
    
        @return: backup index
        @rtype: int
        """
        indexes = []
        for f in os.listdir( pathBackups ):
            if f.startswith( self.prefixBackup ):
                if f.endswith('zip'):
                    try:
                        idx = f.split('_', 1)[0].split( self.prefixBackup )[1]
                    except Exception as e:
                        continue
                    if len(idx) > 0:
                        indexes.append( idx )
        indexes.sort()
        if len(indexes) == 0:
            lastIndex = 0
        else:
            lastIndex = int(indexes.pop()) + 1
        return lastIndex 

    def createBackup(self, backupName):
        """
        Create a backup of all archives

        @type  backupName:
        @param backupName:

        @return: response code
        @rtype: int     """
        ret = self.context.CODE_ERROR
        try:
            backupIndex = self.getLastBackupIndex( pathBackups=self.destBackup )
            backupDate = self.getTimestamp() 
            backupFilename = '%s%s_%s_%s' % ( self.prefixBackup, backupIndex, backupName, backupDate )
            self.trace( "backup adapters to %s/%s.zip" % (self.destBackup,backupFilename) )

            zipped = self.zipFolder(folderPath=self.testsPath, zipName="%s.zip" % backupFilename,
                                    zipPath=self.destBackup, ignoreExt=[], 
                                    includeExt=[ RepoManager.TEST_RESULT_EXT, RepoManager.ZIP_EXT, 
                                                    RepoManager.PNG_EXT, RepoManager.JPG_EXT ])
            ret = zipped
            if zipped == self.context.CODE_OK:
                self.info( "backup adapters successfull: %s" % backupFilename )
                # now notify all connected admin users
                backupSize = os.path.getsize( "%s/%s.zip" % (self.destBackup, backupFilename) )
                notif = {}
                notif['repo-archives'] = {}
                notif['repo-archives']['backup'] = {'name': backupName, 'date': backupDate, 'size': backupSize, 'fullname': "%s.zip" % backupFilename }
                data = ( 'archives', ( 'add-backup' , notif) )  
                ESI.instance().notifyAllAdmins(body = data)
            else:
                self.error( "backup archives %s failed" % backupFilename )
        except Exception as e:
            raise Exception( "[createBackup] %s" % str(e) )
        return ret

    def createTrTmp(self, mainPath, subPath, testName, projectId=1):
        """
        Create a temporary test result file

        @type  mainPath:
        @param mainPath:

        @type  subPath:
        @param subPath:

        @type  testName:
        @param testName:
        """
        ret = {}
        try:
            pathTest = "%s/%s/%s/%s" % ( self.testsPath, projectId, mainPath, subPath )
            # begin fix issue 140 
            testName = testName.rsplit('/', 1)
            if len(testName) > 1: testName = testName[1]
            else: testName = testName[0]
            # end fix issue 140 
            indexFile = self.getLastEventIndex(pathEvents=pathTest)

            # read events from log
            f = open( "%s/%s_%s.log" % (pathTest, testName, indexFile), 'r')
            read_data = f.read()
            f.close()

            # create tmp file
            dataModel = TestResult.DataModel(testResult=read_data)
            trFileName = "%s.tmp" % testName
            f = open( "%s/%s" % (pathTest,trFileName), 'wb')
            raw_data = dataModel.toXml()
            f.write( zlib.compress( raw_data ) )
            f.close()
            
            # construct result
            ret['sub-path'] = subPath
            ret['main-path'] = mainPath
            ret['filename'] = trFileName
            ret['project-id'] = projectId
        except Exception as e:
            self.error( e )
        return ret

    def resetArchives(self, projectId=1):
        """
        Removes all archives from hard disk, no way to reverse this call

        @return: response code
        @rtype: int
        """
        ret =  self.context.CODE_ERROR
        try:
            # delete all folders and files
            ret = self.emptyRepo(projectId=projectId)
            
            # reset the cache
            del self.cacheUuids
            self.cacheUuids = {}
            
            # update all connected users
            if ret == self.context.CODE_OK:
                nb, nbf, backups, stats =self.getListingFilesV2(path="%s/%s/" % (self.testsPath, projectId), 
                                                                project=projectId )
                data = ( 'archive', ( 'reset', backups ) )  
                ESI.instance().notifyAll(body = data)
        except Exception as e:
            raise Exception( "[resetArchives] %s" % str(e) )
        return ret
    
    def getLastLogIndex(self, pathZip, projectId=1):
        """
        Returns the last log index
        zip file

        @type  pathZip:
        @param pathZip:

        @return: 
        @rtype: int
        """
        indexes = []
        for f in os.listdir('%s/%s/%s' % (self.testsPath, projectId, pathZip) ):
            if f.startswith( self.prefixLogs ):
                if f.endswith( RepoManager.ZIP_EXT ):
                    try:
                        idx = f.split('_', 1)[0].split( self.prefixLogs )[1]
                    except Exception as e:
                        continue
                    if len(idx) > 0:
                        indexes.append( idx )
        indexes.sort()
        if len(indexes) == 0:
            lastIndex = 0
        else:
            lastIndex = int(indexes.pop()) + 1
        return lastIndex 

    def createZip(self, mainPathTozip, subPathTozip, projectId=1):
        """
        Create a zip 

        @type  mainPathTozip:
        @param mainPathTozip:   

        @type  subPathTozip:
        @param subPathTozip:

        @return: response code
        @rtype: int
        """
        ret = self.context.CODE_ERROR
        pathTozip = '%s/%s' % (mainPathTozip,subPathTozip)
        try:
            timeArch, milliArch, testName, testUser = subPathTozip.split(".")
            fulltestNameDecoded = base64.b64decode(testName)
            logIndex = self.getLastLogIndex( pathZip=pathTozip, projectId=projectId )
            tmp = fulltestNameDecoded.rsplit('/', 1)
            if len(tmp) == 2:
                testNameDecoded = tmp[1]
            else:
                testNameDecoded = tmp[0]
            fileName = 'logs%s_%s_%s_0' % ( str(logIndex), testNameDecoded, self.getTimestamp())
            self.trace( "zip %s to %s.zip" % (pathTozip,fileName) )
            zipped = self.toZip(    file="%s/%s/%s" % (self.testsPath, projectId, pathTozip),
                                    filename="%s/%s/%s/%s.zip" % (self.testsPath, projectId, pathTozip, fileName),
                                    fileToExclude = [ '%s.zip' % fileName ],
                                    keepTree=False )
            ret = zipped
            if zipped == self.context.CODE_OK:
                self.info( "zip successfull: %s" % fileName )
                if Settings.getInt( 'Notifications', 'archives'):
                    # now notify all connected users
                    size_ = os.path.getsize( "%s/%s/%s/%s.zip" % (self.testsPath, projectId, pathTozip, fileName) )
                    m = [   {   "type": "folder", "name": mainPathTozip, "project": "%s" % projectId,
                                "content": [ {  "type": "folder", "name": subPathTozip, "project": "%s" % projectId,
                                "content": [ { "project": "%s" % projectId, "type": "file", "name": '%s.zip' % fileName, 'size': str(size_) } ]} ] }  ]
                    notif = {}
                    notif['archive'] = m 
                    notif['stats-repo-archives'] = {    'nb-zip':1, 'nb-trx':0, 'nb-tot': 1,
                                                    'mb-used': self.getSizeRepoV2(folder=self.testsPath),
                                                    'mb-free': self.freeSpace(p=self.testsPath) }

                    data = ( 'archive', ( None, notif) )    
                    ESI.instance().notifyByUserTypes(body = data, admin=True, leader=False, tester=True, developer=False)
            else:
                self.error( "zip %s failed" % pathTozip )
        except Exception as e:
            raise Exception( "[createZip] %s" % str(e) )
        return ret

    def addComment(self, archiveUser, archivePath, archivePost, archiveTimestamp):
        """
        Add comment to the archive gived on argument

        @type  archiveUser:
        @param archiveUser:

        @type  archivePath:
        @param archivePath:

        @type  archivePost:
        @param archivePost:

        @type  archiveTimestamp:
        @param archiveTimestamp:

        @return: 
        @rtype: 
        """
        comments = False
        newArchivePath = False
        try:
            # prepare path
            completePath = "%s/%s" % (self.testsPath, archivePath) 

            # to avoid error, the server try to find the good file by himself
            # just take the name of the name and the replay id to find the test automaticly
            trxPath, rightover = archivePath.rsplit('/',1)
            trxfile = rightover.rsplit('_', 1)[0]
            
            for f in os.listdir( "%s/%s" % (self.testsPath,trxPath) ):
                if f.startswith( trxfile ) and f.endswith( RepoManager.TEST_RESULT_EXT ):
                    completePath = "%s/%s/%s" % (self.testsPath, trxPath, f) 
            
            # read test result
            self.trace("read test result")
            dataModel = TestResult.DataModel()
            trLoaded = dataModel.load(absPath=completePath)
            if not trLoaded:
                raise Exception( "failed to load test result" )
            
            self.trace("add comment in data model")
            self.trace("username: %s" % archiveUser)
            self.trace("userpost: %s" % archivePost)
            self.trace("post timestamp: %s" % archiveTimestamp)
            archivePost = str(archivePost)
            postAdded = dataModel.addComment(user_name=archiveUser, 
                                             user_post=archivePost, 
                                             post_timestamp=archiveTimestamp)
            if postAdded is None:
                raise Exception( "failed to add comment in test result" )
            dataModel.properties['properties']['comments'] = postAdded
            comments = postAdded['comment']
            
            self.trace("save test result")
            f = open( completePath, 'wb')
            raw_data = dataModel.toXml()
            f.write( zlib.compress( raw_data ) )
            f.close()

            # rename file to update the number of comment in filename
            nbComments = len( postAdded['comment'] )
            leftover, righover = archivePath.rsplit('_', 1)
            newArchivePath = "%s_%s.%s" % (leftover, str(nbComments), RepoManager.TEST_RESULT_EXT)
            os.rename( completePath, "%s/%s" % (self.testsPath,newArchivePath) ) 
        except Exception as e:
            self.error( "[addComment] %s" % str(e) )
            return ( self.context.CODE_ERROR, archivePath, newArchivePath, comments )
        return ( self.context.CODE_OK, archivePath, newArchivePath , comments )

    def getComments(self, archivePath):
        """
        Returns all comments of the archive gived in argument

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        comments = []
        try:
            # prepare path
            completePath = "%s/%s" % (self.testsPath, archivePath) 

            # to avoid error, the server try to find the good file by himself
            # just take the name of the name and the replay id to find the test automaticly
            trxPath, rightover = archivePath.rsplit('/',1)
            trxfile = rightover.rsplit('_', 1)[0]
            
            for f in os.listdir( "%s/%s" % (self.testsPath,trxPath) ):
                if f.startswith( trxfile ) and f.endswith( RepoManager.TEST_RESULT_EXT ):
                    completePath = "%s/%s/%s" % (self.testsPath, trxPath, f) 

            # read test result
            dataModel = TestResult.DataModel()
            trLoaded = dataModel.load(absPath=completePath)
            if not trLoaded:
                raise Exception( "failed to load test result" )
            comments = dataModel.properties['properties']['comments']
            if isinstance(comments, dict):
                if isinstance( comments['comment'], list):
                    comments = comments['comment']
                else:
                    comments = [ comments['comment'] ]                  
            else:
                comments = []
    
        except Exception as e:
            self.error( "[addComment] %s" % str(e) )
            return ( self.context.CODE_ERROR, archivePath, comments )
        return ( self.context.CODE_OK, archivePath , comments )

    def delComments(self, archivePath):
        """
        Delete all comment on the archive gived in argument

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        try:
            # prepare path
            completePath = "%s/%s" % (self.testsPath, archivePath) 

            # to avoid error, the server try to find the good file by himself
            # just take the name of the name and the replay id to find the test automaticly
            trxPath, rightover = archivePath.rsplit('/',1)
            trxfile = rightover.rsplit('_', 1)[0]
            
            for f in os.listdir( "%s/%s" % (self.testsPath,trxPath) ):
                if f.startswith( trxfile ) and f.endswith( RepoManager.TEST_RESULT_EXT ):
                    completePath = "%s/%s/%s" % (self.testsPath, trxPath, f) 

            # read test result
            dataModel = TestResult.DataModel()
            trLoaded = dataModel.load(absPath=completePath)
            if not trLoaded:
                raise Exception( "failed to load test result" )
            
            # delete all comments in the model
            dataModel.delComments()

            # save test result
            f = open( completePath, 'wb')
            raw_data = dataModel.toXml()
            f.write( zlib.compress( raw_data ) )
            f.close()

            # rename file to update the number of comment in filename
            nbComments = 0
            leftover, righover = archivePath.rsplit('_', 1)
            newArchivePath = "%s_%s.%s" % (leftover, str(nbComments), RepoManager.TEST_RESULT_EXT)
            os.rename( completePath, "%s/%s" % (self.testsPath,newArchivePath) ) 

        except Exception as e:
            self.error( "[delComments] %s" % str(e) )
            return ( self.context.CODE_ERROR, archivePath )
        return ( self.context.CODE_OK, archivePath  )

    def getTestDesign(self, archivePath, archiveName, returnXml=False, projectId=1):
        """
        Returns the test result design

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        designs = ''
        try:
            completePath = None
            for f in os.listdir( "%s/%s/%s" % (self.testsPath,projectId, archivePath) ):
                if returnXml:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_DESIGN_XML_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
                else:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_DESIGN_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
            if completePath is None:
                raise Exception('Test result design not found')
        except Exception as e:
            self.trace( str(e) )
            return ( self.context.CODE_NOT_FOUND, designs )
        else:
            try:
                try:
                    f = open( completePath , 'r'  )
                    raw_designs = f.read()
                    f.close()
                except Exception as e:
                    raise Exception( "open test result design failed: %s" % str(e) )
                else:
                    designs = self.zipb64(data=raw_designs)
            except Exception as e:
                self.error( str(e) )
                return ( self.context.CODE_ERROR, designs )
        return ( self.context.CODE_OK, designs )
        
    def getBasicTestReport(self, archivePath, archiveName,projectId=1):
        """
        Returns the basic test result report

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        reports = ''
        try:
            completePath = None
            for f in os.listdir( "%s/%s/%s" % (self.testsPath,projectId, archivePath) ):
                if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_BASIC_REPORT_EXT ):
                    completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                    break
            if completePath is None:
                raise Exception('Basic test result report not found')
        except Exception as e:
            self.trace( str(e) )
            return ( self.context.CODE_NOT_FOUND, reports )
        else:
            try:
                try:
                    f = open( completePath , 'r'  )
                    raw_reports = f.read()
                    f.close()
                except Exception as e:
                    raise Exception( "open basic test result report failed: %s" % str(e) )
                else:
                    reports = self.zipb64(data=raw_reports)
            except Exception as e:
                self.error( str(e) )
                return ( self.context.CODE_ERROR, reports )
        return ( self.context.CODE_OK, reports )
        
    def getTestReport(self, archivePath, archiveName, returnXml=False, projectId=1):
        """
        Returns the test result report

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        reports = ''
        try:
            completePath = None
            for f in os.listdir( "%s/%s/%s" % (self.testsPath,projectId, archivePath) ):
                if returnXml:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_REPORT_XML_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
                else:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_REPORT_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
            if completePath is None:
                raise Exception('Test result report not found')
        except Exception as e:
            self.trace( str(e) )
            return ( self.context.CODE_NOT_FOUND, reports )
        else:
            try:
                try:
                    f = open( completePath , 'r'  )
                    raw_reports = f.read()
                    f.close()
                except Exception as e:
                    raise Exception( "open test result report failed: %s" % str(e) )
                else:
                    reports = self.zipb64(data=raw_reports)
            except Exception as e:
                self.error( str(e) )
                return ( self.context.CODE_ERROR, reports )
        return ( self.context.CODE_OK, reports )

    def getTestVerdict(self, archivePath, archiveName, returnXml=False, projectId=1):
        """
        Returns the test result csv

        @type  archivePath:
        @param archivePath:

        @return: 
        @rtype: 
        """
        verdict = ''
        try:
            completePath = None
            for f in os.listdir( "%s/%s/%s" % (self.testsPath, projectId, archivePath) ):
                if returnXml:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_VERDICT_XML_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
                else:
                    if f.startswith( archiveName ) and f.endswith( RepoManager.TEST_RESULT_VERDICT_EXT ):
                        completePath = "%s/%s/%s/%s" % (self.testsPath, projectId, archivePath, f) 
                        break
            if completePath is None:
                raise Exception('Test result verdict not found')
        except Exception as e:
            self.trace( str(e) )
            return ( self.context.CODE_NOT_FOUND, verdict )
        else:
            try:
                try:
                    f = open( completePath , 'r'  )
                    raw_verdict = f.read()
                    f.close()
                except Exception as e:
                    raise Exception( "open test result verdict failed: %s" % str(e) )
                else:
                    verdict = self.zipb64(data=raw_verdict)
            except Exception as e:
                self.error( str(e) )
                return ( self.context.CODE_ERROR, verdict )
        return ( self.context.CODE_OK, verdict )

    def zipb64(self, data):
        """
        """
        try: 
            zipped = zlib.compress(data)
        except Exception as e:
            raise Exception( "Unable to compress data: %s" % str(e) )
        else:
            try: 
                encoded = base64.b64encode(zipped)
            except Exception as e:
                raise Exception( "Unable to encode data in base 64: %s" % str(e) )
        return encoded
        
    def createResultLog(self, testsPath, logPath, logName, logData ):
        """
        Create result log
        """
        self.trace("create result log=%s to %s" % (logName,logPath) )
        try:
            # write the file
            f = open( "%s/%s/%s" %(testsPath, logPath, logName), 'wb')
            f.write(logData)
            f.close()
            
            # notify all users
            size_ = os.path.getsize( "%s/%s/%s" %(testsPath, logPath, logName) )
            # extract project id
            if logPath.startswith('/'): logPath = logPath[1:]
            tmp = logPath.split('/', 1)
            projectId = tmp[0]
            tmp = tmp[1].split('/', 1)
            mainPathTozip= tmp[0]
            subPathTozip = tmp[1]
            if Settings.getInt( 'Notifications', 'archives'):
                m = [   {   "type": "folder", "name": mainPathTozip, "project": "%s" % projectId,
                            "content": [ {  "type": "folder", "name": subPathTozip, "project": "%s" % projectId,
                            "content": [ { "project": "%s" % projectId, "type": "file", "name": logName, 'size': str(size_) } ]} ] }  ]
                notif = {}
                notif['archive'] = m 
                notif['stats-repo-archives'] = {    'nb-zip':1, 'nb-trx':0, 'nb-tot': 1,
                                                'mb-used': self.getSizeRepoV2(folder=self.testsPath),
                                                'mb-free': self.freeSpace(p=self.testsPath) }
                data = ( 'archive', ( None, notif) )    
                ESI.instance().notifyByUserAndProject(body = data, admin=True, leader=False, tester=True, 
                                        developer=False, projectId="%s" % projectId)
        
        except Exception as e:
            self.error("unable to create result log: %s" % e )
            return False
        return True
      
    def findTrByID(self, projectId, testId):
        """
        Find a test result according the test id (md5)
        
        test id = md5
        """
        ret = ''
        for entry in list(scandir.scandir( "%s/%s/" % (self.testsPath, projectId) )):
            if entry.is_dir(follow_symlinks=False):
                for entry2 in list(scandir.scandir( entry.path )) :
                    fullPath = entry2.path
                    relativePath = fullPath.split(self.testsPath)[1]

                    # compute the md5
                    hash =  hashlib.md5()
                    hash.update( relativePath )

                    if hash.hexdigest() == testId:
                        ret = relativePath
                        break
        return ret
      
    def findTrInCache(self, projectId, testId):
        """
        Find a test result according the test id (md5) and project id
        
        test id = md5
        """
        ret = self.context.CODE_NOT_FOUND
        tr = ''

        if int(projectId) in self.cacheUuids:
            testUuids = self.cacheUuids[int(projectId)]
            if testId in testUuids:
                ret = self.context.CODE_OK
                tr = testUuids[testId]

        return (ret, tr)
    
    def cacheUuid(self, taskId, testPath):
        """
        """
        # extract projet
        prjId = testPath.split("/", 1)[0]
        prjId = int(prjId)
        
        # save in cache
        if int(prjId) in self.cacheUuids:
            self.cacheUuids[int(prjId)][taskId] = testPath
        else:
            self.cacheUuids[int(prjId)] = { taskId: testPath }

    def cachingUuid(self):
        """
        """
        self.trace("caching all testsresults by uuid")
        for entry in list(scandir.scandir( "%s/" % (self.testsPath) )):
            if entry.is_dir(follow_symlinks=False): # project
                for entry2 in list(scandir.scandir( entry.path )) :
                    if entry2.is_dir(follow_symlinks=False): # date
                        for entry3 in list(scandir.scandir( entry2.path )) :
                            if entry3.is_dir(follow_symlinks=False): # test folder
                                fullPath = entry3.path
                                relativePath = fullPath.split(self.testsPath)[1]
                                try:
                                    f = open( "%s/TASKID" % fullPath, 'r' )
                                    taskId = f.read().strip()
                                    taskId = taskId.lower()
                                    f.close()

                                    self.cacheUuid(taskId=taskId, testPath=relativePath)
                                except Exception as e:
                                    pass
        
    def getTrDescription(self, trPath):
        """
        Get the state of the test result passed on argument
        
        """
        description = {}
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return description
        else:
            try:
                f = open( "%s/DESCRIPTION" % fullPath, 'r' )
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
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return "not-running"
        else:
            try:
                f = open( "%s/STATE" % fullPath, 'r' )
                state = f.read().strip()
                f.close()
                return state.lower()
            except Exception as e:
                return "not-running"
        return state 
                    
    def getTrResult(self, trPath):
        """
        Get the result of the test result passed on argument
        
        """
        result = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return None
        else:
            try:
                f = open( "%s/RESULT" % fullPath, 'r' )
                result = f.read().strip()
                f.close()
                return result.lower()
            except Exception as e:
                return None
        return result 
                    
    def getTrProgress(self, trPath):
        """
        Get the progress of the test result passed on argument
        
        """      
        p = {"percent": 0, "total": 0}
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        res = os.path.exists( fullPath )
        if not res:
            return p
        else:
            try:
                f = open( "%s/PROGRESS" % fullPath, 'r' )
                p_str = f.read().strip()
                p = json.loads(p_str)
                f.close()
            except Exception as e:
                return p
        return p 
        
    def getTrBasicReport(self, trPath, replayId=0):
        """
        Get the report of the test result passed on argument
        
        """
        report = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return( self.context.CODE_NOT_FOUND, report )  
        else:
            try:
                for entry in list(scandir.scandir( fullPath )):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith( "_%s.tbrp" % replayId ) :
                            f = open( "%s/%s" %  (fullPath, entry.name) , 'r'  )
                            report_raw = f.read()
                            report = self.zipb64(data=report_raw)
                            f.close()
                            break
            except Exception as e:
                self.error("unable to get the first one html test basic report: %s" % e )
                return ( self.context.CODE_ERROR, report )
        return ( self.context.CODE_OK, report )  
        
    def getTrReport(self, trPath):
        """
        Get the report of the test result passed on argument
        
        """
        report = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return( self.context.CODE_NOT_FOUND, report )  
        else:
            try:
                for entry in list(scandir.scandir( fullPath )):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith( "_0.trp" ) :
                            f = open( "%s/%s" %  (fullPath, entry.name) , 'r'  )
                            report_raw = f.read()
                            report = self.zipb64(data=report_raw)
                            f.close()
                            break
            except Exception as e:
                self.error("unable to get html test report: %s" % e )
                return ( self.context.CODE_ERROR, report )
        return ( self.context.CODE_OK, report )  
        
    def getTrReportCsv(self, trPath):
        """
        Get the report as csv of the test result passed on argument
        
        """
        report = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return( self.context.CODE_NOT_FOUND, report )  
        else:
            try:
                for entry in list(scandir.scandir( fullPath )):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith( "_0.trv" ) :
                            f = open( "%s/%s" %  (fullPath, entry.name) , 'r'  )
                            report_raw = f.read()
                            report = self.zipb64(data=report_raw)
                            f.close()
                            break
            except Exception as e:
                self.error("unable to get csv test report: %s" % e )
                return ( self.context.CODE_ERROR, report )
        return ( self.context.CODE_OK, report )  
        
    def getTrEvents(self, trPath):
        """
        Get events of the test result passed on argument
        """
        events = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return( self.context.CODE_NOT_FOUND, events )  
        else:
            try:
                for entry in list(scandir.scandir( fullPath )):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith( "_0.trx" ) :
                            f = open( "%s/%s" %  (fullPath, entry.name) , 'r'  )
                            events_raw = f.read()
                            events = self.zipb64(data=events_raw)
                            f.close()
                            break
            except Exception as e:
                self.error("unable to get test events: %s" % e )
                return ( self.context.CODE_ERROR, events )
        return ( self.context.CODE_OK, events )  
        
    def getTrLogs(self, trPath):
        """
        Get logs of the test result passed on argument
        """
        logs = ''
        
        fullPath =  "%s/%s/" % (self.testsPath, trPath)
        
        res = os.path.exists( fullPath )
        if not res:
            return( self.context.CODE_NOT_FOUND, logs )  
        else:
            try:
                for entry in list(scandir.scandir( fullPath )):
                    if not entry.is_dir(follow_symlinks=False):
                        if entry.name.endswith( "_0.zip" ) and entry.name.startswith( "private_storage_" ) :
                            f = open( "%s/%s" %  (fullPath, entry.name) , 'r'  )
                            logs_raw = f.read()
                            logs = self.zipb64(data=logs_raw)
                            f.close()
                            break
            except Exception as e:
                self.error("unable to get test logs: %s" % e )
                return ( self.context.CODE_ERROR, logs )
        return ( self.context.CODE_OK, logs ) 
        
    def __getBasicListing(self, testPath, initialPath, projectId, dateFilter, timeFilter):
        """
        """
        listing = []
        for entry in reversed(list(scandir.scandir( testPath ) ) ):
            if entry.is_dir(follow_symlinks=False):
            
                # compute the test id (md5 hash)
                realPath = "/%s" % entry.path.split(initialPath)[1]
                hash =  hashlib.md5()
                hash.update( realPath )
                
                # example real path: "/1/2016-04-29/2016-04-29_16:14:24.293494.TmV3cy9yZXN0X2FwaQ==.admin"
                # extract the username, testname, date
                _timestamp, _, _testname, username = realPath.rsplit(".")
                _, _, testdate, _testtime = _timestamp.split("/")
                _, testtime = _testtime.split("_")
                testname = base64.b64decode(_testname)
                
                # append to the list
                appendTest = False
                if dateFilter is not None and timeFilter is not None:
                    #if dateFilter == testdate and timeFilter == testtime:
                    if re.match( re.compile( dateFilter, re.S), testdate ) is not None and \
                        re.match( re.compile( timeFilter, re.S), testtime ) is not None:
                        appendTest = True
                else:
                    if dateFilter is not None:
                        #if dateFilter == testdate: 
                        if re.match( re.compile( dateFilter, re.S), testdate ) :
                            appendTest = True
                    if timeFilter is not None:
                        #if timeFilter == testtime: 
                        if re.match( re.compile( timeFilter, re.S), testtime ) is not None:
                            appendTest = True
                    if dateFilter is None and timeFilter is None:    
                        appendTest = True
               
                if appendTest:
                    listing.append( { 'file': "/%s/%s/%s" % (testdate, testtime, testname) , 'test-id': hash.hexdigest() } )
        return listing
        
    def getBasicListing(self, projectId=1, dateFilter=None, timeFilter=None):
        """
        """
        listing = []
        initialPath = "%s/" % (self.testsPath)
        for entry in reversed(list(scandir.scandir( "%s/%s" % (self.testsPath, projectId) ) ) ) :
            if entry.is_dir(follow_symlinks=False): # date
                listing.extend( self.__getBasicListing(testPath=entry.path, 
                                                        initialPath=initialPath, 
                                                        projectId=projectId,
                                                        dateFilter=dateFilter, timeFilter=timeFilter) 
                               )
        return listing

    def getTrResume(self, trPath):
        """
        """
        resume = {}
        fullPath =  "%s/%s/" % (self.testsPath, trPath)

        # check if the test result path exists
        res = os.path.exists( fullPath )
        if not res: return( self.context.CODE_NOT_FOUND, resume )  

        # find the trx file
        trxFile = None
        for entry in list(scandir.scandir( fullPath )):
            if not entry.is_dir(follow_symlinks=False):
                if entry.name.endswith( "_0.trx" ) :
                    trxFile = entry.name
                    break
        if trxFile is None: return (self.context.CODE_NOT_FOUND, resume)

        # open the trx file
        tr = TestResult.DataModel()
        res = tr.load( absPath = "%s/%s" %  (fullPath, trxFile) )
        if not res:  return (self.context.CODE_ERROR, resume)
        
        # decode the file
        try:
            f = cStringIO.StringIO( tr.testresult )
        except Exception as e:
            return (self.context.CODE_ERROR, resume)
        
        try:
            resume = { 
                                'nb-total': 0, 'nb-info': 0, 'nb-error': 0, 'nb-warning': 0, 'nb-debug': 0,
                                'nb-timer': 0, 'nb-step': 0, 'nb-adapter': 0, 'nb-match': 0, 'nb-section': 0,
                                'nb-others': 0, 'nb-step-failed': 0, 'nb-step-passed': 0, 'errors': []
                               }
            for line in f.readlines():
                resume["nb-total"] += 1
                
                l = base64.b64decode(line)
                event = cPickle.loads( l )
                
                if "level" in event:
                    if event["level"] == "info": resume["nb-info"] += 1
                    if event["level"] == "warning": resume["nb-warning"] += 1
                    if event["level"] == "error": 
                        resume["nb-error"] += 1
                        resume["errors"].append( event )
                        
                    if event["level"] == "debug": resume["nb-debug"] += 1
                
                    if event["level"] in [ "send", "received" ]:  resume["nb-adapter"] += 1
                    if event["level"].startswith("step"): resume["nb-step"] += 1
                    if event["level"].startswith("step-failed"): resume["nb-step-failed"] += 1
                    if event["level"].startswith("step-passed"): resume["nb-step-passed"] += 1
                    if event["level"].startswith("timer"): resume["nb-timer"] += 1
                    if event["level"].startswith("match"): resume["nb-match"] += 1
                    if event["level"] == "section": resume["nb-section"] += 1
                else:
                    resume["nb-others"] += 1
        except Exception as e:
            return (self.context.CODE_ERROR, resume)
        
        return (self.context.CODE_OK, resume)
        
###############################
RepoArchivesMng = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return RepoArchivesMng

def initialize (context, taskmgr):
    """
    Instance creation
    """
    global RepoArchivesMng
    RepoArchivesMng = RepoArchives(context=context, taskmgr=taskmgr)

def finalize ():
    """
    Destruction of the singleton
    """
    global RepoArchivesMng
    if RepoArchivesMng:
        RepoArchivesMng = None