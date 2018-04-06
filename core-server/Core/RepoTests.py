#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

try:
    import MySQLdb
except ImportError: # python3 support
    import pymysql as MySQLdb
import os
import sys
import subprocess
import shutil
import zlib
import base64
import tarfile
import scandir
import copy
import json
import re

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
from Libs import Scheduler, Settings, Logger

try:
    import RepoManager
    import EventServerInterface as ESI
    import ProjectsManager
    import Common
    import DbManager
    import ProjectsManager
except ImportError:
    from . import RepoManager
    from . import EventServerInterface as ESI
    from . import ProjectsManager
    from . import Common
    from . import DbManager
    from . import ProjectsManager
    
import Libs.FileModels.TestPlan as TestPlan
import Libs.FileModels.TestUnit as TestUnit
import Libs.FileModels.TestAbstract as TestAbstract
import Libs.FileModels.TestSuite as TestSuite


REPO_TYPE = 0


def uniqid():
    """
    Return a unique id
    """
    from time import time
    return hex(int(time()*10000000))[2:]

    
TS_ENABLED				= "2"
TS_DISABLED				= "0"


class RepoTests(RepoManager.RepoManager, Logger.ClassLogger):
    """
    Tests repository class
    """
    def __init__(self, context, taskmgr):
        """
        Repository manager for tests files
        """
        RepoManager.RepoManager.__init__(self,
                                        pathRepo='%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tests' ) ),
                                        extensionsSupported = [ RepoManager.TEST_SUITE_EXT, RepoManager.TEST_PLAN_EXT, 
                                                                RepoManager.TEST_CONFIG_EXT, RepoManager.TEST_DATA_EXT,
                                                                RepoManager.TEST_UNIT_EXT, RepoManager.TEST_ABSTRACT_EXT, 
                                                                RepoManager.PNG_EXT, RepoManager.TEST_GLOBAL_EXT ],
                                       context=context)
                                       
        self.context=context
        self.taskmgr = taskmgr
        
        # list of files, used for statistics
        self.prefixBackup = "backuptests"
        self.destBackup = "%s%s" % ( Settings.getDirExec(), Settings.get( 'Paths', 'backups-tests' ) )
        self.embeddedPath = "%s/%s/%s" % (  Settings.getDirExec(),   
                                            Settings.get( 'Paths', 'packages' ),  
                                            Settings.get( 'Paths', 'samples' ) )

        # contains oldpath: newpath
        self.renameHistory = {}
        
        # Initialize the repository
        self.info( 'Deploying test samples...' )
        self.deploy()
        
        # cleanup all lock files on init
        self.cleanupLocks()

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="RPT - %s" % txt)

    def deploy(self):
        """
        Deploy
        """
        # Remove the folder on boot
        try:
            if os.path.exists( "%s/%s/%s/" % (self.testsPath, ProjectsManager.DEFAULT_PRJ_ID, Settings.get( 'Paths', 'samples' ) ) ):
                shutil.rmtree( "%s/%s/%s/" % (  self.testsPath, 
                                                ProjectsManager.DEFAULT_PRJ_ID, 
                                                Settings.get( 'Paths', 'samples' ) ) )
        except Exception as e:
            self.error( "pre install cleanup: %s" % str(e) )
        else:
            # Find the latest version to install
            pkgs = os.listdir( self.embeddedPath )
            latestPkg = (0,0,0)
            latestPkgName = None
            try:
                for pkg in pkgs:
                    # Example: Samples-1.2.0.tar.gz
                    ver = pkg.rsplit("-", 1)[1].split(".tar.gz")[0]
                    digits = map( int, ver.split(".") )
                    if tuple(digits) > latestPkg:
                        latestPkg = tuple(digits)
                        latestPkgName = pkg
            except Exception as e:
                self.error("pre install failed: %s" % str(e) )
            else:
                try:
                    DEVNULL = open(os.devnull, 'w')
                    __cmd__ = "%s xf %s/%s -C %s" % (Settings.get( 'Bin', 'tar' ), 
                                                     self.embeddedPath, 
                                                     latestPkgName, 
                                                     Settings.getDirExec())
                    ret = subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
                    if ret: raise Exception("unable to untar tests pkg")
                        
                except Exception as e:
                    self.error("Samples installation failed: %s" % str(e) )
                else:
                    self.info( "Samples %s deployed succesfully" % str(latestPkg) )

    def scheduleBackup(self):
        """
        Schedule an automatic backup on boot
        """
        self.trace('schedule backups tests')
        schedAt = Settings.get( 'Backups', 'tests-at' )
        backupName = Settings.get( 'Backups', 'tests-name' )

        # tests-at=6|1,00,00,00
        schedType = schedAt.split('|')[0]
        schedAt = schedAt.split('|')[1]
        if int(schedType) == Scheduler.SCHED_WEEKLY:
            d, h, m, s = schedAt.split(',')
            self.taskmgr.registerEvent( id=None, author=None, name=None, weekly=( int(d), int(h), int(m), int(s) ), 
                                        daily=None, hourly=None, everyMin=None, everySec=None, 
                                        at=None, delay=None, timesec=None,
                                        callback=self.createBackup, backupName=backupName )
        elif int(schedType) == Scheduler.SCHED_DAILY:
            h, m, s = schedAt.split(',')
            self.taskmgr.registerEvent( id=None, author=None, name=None, weekly=None, 
                                        daily=( int(h), int(m), int(s) ), hourly=None, 
                                        everyMin=None, everySec=None, at=None, delay=None, timesec=None,
                                        callback=self.createBackup, backupName=backupName )
        elif int(schedType) == Scheduler.SCHED_HOURLY:
            m, s = schedAt.split(',')
            self.taskmgr.registerEvent( id=None, author=None, name=None, weekly=None, 
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
            notif['repo-tests'] = {}
            data = ( 'repositories', ( 'reset', notif ) )   
            ESI.instance().notifyAll(body = data)
            return self.context.CODE_OK
        except OSError as e:
            self.trace( e )
            return self.context.CODE_FORBIDDEN
        except Exception as e:
            raise Exception( e )
            return ret
        return ret

    def getTree(self, b64=False, project=1):
        """
        Returns tree
        """
        return self.getListingFilesV2(path="%s/%s" % (self.testsPath, str(project)), 
                                      project=project, supportSnapshot=True  )

    def __getBasicListing(self, testPath, initialPath):
        """
        """
        listing = []
        for entry in list(scandir.scandir( testPath ) ):
            if not entry.is_dir(follow_symlinks=False):
                filePath = entry.path
                listing.append( filePath.split(initialPath)[1] )
            else:
                listing.extend( self.__getBasicListing(testPath=entry.path, initialPath=initialPath) )
        return listing
        
    def getBasicListing(self, projectId=1):
        """
        """
        listing = []
        initialPath = "%s/%s" % (self.testsPath, projectId)
        for entry in list(scandir.scandir( initialPath ) ) :
            if not entry.is_dir(follow_symlinks=False):
                filePath = entry.path
                listing.append( filePath.split(initialPath)[1] )
            else:
                listing.extend( self.__getBasicListing(testPath=entry.path, initialPath=initialPath) )
        return listing
        
    def getBackups(self, b64=False):
        """
        Returns the list of backups
    
        @return:
        @rtype: list
        """
        _, _, tests, _ = self.getListingFilesV2( path=self.destBackup, 
                                                        extensionsSupported=[RepoManager.ZIP_EXT] )
        return tests

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
                    idx = f.split('_', 1)[0].split( self.prefixBackup )[1]
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
        Create a backup of all tests

        @type  backupName:
        @param backupName:

        @return: response code
        @rtype: int
        """
        ret = self.context.CODE_ERROR
        try:
            backupIndex = self.getLastBackupIndex( pathBackups=self.destBackup )
            backupDate = self.getTimestamp()  
            backupFilename = '%s%s_%s_%s' % ( self.prefixBackup, backupIndex, backupName, backupDate)
            self.trace( "backup tests to %s/%s.zip" % (self.destBackup,backupFilename) ) 
            zipped = self.zipFolder(folderPath=self.testsPath, zipName="%s.zip" % backupFilename,
                                    zipPath=self.destBackup, ignoreExt=[ ])
            ret = zipped
            if zipped == self.context.CODE_OK:
                self.info( "backup tests successfull: %s" % backupFilename )
                # now notify all connected admin users 
                backupSize = os.path.getsize( "%s/%s.zip" % (self.destBackup, backupFilename) )
                notif = {}
                notif['repo-tests'] = {}
                notif['repo-tests']['backup'] = {   'name': backupName, 
                                                    'date': backupDate, 
                                                    'size': backupSize, 
                                                    'fullname': "%s.zip" % backupFilename }
                data = ( 'repositories', ( None, notif) )   
                ESI.instance().notifyAllAdmins(body = data)
            else:
                self.error( "backup tests %s failed" % backupFilename )
        except Exception as e:
            raise Exception( "[createBackup] %s" % str(e) )
        return ret

    def cleanupLocks(self):
        """
        Cleanup all lock files
        """
        ret = False
        self.trace('Cleanup all lock files for tests...')
        try:
            DEVNULL = open(os.devnull, 'w')
            sys.stdout.write( "Cleanup all lock files for tests...\n")
            __cmd__ = "%s/Scripts/unlock-tests.sh %s/Scripts/" % (Settings.getDirExec(), Settings.getDirExec())
            subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
            ret = True
        except Exception as e:
            self.error("unable to cleanup lock files for tests: %s" % e)
        
        sys.stdout.flush()
        
        return ret
        
    def addSnapshot(self, snapshotName, snapshotTimestamp, testPath, testPrjId):
        """
        Add snapshot
        """
        self.trace("adding snapshot Name=%s" % snapshotName )
        ret = self.context.CODE_OK
        try:
            # checking if the test exists in first
            res = os.path.exists( "%s/%s/%s" % (self.testsPath, testPrjId, testPath) )
            if not res: 
                self.error( "test not found: %s" % testPath )
                return self.context.CODE_NOT_FOUND
                
            # copy the file and create the snapshot
            snapName = base64.b64encode(snapshotName)

            self.trace("creating snapshot from source=/%s/%s" % (testPrjId, testPath) )
            shutil.copyfile( "%s/%s/%s" % (self.testsPath, testPrjId, testPath),
                             "%s/%s/%s.%s.snapshot" % (self.testsPath, testPrjId, testPath, snapName) )
            self.trace("snapshot created from source Name=%s" % testPath)
        except Exception as e:
            self.error( "unable to add snapshot: %s" % e )
            ret = self.context.CODE_ERROR
        return ret
        
    def deleteAllSnapshots(self, testPath, testPrjId, testName, testExt):
        """
        Delete all snapshots
        """
        self.trace("delete all snapshots Name=%s" % testPath )
        ret = self.context.CODE_OK
        try:
            # checking if the test exists in first
            res = os.path.exists( "%s/%s/%s" % (self.testsPath, testPrjId, testPath) )
            if not res: 
                self.error( "test not found: %s" % testPath )
                return self.context.CODE_NOT_FOUND
                
            # delete all snapshot according to the file name
            currentPath = testPath.rsplit( "%s.%s" % (testName, testExt) , 1)[0]
            self.trace("delete all snapshots, inspecting dir=%s/%s/%s" % (self.testsPath, testPrjId, currentPath) )
            for file in os.listdir( "%s/%s/%s" % (self.testsPath, testPrjId, currentPath) ):
                if file.endswith(".snapshot") and file.startswith( "%s.%s" % (testName, testExt) ):
                    snapPath = "%s/%s/%s/%s" % (self.testsPath, testPrjId, currentPath, file)
                    os.remove( snapPath )
            self.trace("all snapshots removed Name=%s" % testPath)        
        except Exception as e:
            self.error( "unable to delete all snapshots: %s" % e )
            ret = self.context.CODE_ERROR
        return ret
    
    def deleteSnapshot(self, snapshotName, snapshotPath, snapshotPrjId):
        """
        Delete snapshot
        """
        self.trace("delete snapshot Name=%s" % snapshotName )
        ret = self.context.CODE_OK
        try:
            snapPath = "%s/%s/%s/%s" % (self.testsPath, snapshotPrjId, snapshotPath, snapshotName)
            
            # checking if the snapshot exists in first
            res = os.path.exists( snapPath )
            if not res: 
                self.error( "snapshot not found: %s in %s" % (snapshotName,snapshotPath)  )
                return self.context.CODE_NOT_FOUND
            
            os.remove( snapPath )
            self.trace("snapshot removed Name=%s" % snapshotName)     
        except Exception as e:
            self.error( "unable to delete snapshot: %s" % e )
            ret = self.context.CODE_ERROR
        return ret
        
    def restoreSnapshot(self, snapshotName, snapshotPath, snapshotPrjId):
        """
        Restore snapshot
        """
        self.trace("restore snapshot Name=%s" % snapshotName )
        ret = self.context.CODE_OK
        try:
            snapPath = "%s/%s/%s/%s" % (self.testsPath, snapshotPrjId, snapshotPath, snapshotName)
            
            # checking if the snapshot exists in first
            res = os.path.exists( snapPath )
            if not res: 
                self.error( "snapshot not found: %s in %s" % (snapshotName,snapshotPath)  )
                return self.context.CODE_NOT_FOUND
            
            testName = snapshotName.rsplit(".snapshot", 1)[0].rsplit(".", 1)[0]
            destTest = "%s/%s/%s/%s" % (self.testsPath, snapshotPrjId, snapshotPath, testName)
            
            self.trace("restoring snapshot to dest=%s" % destTest )
            shutil.copyfile( snapPath, destTest )
            self.trace("snapshot restored to source Name=%s" % destTest)
        except Exception as e:
            self.error( "unable to restore snapshot: %s" % e )
            ret = self.context.CODE_ERROR
        return ret
        
    def setTestsWithDefault(self):
        """
        Set tests with defaults values (adapters and libraries)
        """
        self.trace("Set tests with default values")
        ret = self.context.CODE_OK
        try:
            for path, subdirs, files in os.walk(self.testsPath):
                for name in files:  
                    if name.endswith(RepoManager.TEST_PLAN_EXT) or name.endswith(RepoManager.TEST_GLOBAL_EXT) :
                        doc = TestPlan.DataModel()
                        res = doc.load( absPath = os.path.join(path, name) )
                        if res: 
                            for d in doc.properties['properties']['descriptions']['description']:
                                if d['key'] == 'adapters': d['value'] = Settings.get( 'Default', 'current-adapters' )
                                if d['key'] == 'libraries': d['value'] = Settings.get( 'Default', 'current-libraries' )
                            saved = doc.write(absPath = os.path.join(path, name) )
                            if not saved:
                                self.error("unable to save file tpx/tgx (%s)" % os.path.join(path, name))
                                
                    elif name.endswith(RepoManager.TEST_UNIT_EXT):
                        doc = TestUnit.DataModel()
                        res = doc.load( absPath = os.path.join(path, name) )
                        if res: 
                            for d in doc.properties['properties']['descriptions']['description']:
                                if d['key'] == 'adapters': d['value'] = Settings.get( 'Default', 'current-adapters' )
                                if d['key'] == 'libraries': d['value'] = Settings.get( 'Default', 'current-libraries' )
                            saved = doc.write(absPath = os.path.join(path, name) )
                            if not saved:
                                self.error("unable to save file tux (%s)" % os.path.join(path, name))
                                
                    elif name.endswith(RepoManager.TEST_ABSTRACT_EXT):
                        doc = TestAbstract.DataModel()
                        res = doc.load( absPath = os.path.join(path, name) )
                        if res: 
                            for d in doc.properties['properties']['descriptions']['description']:
                                if d['key'] == 'adapters': d['value'] = Settings.get( 'Default', 'current-adapters' )
                                if d['key'] == 'libraries': d['value'] = Settings.get( 'Default', 'current-libraries' )
                            saved = doc.write(absPath = os.path.join(path, name) )
                            if not saved:
                                self.error("unable to save file tax (%s)" % os.path.join(path, name))
                                
                    elif name.endswith(RepoManager.TEST_SUITE_EXT):
                        doc = TestSuite.DataModel()
                        res = doc.load( absPath = os.path.join(path, name) )
                        if res: 
                            for d in doc.properties['properties']['descriptions']['description']:
                                if d['key'] == 'adapters': d['value'] = Settings.get( 'Default', 'current-adapters' )
                                if d['key'] == 'libraries': d['value'] = Settings.get( 'Default', 'current-libraries' )
                            saved = doc.write(absPath = os.path.join(path, name) )
                            if not saved:
                                self.error("unable to save file tsx (%s)" % os.path.join(path, name))
                    else:
                        pass
                        
        except Exception as e:
            self.error( "unable to set tests with default: %s" % e )
            ret = self.context.CODE_ERROR
        return ret

    def addtf2tg(self, data_):
        """
        Add remote testplan, testsuites or testunit in the testglobal
        internal function

        @param data_:
        @type data_:
        """
        ret = ( self.context.CODE_OK, "")
        alltests = []
        # read each test files in data
        for ts in data_:
            # backward compatibility
            if 'alias' not in ts:
                ts['alias'] = ''
                
            # extract project info
            prjName = str(ts['file']).split(":", 1)[0]
            ts.update( { 'testproject': prjName } )
            
            # extract test name
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                filenameTs, fileExt = tmp[1].rsplit(".", 1)
            else:
                filenameTs, fileExt = tmp[0].rsplit(".", 1)
                
            # extract test path
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                testPath = "/%s" % tmp[0]
            else:
                testPath = "/"
            ts.update( { 'testpath': testPath } )
            
            if ts['type'] == "remote" and ts['enable'] == TS_DISABLED:
                ts.update( { 'path': filenameTs, 'depth': 1 } )
                alltests.append( ts )
                
            if ts['type'] == "remote" and ts['enable'] == TS_ENABLED:
                # extract the project name then the project id
                prjID = 0
                absPath = ''
                try:
                    prjName, absPath = ts['file'].split(':', 1)
                except Exception as e:
                    self.error("unable to extract project name: %s" % str(e) )
                    ret = ( self.context.CODE_NOT_FOUND, "ID=%s %s" % (ts['id'],ts['file'])  )
                    break   
                else:
                    prjID = ProjectsManager.instance().getProjectID(name=prjName)

                    # prepare data model according to the test extension
                    if absPath.endswith(RepoManager.TEST_SUITE_EXT):
                        doc = TestSuite.DataModel()
                    elif absPath.endswith(RepoManager.TEST_UNIT_EXT):
                        doc = TestUnit.DataModel()
                    elif absPath.endswith(RepoManager.TEST_ABSTRACT_EXT):
                        doc = TestAbstract.DataModel()
                    elif absPath.endswith(RepoManager.TEST_PLAN_EXT):
                        doc = TestPlan.DataModel()
                    else:
                        self.error("unknown test extension file: %s" % absPath )
                        ret = ( self.context.CODE_NOT_FOUND, "ID=%s %s" % (ts['id'],ts['file'])  )
                        break
                    
                    # load the data model
                    res = doc.load( absPath = "%s/%s/%s" % ( self.testsPath, prjID, absPath ) )
                    if not res:
                        ret = ( self.context.CODE_NOT_FOUND, absPath  )
                        break   
                    else:
                        # update/add test parameters with the main parameters of the test global
                        self.__updatetsparams( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                newParam=ts['properties']['inputs-parameters']['parameter'] )
                        self.__updatetsparams( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                newParam=ts['properties']['outputs-parameters']['parameter'] )
                        # fix in v11, properly dispatch agent keys                        
                        self.__updatetsparams( currentParam=doc.properties['properties']['agents']['agent'],
                                                newParam=ts['properties']['agents']['agent'] )
                        # end of fix
                        ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                        ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']
                        # fix in v11, properly dispatch agent keys
                        ts['properties']['agents'] = doc.properties['properties']['agents']
                        # end of fix
                        
                        if fileExt == RepoManager.TEST_SUITE_EXT:
                            ts.update( { 'test-definition': doc.testdef, 'test-execution': doc.testexec, 'path': filenameTs } )
                            alltests.append( ts )
                        elif fileExt == RepoManager.TEST_UNIT_EXT:
                            ts.update( { 'test-definition': doc.testdef, 'path': filenameTs } )
                            alltests.append( ts )
                        elif fileExt == RepoManager.TEST_ABSTRACT_EXT:
                            ts.update( { 'test-definition': doc.testdef, 'path': filenameTs } )
                            alltests.append( ts )
                        elif fileExt == RepoManager.TEST_PLAN_EXT:
                            self.trace('Reading sub test plan')
                            sortedTests = doc.getSorted()
                            subret, suberr = self.addtf2tp( data_=sortedTests, tpid=ts['id'] )
                            ret = (subret, suberr)
                            if subret != self.context.CODE_OK:
                                del sortedTests
                                break
                            else:
                                alias_ts = ts['alias']
                                # fix issue encode, ugly fix
                                try:
                                    alias_ts =  str(alias_ts)
                                except UnicodeEncodeError as e:
                                    pass
                                else:
                                    try:
                                        alias_ts = alias_ts.encode('utf8')
                                    except UnicodeDecodeError as e:
                                        alias_ts = alias_ts.decode('utf8')
                                # end of fix
                        
                                # add testplan separator
                                alltests.extend( [{'extension': 'tpx', 'separator': 'started', 'enable': "0" , 'depth': 1, 
                                                    'id': ts['id'], 'testname': filenameTs, 'parent': ts['parent'], 
                                                    'alias': alias_ts, 'properties': ts['properties'],
                                                    "testpath": ts['testpath'], "testproject": ts['testproject'] }] ) 
                                                    
                                # update all subtest with parameters from testplan
                                for i in xrange(len(sortedTests)):
                                    self.__updatetsparams( currentParam=sortedTests[i]['properties']['inputs-parameters']['parameter'],
                                                         newParam=ts['properties']['inputs-parameters']['parameter'] )
                                    self.__updatetsparams( currentParam=sortedTests[i]['properties']['outputs-parameters']['parameter'],
                                                         newParam=ts['properties']['outputs-parameters']['parameter'] )
                                    # fix in v11, properly dispatch agent keys    
                                    self.__updatetsparams( currentParam=sortedTests[i]['properties']['agents']['agent'],
                                                         newParam=ts['properties']['agents']['agent'] )
                                    # end of fix
                                self.trace('Read sub test plan finished')
                                
                                alltests.extend( sortedTests )
                                alltests.extend( [{ 'extension': 'tpx', 'separator': 'terminated',  
                                                    'enable': "0" , 'depth': 1, 
                                                    'id': ts['id'], 'testname': filenameTs, 
                                                    'parent': ts['parent'], 'alias': alias_ts }] )
        return ret + (alltests, )

    def addtf2tp(self, data_, tpid=0):
        """
        Add remote testsuites or testunit in the testplan
        Internal function

        @param data_:
        @type data_:
        """
        ret = (self.context.CODE_OK, "")
        for ts in data_:
            # extract project info
            prjName = str(ts['file']).split(":", 1)[0]
            ts.update( { 'testproject': prjName } )
            
            # extract test name
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                filenameTs, fileExt = tmp[1].rsplit(".", 1)
            else:
                filenameTs, fileExt = tmp[0].rsplit(".", 1)
           
            # extract test path
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                testPath = "/%s" % tmp[0]
            else:
                testPath = "/"
            ts.update( { 'testpath': testPath } )
            
            if ts['type'] == "remote" and ts['enable'] == TS_DISABLED:
                ts.update( { 'path': filenameTs, 'tpid': tpid } )
                # backward compatibility
                self.__fixAliasTp(ts=ts)
                        
            elif ts['type'] == "remote" and ts['enable'] == TS_ENABLED:
                prjID = 0
                absPath = ''
                try:
                    prjName, absPath = ts['file'].split(':', 1)
                except Exception as e:
                    self.error("unable to extract project name: %s" % str(e) )
                    ret = ( self.context.CODE_NOT_FOUND, "ID=%s %s" % (ts['id'],ts['file'])  )
                    break   
                else:
                    prjID = ProjectsManager.instance().getProjectID(name=prjName)
                    if absPath.endswith(RepoManager.TEST_SUITE_EXT):
                        doc = TestSuite.DataModel()
                    elif absPath.endswith(RepoManager.TEST_ABSTRACT_EXT):
                        doc = TestAbstract.DataModel()
                    else:
                        doc = TestUnit.DataModel()
                    res = doc.load( absPath = "%s/%s/%s" % ( self.testsPath, prjID, absPath ) )
                    if not res:
                        ret = ( self.context.CODE_NOT_FOUND, "ID=%s %s" % (ts['id'],ts['file'])  )
                        break   
                    else:

                        #
                        self.__updatetsparams( currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                                newParam=ts['properties']['inputs-parameters']['parameter'] )
                        self.__updatetsparams( currentParam=doc.properties['properties']['outputs-parameters']['parameter'],
                                                newParam=ts['properties']['outputs-parameters']['parameter'] )
                        
                        # fix in v11, properly dispatch agent keys                        
                        self.__updatetsparams( currentParam=doc.properties['properties']['agents']['agent'],
                                                newParam=ts['properties']['agents']['agent'] )
                        # end of fix
                        
                        ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']
                        ts['properties']['outputs-parameters'] = doc.properties['properties']['outputs-parameters']
                        
                        # fix in v11, properly dispatch agent keys
                        ts['properties']['agents'] = doc.properties['properties']['agents']
                        # end of fix
                        
                        if fileExt == RepoManager.TEST_SUITE_EXT:
                            ts.update( { 'test-definition': doc.testdef, 'test-execution': doc.testexec, 
                                         'path': filenameTs, 'tpid': tpid } )
                        elif fileExt == RepoManager.TEST_ABSTRACT_EXT:
                            ts.update( { 'test-definition': doc.testdef, 'path': filenameTs, 'tpid': tpid } )
                        else:
                            ts.update( { 'test-definition': doc.testdef, 'path': filenameTs, 'tpid': tpid } )
                
                        # backward compatibility
                        self.__fixAliasTp(ts=ts)
            else:
                pass
        return ret

    def __fixAliasTp(self, ts):
        """
        """
        # backward compatibility
        if 'alias' not in ts:
            ts['alias'] = ''
        
        # fix issue encode, ugly fix
        try:
            ts['alias'] =  str(ts['alias'])
        except UnicodeEncodeError as e:
            pass
        else:
            try:
                ts['alias'] = ts['alias'].encode('utf8')
            except UnicodeDecodeError as e:
                ts['alias'] = ts['alias'].decode('utf8')
    
    def __updatetsparams(self, currentParam, newParam):
        """
        Update current test parameters with main parameter
        Internal function

        @param currentParam:
        @type currentParam:

        @param newParam:
        @type newParam:
        """
        for i in xrange(len(currentParam)):
            for np in newParam:
                if np['name'] == currentParam[i]['name'] and currentParam[i]['type'] != "alias":
                    currentParam[i] = np
        # adding new param
        newparams = self.__getnewparams(currentParam, newParam)
        for np in newparams:
            currentParam.append( np )

    def __getnewparams(self, currentParam, newParam):
        """
        New param to add
        Internal function

        @param currentParam:
        @type currentParam:

        @param newParam:
        @type newParam:
        """
        toAdd  = []
        for np in newParam:
            isNew = True
            for cp in currentParam:
                if np['name'] == cp['name']:
                    isNew = False
            if isNew:
                toAdd.append( np )
        return toAdd

    def findInstance(self, filePath, projectName, projectId):
        """
        Find a test instance according to the path of the file
        """
        self.trace("Find tests instance: %s" % filePath)
        
        if filePath.startswith("/"): filePath = filePath[1:]
        
        tests = []
        try:
            for path, subdirs, files in os.walk("%s/%s" % (self.testsPath, projectId) ):
                for name in files:  
                    if name.endswith(RepoManager.TEST_PLAN_EXT) or name.endswith(RepoManager.TEST_GLOBAL_EXT) :
                        doc = TestPlan.DataModel()
                        res = doc.load( absPath = os.path.join(path, name) )
                        if not res:
                            self.error( 'unable to read test plan: %s' % os.path.join(path, name) )
                        else:
                            testsfile = doc.testplan['testplan']['testfile']
                            t= {"instance": 0}
                            testFound = False
                            for i in xrange(len(testsfile)):
                                if testsfile[i]['type'] == 'remote':
                                    if "%s:%s" % (projectName, filePath) == testsfile[i]['file']:
                                        p = os.path.join(path, name)
                                        p = p.split( "%s/%s" % (self.testsPath, projectId) )[1]
                                        t['test'] = p
                                        t['instance'] += 1
                                        testFound = True
                            if testFound: tests.append(t)
  
        except Exception as e:
            self.error( "unable to find test instance: %s" % e )
            return (self.context.CODE_ERROR, tests)
        return (self.context.CODE_OK, tests)
    
    def getFile(self, pathFile, binaryMode=True, project='', addLock=True, login='', 
                    forceOpen=False, readOnly=False):
        """
        New in v17
        Return the file ask by the tester
        and check the file content for testplan or testglobal
        """
        ret = RepoManager.RepoManager.getFile(self, pathFile=pathFile, binaryMode=binaryMode, project=project, 
                                                    addLock=addLock, login=login, forceOpen=forceOpen, 
                                                    readOnly=readOnly)
        result, path_file, name_file, ext_file, project, data_base64, locked, locked_by = ret
        if result != self.context.CODE_OK:
            return ret
            
        if ext_file in [ RepoManager.TEST_PLAN_EXT, RepoManager.TEST_GLOBAL_EXT]:
            # checking if all links are good
            doc = TestPlan.DataModel()
            absPath =  "%s/%s/%s" % (self.testsPath, project, pathFile)
            if not doc.load( absPath =  absPath ):
                self.error( 'unable to read test plan: %s/%s/%s' % (self.testsPath, project, pathFile) )
                return ret
            else:
                testsfile = doc.testplan['testplan']['testfile']
                
                # get all projcts
                success, projectsList = ProjectsManager.instance().getProjectsFromDB()
                
                # read all tests file defined in the testplan or testglobal
                for i in xrange(len(testsfile)):
                    # update only remote file
                    if testsfile[i]['type'] == 'remote':
                        # mark as missing ? 
                        prjName, testPath = testsfile[i]['file'].split(":", 1)
                        prjId = 0
                        for prj in projectsList:
                            if prj["name"] == prjName: 
                                prjId = int(prj["id"])
                                break

                        if not os.path.exists(  "%s/%s/%s" % (self.testsPath, prjId, testPath)  ):
                            testsfile[i]["control"] = "missing"
                        else:
                            testsfile[i]["control"] = ""
                            
                # finally save the change
                doc.write( absPath=absPath )
                return (result, path_file, name_file, ext_file, project, doc.getRaw(), locked, locked_by)
            return ret
        else:
            return ret
    
    def delDir(self, pathFolder, project=''):
        """
        Delete a folder
        """
        # folders reserved
        mp = "%s/%s/" % (self.testsPath, project)
        if os.path.normpath( "%s/%s" % (mp,unicode(pathFolder)) ) == os.path.normpath( "%s/@Recycle" % (mp) ) :
            return self.context.CODE_FORBIDDEN
        if os.path.normpath( "%s/%s" % (mp,unicode(pathFolder)) ) == os.path.normpath( "%s/@Sandbox" % (mp) ) :
            return self.context.CODE_FORBIDDEN
        # end of new
        
        return RepoManager.RepoManager.delDir(self, pathFolder=pathFolder, project=project)

    def delDirAll(self, pathFolder, project=''):
        """
        Delete a folder and all inside
        """
        # folders reserved
        mp = "%s/%s/" % (self.testsPath, project)
        if os.path.normpath( "%s/%s" % (mp,unicode(pathFolder)) ) == os.path.normpath( "%s/@Recycle" % (mp) ) :
            return self.context.CODE_FORBIDDEN
        if os.path.normpath( "%s/%s" % (mp,unicode(pathFolder)) ) == os.path.normpath( "%s/@Sandbox" % (mp) ) :
            return self.context.CODE_FORBIDDEN
        # end of new
         
        return RepoManager.RepoManager.delDirAll(self, pathFolder=pathFolder, project=project)
  
    def moveDir(self, mainPath, folderName, newPath, project='', newProject='', projectsList=[], renamedBy=None):
        """
        Move a folder
        """
        # folders reserved new in v17
        mp = "%s/%s/" % (self.testsPath, project)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(folderName)) ) == os.path.normpath( "%s/@Recycle" % (mp) ) :
            return (self.context.CODE_FORBIDDEN, mainPath, folderName, newPath, project)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(folderName)) ) == os.path.normpath( "%s/@Sandbox" % (mp) ) :
            return (self.context.CODE_FORBIDDEN, mainPath, folderName, newPath, project)
        # end of new
        
        # execute the rename function as before
        ret = RepoManager.RepoManager.moveDir(self, mainPath=mainPath, folderName=folderName, newPath=newPath, 
                                            project=project, newProject=newProject)
        return ret
        
    def moveFile(self, mainPath, fileName, extFilename, newPath, project='', newProject='', 
                        supportSnapshot=False, projectsList=[], renamedBy=None):
        """
        Move a file
        """
        # execute the rename function as before
        ret = RepoManager.RepoManager.moveFile( self, mainPath=mainPath, fileName=fileName, extFilename=extFilename, 
                                                newPath=newPath, project=project, newProject=newProject, 
                                                supportSnapshot=supportSnapshot)

        return ret
        
    def duplicateDir(self, mainPath, oldPath, newPath, project='', newProject='', newMainPath=''):
        """
        Duplicate a folder
        """
        # folders reserved new in v17
        mp = "%s/%s/" % (self.testsPath, project)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(oldPath)) ) == os.path.normpath( "%s/@Recycle" % (mp) ) :
            return (self.context.CODE_FORBIDDEN)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(oldPath)) ) == os.path.normpath( "%s/@Sandbox" % (mp) ) :
            return (self.context.CODE_FORBIDDEN)
        # end of new
        
        return  RepoManager.RepoManager.duplicateDir(self, mainPath=mainPath, oldPath=oldPath, newPath=newPath, 
                                                     project=project, newProject=newProject, newMainPath=newMainPath)
                                                     
    def renameDir(self, mainPath, oldPath, newPath, project='', projectsList=[], renamedBy=None):
        """
        Rename a folder
        """
        # folders reserved new in v17
        mp = "%s/%s/" % (self.testsPath, project)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(oldPath)) ) == os.path.normpath( "%s/@Recycle" % (mp) ) :
            return (self.context.CODE_FORBIDDEN, mainPath, oldPath, newPath, project)
        if os.path.normpath( "%s/%s/%s" % (mp, mainPath, unicode(oldPath)) ) == os.path.normpath( "%s/@Sandbox" % (mp) ) :
            return (self.context.CODE_FORBIDDEN, mainPath, oldPath, newPath, project)
        # end of new
         
        # execute the rename function as before
        ret = RepoManager.RepoManager.renameDir(self, mainPath=mainPath, oldPath=oldPath, newPath=newPath, 
                                                     project=project)

        return ret
        
    def renameFile(self, mainPath, oldFilename, newFilename, extFilename, project='', 
                    supportSnapshot=False, projectsList=[], renamedBy=None):
        """
        Rename a file
        New in v17
        And save the change in the history
        """
        # execute the rename function as before
        ret = RepoManager.RepoManager.renameFile(   self, mainPath=mainPath, oldFilename=oldFilename, 
                                                    newFilename=newFilename,
                                                    extFilename=extFilename, project=project, 
                                                    supportSnapshot=supportSnapshot )

        return ret

    # dbr13 >>
    def updateLinkedScriptPath(self, project, mainPath, oldFilename, newFilename, extFilename, user_login):

        # get current project name and accessible projects list for currnet user

        project_name = ProjectsManager.instance().getProjectName(prjId=project)
        projects = ProjectsManager.instance().getProjects(user=user_login)

        updated_files_list = []

        # create old and new file name
        if mainPath != '/':
            new_test_file_name = '%s:%s/%s.%s' % (project_name, mainPath, newFilename, extFilename)

            # for update location func
            if oldFilename.rsplit(".")[-1] in [RepoManager.TEST_PLAN_EXT,
                                               RepoManager.TEST_ABSTRACT_EXT,
                                               RepoManager.TEST_UNIT_EXT,
                                               RepoManager.TEST_SUITE_EXT]:
                old_test_file_name = oldFilename
            else:
                # for rename func
                old_test_file_name = '%s:/*%s/%s.%s' % (project_name, mainPath[1:], oldFilename, extFilename)
        else:
            new_test_file_name = '%s:%s.%s' % (project_name, newFilename, extFilename)

            # for update location func
            if oldFilename.rsplit(".")[-1] in [RepoManager.TEST_PLAN_EXT,
                                               RepoManager.TEST_ABSTRACT_EXT,
                                               RepoManager.TEST_UNIT_EXT,
                                               RepoManager.TEST_SUITE_EXT]:

                old_test_file_name = oldFilename
            else:
                # for rename func
                old_test_file_name = '%s:%s.%s' % (project_name, oldFilename, extFilename)

        for proj_id in projects:
            project_id = proj_id['project_id']
            _, _, listing, _ = self.getTree(project=project_id)

            tests_tree_update_locations = self.getTestsForUpdate(listing=listing, extFileName=extFilename)

            files_paths = self.get_files_paths(tests_tree=tests_tree_update_locations)

            for file_path in files_paths:
                # init appropriate data model for current file path
                if file_path.endswith(RepoManager.TEST_PLAN_EXT):
                    doc = TestPlan.DataModel()
                    ext_file_name = RepoManager.TEST_PLAN_EXT
                elif file_path.endswith(RepoManager.TEST_GLOBAL_EXT):
                    doc = TestPlan.DataModel(isGlobal=True)
                    ext_file_name =RepoManager.TEST_GLOBAL_EXT
                else:
                    return "Bad file extension: %s" % file_path

                absPath = '%s%s%s' % (self.testsPath, project_id, file_path)
                res = doc.load(absPath=absPath)
                test_files_list = doc.testplan['testplan']['testfile']

                is_changed = False

                for test_file in test_files_list:
                    old_test_file_name_regex = re.compile(old_test_file_name)
                    if re.findall(old_test_file_name_regex, test_file['file']):
                        test_file['file'] = new_test_file_name
                        test_file['extension'] = extFilename
                        is_changed = True
                if is_changed:
                    file_content = doc.getRaw()
                    f_path_list = file_path.split('/')
                    path_file = '/'.join(f_path_list[:-1])
                    name_file = f_path_list[-1][:-4]
                    putFileReturn = self.uploadFile(pathFile=path_file, nameFile=name_file,
                                                    extFile=ext_file_name,
                                                    contentFile=file_content, login=user_login, project=project_id,
                                                    overwriteFile=True, createFolders=False, lockMode=True,
                                                    binaryMode=True, closeAfter=False)
                    success, pathFile, nameFile, extFile, project,\
                    overwriteFile, closeAfter, isLocked, lockedBy = putFileReturn
                    updated_files_list.append({"code": success,
                                               "file-path": pathFile,
                                               "file-name": nameFile,
                                               "file-extension": extFile,
                                               "project-id":  project_id,
                                               "overwrite":  overwriteFile,
                                               "close-after": closeAfter,
                                               "locked": isLocked,
                                               "locked-by": lockedBy})
        return updated_files_list

    def getTestsForUpdate(self, listing, extFileName):

        tests_list = []

        extDict = {
            RepoManager.TEST_ABSTRACT_EXT: [RepoManager.TEST_GLOBAL_EXT, RepoManager.TEST_PLAN_EXT],
            RepoManager.TEST_UNIT_EXT: [RepoManager.TEST_GLOBAL_EXT, RepoManager.TEST_PLAN_EXT],
            RepoManager.TEST_SUITE_EXT: [RepoManager.TEST_GLOBAL_EXT, RepoManager.TEST_PLAN_EXT],
            RepoManager.TEST_PLAN_EXT: [RepoManager.TEST_GLOBAL_EXT]
        }

        for test in listing:
            if test['type'] == 'file':
                ext_test = test['name'].split('.')[-1]
                req_exts = extDict[extFileName]
                if extFileName in extDict and ext_test in req_exts:
                    tests_list.append(test)
            else:
                if test['type'] == 'folder':
                    tests_list.append(test)
                    tests_list[-1]['content'] = (self.getTestsForUpdate(listing=test['content'],
                                                                        extFileName=extFileName))
        return tests_list

    def get_files_paths(self, tests_tree, file_path='/'):

        list_path = []
        for test in tests_tree:
            f_path = file_path
            if test['type'] == 'file':
                list_path.append('%s%s' % (f_path, test['name']))
            else:
                f_path += '%s/' % test['name']
                list_path += self.get_files_paths(test['content'], file_path=f_path)
        return list_path

    # dbr13 <<
        
    def saveToHistory(self, oldPrjId, oldPath, newPrjId, newPath):
        """
        New in v17
        Save all changes in files maded by users
        Theses changes enable to fix testplan or testglobal
        """
        self.renameHistory[ oldPath ] =  { 
                                            "old-prj-id": oldPrjId, 
                                            "old-path": oldPath.split(":", 1)[1],
                                            "virtual-old-path": oldPath,
                                            "new-prj-id": newPrjId,
                                            "new-path": newPath.split(":", 1)[1],
                                            "virtual-new-path": newPath
                                         }
                                         
        self.trace( "NB entries in history: %s" % len(self.renameHistory) )

    def getVariablesFromDB(self, projectId=None):
        """
        Get test variables from database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all users
        sql = """SELECT id, name, project_id"""
        if Settings.getInt( 'MySql', 'test-environment-encrypted'):
            sql += """, AES_DECRYPT(value, "%s") as value""" % Settings.get( 'MySql', 'test-environment-password')
        else:
            sql += """, value"""
        sql += """ FROM `%s-test-environment`""" % ( prefix)
        if projectId is not None:
            sql += """ WHERE project_id='%s'""" % escape("%s" % projectId)
        sql += """ ORDER BY name"""
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read test environment table" )
            return (self.context.CODE_ERROR, "unable to test environment table")

        return (self.context.CODE_OK, dbRows)
        
    def getVariableFromDB(self, projectId, variableName=None, variableId=None):
        """
        Get a specific variable from database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        
        # get all users
        sql = """SELECT id, name, project_id"""
        if Settings.getInt( 'MySql', 'test-environment-encrypted'):
            sql += """, AES_DECRYPT(value, "%s") as value""" % Settings.get( 'MySql', 'test-environment-password')
        else:
            sql += """, value"""
        sql += """ FROM `%s-test-environment`""" % ( prefix)
        sql += """ WHERE project_id='%s'""" % escape( "%s" % projectId)
        if variableName is not None:
            sql += """ AND name LIKE '%%%s%%'""" % escape(variableName)
        if variableId is not None:
            sql += """ AND id='%s'""" % escape( "%s" % variableId)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to search test environment table" )
            return (self.context.CODE_ERROR, "unable to search variable in test environment table")

        return (self.context.CODE_OK, dbRows)
        
    def addVariableInDB(self, projectId, variableName, variableValue):
        """
        Add a variable in the database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        projectId = str(projectId)
        
        if ":" in variableName:
            return (self.context.CODE_ERROR, "bad variable name provided")
            
        # check if the name is not already used
        sql = """SELECT * FROM `%s-test-environment` WHERE name='%s'""" % ( prefix, 
                                                                            escape(variableName.upper()) )
        sql += """ AND project_id='%s'""" % escape(projectId)
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to get variable by name" )
            return (self.context.CODE_ERROR, "unable to get variable by name")
        if len(dbRows): return (self.context.CODE_ALREADY_EXISTS, "this variable already exists")
        
        # good json ?
        try:
            var_json = json.loads(variableValue)
        except Exception as e:
            return (self.context.CODE_ERROR, "bad json value provided")
         
        # this name is free then create project
        sql = """INSERT INTO `%s-test-environment`(`name`, `value`, `project_id` )""" % prefix
        if Settings.getInt( 'MySql', 'test-environment-encrypted'):
            sql += """VALUES('%s', AES_ENCRYPT('%s', '%s'), '%s')""" % (escape(variableName.upper()), 
                                                                        escape(variableValue), 
                                                                        Settings.get( 'MySql', 'test-environment-password'), 
                                                                        escape(projectId))
        else:
            sql += """VALUES('%s', '%s', '%s')""" % (   escape(variableName.upper()), 
                                                        escape(variableValue), 
                                                        escape(projectId))
        dbRet, lastRowId = DbManager.instance().querySQL( query = sql, insertData=True  )
        if not dbRet: 
            self.error("unable to insert variable")
            return (self.context.CODE_ERROR, "unable to insert variable")
            
        return (self.context.CODE_OK, "%s" % int(lastRowId) )
        
    def duplicateVariableInDB(self, variableId, projectId=None):
        """
        Duplicate a variable in database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        variableId = str(variableId)
        
        # find variable by id
        sql = """SELECT * FROM `%s-test-environment` WHERE  id='%s'""" % ( prefix, escape(variableId) )
        if projectId is not None:
            sql += """ AND project_id='%s'""" % escape(projectId)
            
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read variable id" )
            return (self.context.CODE_ERROR, "unable to read variable id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this variable id does not exist")
        variable = dbRows[0]
        
        # duplicate variable
        newVarName = "%s-COPY#%s" % (variable['name'], uniqid())

        return self.addVariableInDB(projectId=variable["project_id"], variableName=newVarName, variableValue=variable["value"])
        
    def updateVariableInDB(self, variableId, variableName=None, variableValue=None, projectId=None):
        """
        Update the value of a variable in a database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        variableId = str(variableId)

        # find variable by id
        sql = """SELECT * FROM `%s-test-environment` WHERE  id='%s'""" % ( prefix, escape(variableId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to read variable id" )
            return (self.context.CODE_ERROR, "unable to read variable id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "this variable id does not exist")
        
        sql_values = []
        if variableName is not None:
            sql_values.append( """name='%s'""" % escape(variableName.upper()))
        if variableValue is not None:
            # good json ?
            try:
                var_json = json.loads(variableValue)
            except Exception as e:
                return (self.context.CODE_ERROR, "bad json value provided")
         
            if Settings.getInt( 'MySql', 'test-environment-encrypted'):
                sql_values.append( """value=AES_ENCRYPT('%s', '%s')""" % ( escape(variableValue), 
                                                                           Settings.get( 'MySql', 'test-environment-password')) )
            else:
                sql_values.append( """value='%s'""" % escape(variableValue))
        if projectId is not None:
            projectId = str(projectId)
            sql_values.append( """project_id='%s'""" % escape(projectId))
            
        # update
        if len(sql_values):
            sql = """UPDATE `%s-test-environment` SET %s WHERE id='%s'""" % (   prefix, 
                                                                                ','.join(sql_values), 
                                                                                variableId )
            dbRet, _ = DbManager.instance().querySQL( query = sql )
            if not dbRet: 
                self.error("unable to update variable")
                return (self.context.CODE_ERROR, "unable to update variable")
            
        return (self.context.CODE_OK, "" )
        
    def delVariableInDB(self, variableId, projectId=None):
        """
        Delete a variable in database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        variableId = str(variableId)
        
        # check if the name is not already used
        sql = """SELECT * FROM `%s-test-environment` WHERE id='%s'""" % ( prefix, escape(variableId) )
        if projectId is not None:
            sql += """ AND project_id='%s'""" % escape( "%s" % projectId)
            
        dbRet, dbRows = DbManager.instance().querySQL( query = sql, columnName=True  )
        if not dbRet: 
            self.error( "unable to get variable by id" )
            return (self.context.CODE_ERROR, "unable to get variable by id")
        if not len(dbRows): return (self.context.CODE_NOT_FOUND, "variable id provided does not exist")
        
        # delete from db
        sql = """DELETE FROM `%s-test-environment` WHERE  id='%s'""" % ( prefix, escape(variableId) )
        if projectId is not None:
            sql += """ AND project_id='%s'""" % escape( "%s" % projectId)
            
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to remove variable by id" )
            return (self.context.CODE_ERROR, "unable to remove variable by id")
            
        return (self.context.CODE_OK, "" )
        
    def delVariablesInDB(self, projectId):
        """
        Delete all variables in database
        """
        # init some shortcut
        prefix = Settings.get( 'MySql', 'table-prefix')
        escape = MySQLdb.escape_string
        projectId = str(projectId)

        # delete from db
        sql = """DELETE FROM `%s-test-environment` WHERE  project_id='%s'""" % ( prefix, escape(projectId) )
        dbRet, dbRows = DbManager.instance().querySQL( query = sql  )
        if not dbRet: 
            self.error( "unable to reset variables" )
            return (self.context.CODE_ERROR, "unable to reset variables")
            
        return (self.context.CODE_OK, "" )

        
###############################
RepoTestsMng = None
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return RepoTestsMng

def initialize (context, taskmgr):
    """
    Instance creation
    """
    global RepoTestsMng
    RepoTestsMng = RepoTests(context=context, taskmgr=taskmgr)

def finalize ():
    """
    Destruction of the singleton
    """
    global RepoTestsMng
    if RepoTestsMng:
        RepoTestsMng = None