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

"""
Generic document module
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
try:
    from PyQt4.QtGui import (QWidget)
except ImportError:
    from PyQt5.QtWidgets import (QWidget)

from Libs import QtHelper, Logger


class WDocument(QWidget, Logger.ClassLogger):
    """
    Document widget
    """
    def __init__(self, parent = None, path = None, filename = None, extension = None,
                        nonameId = None, remoteFile=False, repoDest=None, project=0, isLocked=False):
        """
        Constructor

        @param parent: 
        @type parent:

        @param path: 
        @type path:

        @param filename: 
        @type filename:

        @param extension: 
        @type extension:

        @param nonameId: 
        @type nonameId:

        @param remoteFile: 
        @type remoteFile:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.project = project
        self.path = path
        self.extension = extension
        self.filename = 'Noname'
        if filename is None:
            self.filename += str(nonameId)
        else: 
            self.filename = str(filename)

        self.__modify = False
        self.__readOnly = True
        self.__isLocked = isLocked
        self.isRemote = remoteFile
        self.repoDest = repoDest            
        
    def getPathOnly(self):
        """
        Returns path only
        """
        return self.path

    def updateFilename(self, filename):
        """
        Update filename
        """
        self.filename = str(filename)

    def updatePath(self, pathFilename):
        """
        Update path
        """
        self.path = str(pathFilename)

    def isSaved (self):
        """
        Retuns True if the document is saved

        @return:
        @rtype: boolean
        """
        if self.path is not None:
            return True
        else:
            return False

    def unSaved(self):
        """
        Set unsave
        """
        self.path = None

    def isModified (self):
        """
        Return boolean to indicate if the document is modified

        @return: 
        @rtype: boolean
        """
        return self.__modify

    def isLocked (self):
        """
        Return boolean to indicate if the document is modified

        @return: 
        @rtype: boolean
        """
        return self.__isLocked
        
    def setReadOnly (self, readOnly):
        """
        Set as readonly

        @param readOnly: 
        @type readOnly:
        """
        self.__readOnly = readOnly

    def getReadOnly(self):
        """
        Is readonly ?
        """
        return self.__readOnly

    def setUnmodify (self, repoType=None):
        """
        Set unmodify
        """
        self.__modify = False
        if repoType is not None:
            self.repoDest = repoType
        self.parent.updateTabTitle(wdoc = self, title = self.getShortName() )

    def setModify (self):
        """
        Set modify
        """
        if not self.__readOnly:
            self.__modify = True
            self.parent.updateTabTitle(wdoc = self, title = self.getShortName() )

    def getPath (self, absolute = True, withAsterisk = False, withExtension = True, 
                 withLocalTag = False):
        """
        Return the path of the file

        @param absolute: 
        @type absolute: boolean

        @param withAsterisk: 
        @type withAsterisk: boolean

        @return: 
        @rtype: string
        """
        fileName = self.getShortName( withAsterisk = withAsterisk, 
                                      withExtension = withExtension, 
                                      withLocalTag=withLocalTag)
        if absolute: 
            root = self.path
        else:
            root = ''
        if self.path is not None: 
            if len(root) == 0:
                path = r'%s' % fileName
            else:
                path = r'%s/%s' % (root, fileName)
        else:
            path = r'%s' % fileName
        return path

    def getShortName (self, withAsterisk = True, withExtension = False, 
                      withLocalTag=True):
        """
        Return the name of the script

        @param withAsterisk: 
        @type withAsterisk: boolean

        @param withExtension: 
        @type withExtension: boolean

        @param withLocalTag: 
        @type withLocalTag: boolean

        @return: 
        @rtype: string
        """
        if withExtension:           
            if self.extension is not None:
                title = "%s.%s" % (self.filename, self.extension) 
            else:
                title = self.filename
        else:
            title = self.filename

        if withAsterisk:
            if self.__modify:
                title += " *"
            elif title.endswith(' *'):
                title = title[:-2]
        return title
