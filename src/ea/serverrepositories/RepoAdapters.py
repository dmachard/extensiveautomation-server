#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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
import base64
import parser

from ea.serverrepositories import RepoManager
from ea.libs import ( Settings, Logger )

REPO_TYPE = 1
NO_DATA = ''

MAIN_DESCR = "This library contains all adapters available to test your SUT (System Under Test)."

MAIN_INIT = """%s

__DESCRIPTION__ = "%s"

__HELPER__ =    [%s]

__all__ = [%s]"""


ADP_INIT = """%s

__DESCRIPTION__ = "%s"
"""

REGEXP_VERSION = r"^v[0-9]{3,}\Z"

class RepoAdapters(RepoManager.RepoManager, Logger.ClassLogger):    
    """
    Repo adapters manager
    """
    def __init__(self, context):
        """
        Construct Adpaters Manager
        """
        RepoManager.RepoManager.__init__(self,
                                    pathRepo='%s/%s/' % ( Settings.getDirExec(), 
                                                          Settings.get( 'Paths', 'packages-sutadapters' ) ), 
                                    extensionsSupported = [ RepoManager.PY_EXT, 
                                                            RepoManager.TXT_EXT ],
                                    context = context)

        self.context = context
        self.__pids__ = {}

        # update main init file
        self.updateMainInit()

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="RAP - %s" % txt)

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

    def addPyInitFile(self, pathFile, descr="", helper="", 
                        allmodules="", adps=False, mainInit=False):
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
                default_init = ADP_INIT % (HEADER, descr)

            f = open( '%s/__init__.py' % pathFile, 'w')
            f.write( default_init )
            f.close()
        except Exception as e:
            self.error( e )
            return False
        return True

    def getTree(self, b64=False):
        """
        Get tree folders
        """
        return self.getListingFilesV2(path=self.testsPath, 
                                      folderIgnored= [ "deps", "samples"])

    def updateMainInit(self):
        """
        Update the main init file
        """
        allmodules = self.getInstalled(withQuotes=True)
        ret = self.addPyInitFile( pathFile = self.testsPath, descr=MAIN_DESCR, 
                                    allmodules=allmodules, mainInit=True )
        return ret

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
            return False, str(e)

        return True, ''

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

        if mainAdapters:
            # update main init file
            ret = self.updateMainInit()
            if not ret:
                return self.context.CODE_ERROR
                
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
        if pathFile == "__init__.py":
            return self.context.CODE_FORBIDDEN
        try:
            if pathFile.endswith('.py'):
                RepoManager.RepoManager.delFile(self, pathFile="%so" % pathFile)
                RepoManager.RepoManager.delFile(self, pathFile="%sc" % pathFile)
        except Exception:
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
        if mainPath == "" and fileName == "__init__":
            return ( self.context.CODE_FORBIDDEN, mainPath, fileName, extFilename, newPath )
        return RepoManager.RepoManager.moveFile(self, mainPath, fileName, extFilename, newPath )

    def duplicateDir(self, mainPath, oldPath, newPath, newMainPath=''):
        """
        Duplicate folder
        """
        ret =  RepoManager.RepoManager.duplicateDir(self, mainPath=mainPath, oldPath=oldPath, 
                                                    newPath=newPath, newMainPath=newMainPath)
        self.updateMainInit()
        return ret

    def renameDir(self, mainPath, oldPath, newPath):
        """
        Rename folder
        """
        ret =  RepoManager.RepoManager.renameDir(self, mainPath=mainPath, 
                                                 oldPath=oldPath, newPath=newPath)
        self.updateMainInit()
        return ret
    
    def delDir(self, pathFolder):
        """
        Delete folder
        """
        ret = RepoManager.RepoManager.delDir(self, pathFolder=pathFolder)
        self.updateMainInit()
        return ret

    def delDirAll(self, pathFolder):
        """
        Delete all folders
        """
        ret = RepoManager.RepoManager.delDirAll(self, pathFolder=pathFolder)
        self.updateMainInit()
        return ret

RA = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return RA

def initialize (context):
    """
    Instance creation
    """
    global RA
    RA = RepoAdapters(context=context)

def finalize ():
    """
    Destruction of the singleton
    """
    global RA
    if RA:
        RA = None