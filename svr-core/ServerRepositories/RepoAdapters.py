#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2018 Denis Machard
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

import os 
import sys
import subprocess
import shlex
import shutil
import base64
import zlib
import parser
import re
import tempfile
import tarfile
try:
    import ConfigParser
except ImportError: # python3 support
    import configparser as ConfigParser
import json

try:
    import RepoManager
    import RepoLibraries
except ImportError: # python3 support
    from . import RepoManager
    from . import RepoLibraries

from ServerEngine import ( Common )
from Libs import ( Scheduler, Settings, Logger )
from ServerInterfaces import EventServerInterface as ESI

REPO_TYPE = 1
NO_DATA = ''

MAIN_DESCR = "This library contains all adapters available to test your SUT (System Under Test)."

MAIN_INIT = """%s

__DESCRIPTION__ = "%s"

__HELPER__ =    [%s]

__all__ = [%s]"""

ADPS_INIT = """%s

import TestExecutorLib.TestAdapterLib as TestAdapterLib
import TestExecutorLib.TestLibraryLib as TestLibraryLib

TestAdapterLib.setVersion("%s")
TestLibraryLib.setVersion("%s")

__DEFAULT__ = False

__RN__ = "\"\"tbc"\"\"

__DESCRIPTION__ = "%s"

__HELPER__ =    [%s]
"""

ADP_INIT = """%s

__DESCRIPTION__ = "%s"

__HELPER__ =    [%s]
"""

DEF_RN= """Date: xx/xx/xxxx
What's new
    1. 
Issues fixed
    1. 
"""

REGEXP_VERSION = r"^v[0-9]{3,}\Z"

class RepoAdapters(RepoManager.RepoManager, Logger.ClassLogger):    
    """
    Repo adapters manager
    """
    def __init__(self, context, taskmgr):
        """
        Construct Adpaters Manager
        """
        RepoManager.RepoManager.__init__(self,
                                    pathRepo='%s/%s/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'adapters' ) ), 
                                    extensionsSupported = [ RepoManager.PY_EXT, RepoManager.TXT_EXT ],
                                    context = context)

        self.context = context
        self.taskmgr = taskmgr
        self.__pids__ = {}
        self.prefixBackup = "backupadapters"
        self.destBackup = "%s%s" % ( Settings.getDirExec(), Settings.get( 'Paths', 'backups-adapters' ) )
        self.embeddedPath = "%s/%s/%s" % (  Settings.getDirExec(),
                                            Settings.get( 'Paths', 'packages' ),  
                                            Settings.get( 'Paths', 'adapters' ) )

        # Initialize the repository
        self.info( 'Deploying sut adapters ...' )
        deployed = self.deploy()
        if deployed:
            self.info("All sut adapters deployed" )

        # update main init file
        self.updateMainInit()
        
        # cleanup all lock files on init
        self.cleanupLocks()
        
    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="RAP - %s" % txt)
        
    def deploy(self):
        """
        Deploy package
        """
        # list  embedded package
        # then delete it if already exists on target folder
        # finaly untar the package
        deployedSuccess=True
        pkgs = os.listdir( self.embeddedPath )
        for pkg in pkgs:
            try:
                # Example: SutAdapters-1.2.0.tar.gz
                versionStr = pkg.rsplit("-", 1)[1].split(".tar.gz")[0]
                versionTarget = versionStr
            except Exception as e:
                self.error( "unable to extract version: %s" %str(e) )
                deployedSuccess=False
            else:
                # remove folder if exists
                versionPath = "%s/%s/" % (self.testsPath, versionTarget )
                try:
                    if os.path.exists( versionPath ):
                        shutil.rmtree( versionPath )
                except Exception as e:
                    self.error( "pre install cleanup: %s" %str(e) )
                    deployedSuccess=False
                else:
                    # untar
                    try:
                        DEVNULL = open(os.devnull, 'w')
                        __cmd__ = "%s xf %s/%s -C %s" % (Settings.get( 'Bin', 'tar' ), 
                                                         self.embeddedPath, pkg, 
                                                         Settings.getDirExec())
                        ret = subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
                        if ret: raise Exception("unable to untar sut adapter pkg")
            
                    except Exception as e:
                        self.error("sut adapter installation failed: %s" % str(e) )
                        deployedSuccess=False
                    else:
                        self.trace( "Sut adapter %s deployed succesfully" % versionTarget )
        return deployedSuccess
        
    def getGeneric(self):
        """
        Return the default generic package
        """
        settings_file = ConfigParser.ConfigParser()
        settings_file.read( "%s/settings.ini" % Settings.getDirExec() )
        defaultPkg = settings_file.get("Default", "generic-adapters" )
        del settings_file
        return defaultPkg
        
    def setGeneric(self, packageName):
        """
        Set the package as default
        """
        ret =  self.context.CODE_ERROR
        self.trace("set as generic the package -> %s" % packageName)
        try:
            # read the file
            fd_setting = open( "%s/settings.ini" % Settings.getDirExec() )
            settings_content = fd_setting.read()
            fd_setting.close()
            
            # replace key adapter, settings is not used because comments are removed
            newsettings_content = re.sub("generic-adapters=.*", 
                                         "generic-adapters=%s" % packageName, 
                                         settings_content)
            fd_setting2 = open( "%s/settings.ini" % Settings.getDirExec(), 'w' )
            fd_setting2.write(newsettings_content)
            fd_setting2.close()
            
            ret = self.context.CODE_OK
        except Exception as e:
            self.error('unable to set the generic adapter: %s' % e)
        return ret
        
    def getDefault(self):
        """
        Return the default adapters package
        """
        settings_file = ConfigParser.ConfigParser()
        settings_file.read( "%s/settings.ini" % Settings.getDirExec() )
        defaultPkg = settings_file.get("Default", "current-adapters" )
        del settings_file
        return defaultPkg
        
    def setDefaultV2(self, packageName):
        """
        Set the package as default
        """
        ret =  self.context.CODE_ERROR
        self.trace("set as default the package -> %s" % packageName)
        try:
            # read the file
            fd_setting = open( "%s/settings.ini" % Settings.getDirExec() )
            settings_content = fd_setting.read()
            fd_setting.close()
            
            # replace key adapter, settings is not used because comments are removed
            newsettings_content = re.sub("current-adapters=.*", 
                                         "current-adapters=%s" % packageName, 
                                         settings_content)
            fd_setting2 = open( "%s/settings.ini" % Settings.getDirExec(), 'w' )
            fd_setting2.write(newsettings_content)
            fd_setting2.close()
            
            ret = self.context.CODE_OK
        except Exception as e:
            self.error('unable to set the default adapter v2: %s' % e)
        return ret

    def unsetAll(self):
        """
        Set all package to defaut=False
        Will be deprecated on the next release
        """
        for f in os.listdir(self.testsPath):
            if os.path.isdir( "%s/%s" % (self.testsPath,f) ):
                try:
                    fd_init = open( "%s/%s/__init__.py" % (self.testsPath,f) )
                    initcontent = fd_init.read()
                    fd_init.close()
                except Exception as e:
                    self.error( "unable to read init file (%s/%s): %s" % (self.testsPath,f, e) )
                else:
                    newinitcontent = initcontent.replace("__DEFAULT__ = True","__DEFAULT__ = False")
                    fd_init2 = open( "%s/%s/__init__.py" % (self.testsPath,f), 'w' )
                    fd_init2.write(newinitcontent)
                    fd_init2.close()

    def getInstalled(self, withQuotes=False, asList=False):
        """
        Return all installed adapters
        """
        installed = []
        for f in os.listdir(self.testsPath):
            if f == "__pycache__": continue
            
            if os.path.isdir( "%s/%s" % (self.testsPath,f) ):
                if withQuotes:
                    installed.append('"%s"' % f)
                else:
                    installed.append(f)
        installed.sort()
        self.trace( "Sut adapters installed: %s" % ', '.join(installed) )
        if asList:
            return installed
        return ','.join(installed)

    def scheduleBackup(self):
        """
        Schedule an automatic backup on boot
        """
        self.trace('schedule backups adapters')
        schedAt = Settings.get( 'Backups', 'adapters-at' )
        backupName = Settings.get( 'Backups', 'adapters-name' )

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
                                        daily=( int(h), int(m), int(s) ), hourly=None, everyMin=None, 
                                        everySec=None, at=None, delay=None, timesec=None,
                                        callback=self.createBackup, backupName=backupName )
        elif int(schedType) == Scheduler.SCHED_HOURLY:
            m, s = schedAt.split(',')
            self.taskmgr.registerEvent( id=None, author=None, name=None, weekly=None, 
                                        daily=None, hourly=( int(m), int(s) ), everyMin=None, 
                                        everySec=None, at=None, delay=None, timesec=None,
                                        callback=self.createBackup, backupName=backupName )
        else:
            self.error( 'schedulation type not supported: %s' % schedType )

    def addPyInitFile(self, pathFile, descr="", helper="", allmodules="", adps=False, mainInit=False):
        """
        Add the default __init__ file of the repository

        @type  archivePath:
        @param archivePath:

        @type  descr:
        @param descr:

        @return: 
        @rtype: 
        """
        HEADER = ''
        tpl_path = "%s/%s/adapter_header.tpl" % ( Settings.getDirExec(), 
                                                  Settings.get( 'Paths', 'templates' ) )
        try:
            fd = open( tpl_path , "r")
            HEADER = fd.read()
            fd.close()
        except Exception as e:
            self.error( 'unable to read template adapter header: %s' % str(e) )

        try:
            if mainInit:
                default_init = MAIN_INIT % (HEADER, descr, helper, allmodules)
            else:
                default_init = ADP_INIT % (HEADER, descr, helper)
            
            if adps:
                default_init = ADPS_INIT % (HEADER, 
                                            Settings.get( 'Default', 'current-adapters' ),
                                            Settings.get( 'Default', 'current-libraries' ), 
                                            descr, 
                                            helper)

            f = open( '%s/__init__.py' % pathFile, 'w')
            f.write( default_init )
            f.close()
        except Exception as e:
            self.error( e )
            return False
        return True

    def addDefaultRn(self, pathFile):
        """
        Add the default release notes of the repository

        @return: 
        @rtype: 
        """
        try:
            default_rn = DEF_RN
            f = open( '%s/releasenotes.txt' % pathFile , 'w')
            f.write( default_rn )
            f.close()
        except Exception as e:
            self.error( e )
            return False
        return True

    def uninstall(self):
        """
        Removes all files in the repository

        @return: 
        @rtype: 
        """
        ret =  self.context.CODE_ERROR
        try:
            # remove all files and folders
            ret = self.emptyRepo(projectId='')

            # create default __init__ file
            initCreated = self.updateMainInit()
            if not initCreated:
                ret =  self.context.CODE_ERROR
            return ret
        except Exception as e:
            raise Exception( "[uninstall] %s" % str(e) )
        return ret

    def deleteBackups(self):
        """
        Delete all backups 

        @return: 
        @rtype: 
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
            notif['repo-adapters'] = {}
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

    def getBackups(self, b64=False):
        """
        Get all backups

        @return: 
        @rtype: 
        """
        _, _, backups, _ = self.getListingFilesV2(path=self.destBackup, 
                                                  extensionsSupported=[RepoManager.ZIP_EXT])
        return backups

    def getTree(self, b64=False):
        """
        Get tree folders
        """
        return self.getListingFilesV2(path=self.testsPath)

    def getLastBackupIndex(self, pathBackups ):
        """
        Returns the lask backup index

        @type  pathBackups:
        @param pathBackups:

        @return: 
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
        Create a backup of all adapters

        @type  backupName:
        @param backupName:

        @return: 
        @rtype: 
        """
        ret = self.context.CODE_ERROR
        try:
            backupIndex = self.getLastBackupIndex( pathBackups=self.destBackup )
            backupDate = self.getTimestamp() 
            backupFilename = '%s%s_%s_%s' % ( self.prefixBackup, backupIndex, backupName, backupDate )
            
            # new in v14.0.0: create tar gz
            if Settings.getInt( 'Backups', 'adapters-dest-tar-gz' ):
                self.trace( "backup adapters to %s/%s.tar.gz" % (self.destBackup,backupFilename) )
                DEVNULL = open(os.devnull, 'w')
                __cmd__ = "%s cvfz %s/%s.tar.gz -C %s ." % (Settings.get( 'Bin', 'tar' ), 
                                                            self.destBackup, 
                                                            backupFilename, 
                                                            self.testsPath)
                ret = subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
                if ret: raise Exception("unable to tar sut adapter pkg")
                ret = self.context.CODE_OK
                
            # create a zip file
            if Settings.getInt( 'Backups', 'adapters-dest-zip' ):
                self.trace( "backup adapters to %s/%s.zip" % (self.destBackup,backupFilename) )
                zipped = self.zipFolder(folderPath=self.testsPath, 
                                        zipName="%s.zip" % backupFilename,
                                        zipPath=self.destBackup, 
                                        ignoreExt=['.pyc', '.pyo'])
                ret = zipped
                if zipped == self.context.CODE_OK:
                    self.info( "backup adapters successfull: %s" % backupFilename )
                    # now notify all connected admin users
                    backupSize = os.path.getsize( "%s/%s.zip" % (self.destBackup, backupFilename) )
                    notif = {}
                    notif['repo-adapters'] = {}
                    notif['repo-adapters']['backup'] = {'name': backupName, 'date': backupDate, 'size': backupSize, 
                                                        'fullname': "%s.zip" % backupFilename }
                    data = ( 'repositories', ( None, notif) )   
                    ESI.instance().notifyAllAdmins(body = data)
                else:
                    self.error( "backup adapters %s failed" % backupFilename )
        except Exception as e:
            raise Exception( "[createBackup] %s" % str(e) )
        return ret

    def updateMainInit(self):
        """
        Update the main init file
        """
        descr = ""
        allmodules = self.getInstalled(withQuotes=True)
        ret = self.addPyInitFile( pathFile = self.testsPath, descr=MAIN_DESCR, 
                                    allmodules=allmodules, mainInit=True )
        return ret

    def notifyUpdate(self):
        """
        """
        # update context and rns of all connected  users
        data = ( 'context-server', ( 'update', self.context.getInformations() ) )     
        ESI.instance().notifyAll(body = data)

    def getRn(self, b64=False):
        """
        Return the adapters release notes

        @return: 
        @rtype: string
        """
        # rn_ret = ''
        rns = []
        adps = self.getInstalled(asList=True)
        adps.reverse()
        for f in adps:
            rn = ''
            try:
                frn = open( '%s/%s/__init__.py' % (self.testsPath,f)  )
                init_raw= frn.read()
                if '"""' in init_raw:
                    rn = init_raw.split('__RN__ = """')[1].split('"""', 1)[0]
                else:
                    rn = ''
                frn.close()
            except Exception as e:
                self.error( "Unable to read init file: %s" % str(e) )
            else:
                version_name = f
                match = re.search(REGEXP_VERSION, f)
                if match:
                    version_name = f[1:]
                rns.append( "\n%s\n%s" % (version_name, Common.indent(rn,1) ) )

        return '\n'.join(rns)

    def checkSyntax(self, content):
        """
        Check the syntax of the content passed as argument

        @param content: 
        @type content:

        @return: 
        @rtype: tuple
        """
        try:
            content_decoded = base64.b64decode(content)
            parser.suite(content_decoded).compile()
        except SyntaxError as e:
            syntax_msg = str(e)
            return False, str(e)

        return True, ''

    def checkGlobalSyntax(self):
        """
        Check syntax and more of all adapters

        @return: 
        @rtype: tuple
        """
        __cmd__ = "%s %s/Core/docgenerator.py %s %s False False True True" % ( Settings.get( 'Bin', 'python' ), 
                                                                               Settings.getDirExec(), Settings.getDirExec(),
                                                                                "%s/%s" % (Settings.getDirExec(), 
                                                                                Settings.get( 'Paths', 'tmp' ) )
                                                                            )
        p = os.popen(__cmd__)
        msg_err = p.readlines()
        if len(msg_err) == 0:
            return True, ''
        else:
            msg_err = '\n'.join(msg_err).replace(".py", "")
            return False, msg_err

    def addAdapter(self, pathFolder, adapterName, mainAdapters=False):
        """
        Add adapter

        @param pathFolder: 
        @type pathFolder:

        @param adapterName: 
        @type adapterName:  

        @return: 
        @rtype:
        """
        ret = self.addDir(pathFolder, adapterName)
        if ret != self.context.CODE_OK:
            return ret
        
        allmodules = ''
        if mainAdapters:
            # update main init file
            ret = self.updateMainInit()
            if not ret:
                return self.context.CODE_ERROR
            else:
                self.notifyUpdate()
        
        ret = self.addPyInitFile( pathFile = "%s/%s/%s/" % (self.testsPath, pathFolder, adapterName), 
                                  adps=mainAdapters )
        if not ret:
            return self.context.CODE_ERROR
        else:
            return self.context.CODE_OK

    def delFile(self, pathFile):
        """
        Delete the file gived in argument
        The rename of the file 'releasenotes' and __init__.py are denied,
        it is specific to the repository adapters

        @type  pathFile:
        @param pathFile:

        @return: 
        @rtype: 
        """
        # exceptions
        if pathFile == "releasenotes.txt":
            return self.context.CODE_FORBIDDEN
        if pathFile == "__init__.py":
            return self.context.CODE_FORBIDDEN
        try:
            if pathFile.endswith('.py'):
                RepoManager.RepoManager.delFile(self, pathFile="%so" % pathFile)
                RepoManager.RepoManager.delFile(self, pathFile="%sc" % pathFile)
        except Exception as e:
            pass
        return RepoManager.RepoManager.delFile(self, pathFile=pathFile)
    
    def renameFile(self, mainPath, oldFilename, newFilename, extFilename):
        """
        Rename the file gived in argument
        The rename of the file 'releasenotes' is denied, it is specific to the repository adapters

        @type  mainPath:
        @param mainPath:

        @type  oldFilename:
        @param oldFilename:

        @type  newFilename:
        @param newFilename:

        @type  extFilename:
        @param extFilename:

        @return: 
        @rtype: 
        """
        # exceptions
        if mainPath == "" and oldFilename == "releasenotes":
            return ( self.context.CODE_FORBIDDEN, mainPath, oldFilename, newFilename, extFilename )
        if mainPath == "" and oldFilename == "__init__":
            return ( self.context.CODE_FORBIDDEN, mainPath, oldFilename, newFilename, extFilename )
        return RepoManager.RepoManager.renameFile(self, mainPath, oldFilename, newFilename, extFilename)

    def moveFile(self, mainPath, fileName, extFilename, newPath ):
        """
        Move the file gived in argument
        Move the file 'releasenotes' is denied, it is specific to the repository adapters

        @type  mainPath:
        @param mainPath:

        @type  fileName:
        @param fileName:

        @type  newPath:
        @param newPath:

        @type  extFilename:
        @param extFilename:

        @return: 
        @rtype: 
        """
        # exceptions
        if mainPath == "" and fileName == "releasenotes":
            return ( self.context.CODE_FORBIDDEN, mainPath, fileName, extFilename, newPath )
        if mainPath == "" and fileName == "__init__":
            return ( self.context.CODE_FORBIDDEN, mainPath, fileName, extFilename, newPath )
        return RepoManager.RepoManager.moveFile(self, mainPath, fileName, extFilename, newPath )

    def duplicateDir(self, mainPath, oldPath, newPath, newMainPath=''):
        """
        Duplicate folder
        """
        ret =  RepoManager.RepoManager.duplicateDir(self, mainPath=mainPath, oldPath=oldPath, 
                                                    newPath=newPath, newMainPath=newMainPath)
        ok = self.updateMainInit()
        if ok:
            # BEGING Issue 411, set the package as default
            try:
                fd_init = open( "%s/%s/%s/__init__.py" % (self.testsPath, newMainPath, newPath) )
                initcontent = fd_init.read()
                fd_init.close()
            except Exception as e:
                self.error( "unable to read init file (%s/%s/%s/__init__.py): %s" % (self.testsPath, newMainPath, newPath, e) )
            else:
                if "__DEFAULT__" in initcontent:
                    self.trace("updating init file to set as default")
                    newinitcontent = initcontent.replace("__DEFAULT__ = True","__DEFAULT__ = False")
                    fd_init2 = open( "%s/%s/%s/__init__.py" % (self.testsPath, newMainPath, newPath), 'w' )
                    fd_init2.write(newinitcontent)
                    fd_init2.close()
            # END Issue 411
            # notify the change
            self.notifyUpdate()
        return ret

    def renameDir(self, mainPath, oldPath, newPath):
        """
        Rename folder
        """
        ret =  RepoManager.RepoManager.renameDir(self, mainPath=mainPath, 
                                                 oldPath=oldPath, newPath=newPath)
        ok = self.updateMainInit()
        if ok:
            self.notifyUpdate()
        return ret
    
    def delDir(self, pathFolder):
        """
        Delete folder
        """
        ret = RepoManager.RepoManager.delDir(self, pathFolder=pathFolder)
        ok = self.updateMainInit()
        if ok:
            self.notifyUpdate()
        return ret

    def delDirAll(self, pathFolder):
        """
        Delete all folders
        """
        ret = RepoManager.RepoManager.delDirAll(self, pathFolder=pathFolder)
        ok = self.updateMainInit()
        if ok:
            self.notifyUpdate()
        return ret
        
    def cleanupLocks(self):
        """
        Cleanup all lock files
        """
        ret = False
        self.trace('Cleanup all lock files for adapters...')
        try:
            DEVNULL = open(os.devnull, 'w')
            sys.stdout.write( "Cleanup all lock files for adapters...\n")
            __cmd__ = "%s/Scripts/unlock-adapters.sh %s/Scripts/" % (Settings.getDirExec(), 
                                                                     Settings.getDirExec())
            subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
            ret = True
        except Exception as e:
            self.error("unable to cleanup lock files for adapters: %s" % e)
        
        sys.stdout.flush()
        
        return ret
    
    def generateFromWSDL(self, wsdlUrl, wsdlFile, pkg, overwrite=False):
        """
        Generate adapter from wsdl
        """
        self.trace("Generating adapter form wsdl..." )
        ret = False
        try:
            wsdl = wsdlUrl
            f = None
            if len(wsdlFile):
                self.trace("mode read from file")
                wsdlDecoded = base64.b64decode(wsdlFile)
                f = tempfile.NamedTemporaryFile(delete=False)
                f.write(wsdlDecoded)
                f.close()
                
                wsdl = f.name
                
            __cmd__ = '%s %s/Scripts/generate-wsdl-adapter.py --wsdl="%s" --pkg="%s" --pathlib="%s"' % ( 
                                                            Settings.get( 'Bin', 'python' ),
                                                            Settings.getDirExec(),
                                                            wsdl, 
                                                            pkg,
                                                            Settings.getDirExec()
                                                        )
            if overwrite:
                __cmd__ += ' --overwrite'
            self.trace( __cmd__ )
            __cmd_args__ = shlex.split(__cmd__)
            p = subprocess.Popen( __cmd_args__, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
            out, err = p.communicate()
            if out:
                self.trace( "WSDL generator (out): %s" % out )
            if err:
                self.error( "WSDL generator (err): %s" % err )
            if p.returncode >= 1:
                self.error('Unable to make adp from wsdl')
            else:
                self.info('Adapter generated successfully')
                ret = True

        except Exception as e:
            self.error( "unable to generate adapter from wsdl: %s" % e )

        return ret

RA = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return RA

def initialize (context, taskmgr):
    """
    Instance creation
    """
    global RA
    RA = RepoAdapters(context=context, taskmgr=taskmgr)

def finalize ():
    """
    Destruction of the singleton
    """
    global RA
    if RA:
        RA = None