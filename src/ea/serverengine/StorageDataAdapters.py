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

import os
import shutil
import time

from ea.libs import Settings, Logger
from ea.serverinterfaces import EventServerInterface as ESI
from ea.serverrepositories import (RepoManager)


class StorageDataAdapters(RepoManager.RepoManager, Logger.ClassLogger):
    def __init__(self, context):
        """
        Storage data adapters
        """
        RepoManager.RepoManager.__init__(self, pathRepo='%s%s' % (Settings.getDirExec(),
                                                                  Settings.get('Paths', 'tmp')),
                                         context=context)
        self.context = context
        self.prefixAdapters = "adapter"
        self.prefixAdaptersAll = "private_storage"
        self.adpDataPath = os.path.normpath("%s/AdaptersData" % self.testsPath)

        self.initStorage()

    def getStoragePath(self):
        """
        Returns the storage main path
        """
        return self.adpDataPath

    def initSubStorage(self, dirProject, dirToday, dirTest):
        """
        Initialize the sub storage folders  YYYY-MM-DD/testid
        """
        # create temp main dir
        mainDir = "%s/%s" % (self.adpDataPath, dirProject)
        mainDir = os.path.normpath(mainDir)
        try:
            if not os.path.exists(mainDir):
                os.mkdir(mainDir, 0o755)
                self.trace("sub adapters storage created: %s" % dirProject)
        except Exception as e:
            self.error("sub adapters folder creation error: %s" % str(e))

        mainDir = "%s/%s/%s" % (self.adpDataPath, dirProject, dirToday)
        mainDir = os.path.normpath(mainDir)
        try:
            if not os.path.exists(mainDir):
                os.mkdir(mainDir, 0o755)
                self.trace("sub adapters storage created: %s" % dirToday)
        except Exception as e:
            self.error("sub adapters folder creation error: %s" % str(e))

        testDir = "%s/%s" % (mainDir, dirTest)
        testDir = os.path.normpath(testDir)
        try:
            # remove first
            if os.path.exists(testDir):
                shutil.rmtree(testDir)
            else:
                os.mkdir(testDir, 0o755)
                self.trace("sub test adapters storage created: %s" % dirTest)
        except Exception as e:
            self.error("sub test adapters folder creation error: %s" % str(e))

    def removeSubStorage(self, dirToday, dirTest, projectId=0):
        """
        Remove the sub storage folder, just the testid
        """
        mainDir = "%s/%s/%s" % (self.adpDataPath, projectId, dirToday)
        testDir = "%s/%s" % (mainDir, dirTest)
        testDir = os.path.normpath(testDir)
        try:
            if os.path.exists(testDir):
                shutil.rmtree(testDir)
                self.trace("adapters storage deleted: %s" % dirTest)
        except Exception as e:
            self.error(
                "unable to delete the temp adapters folder: %s" %
                str(e))

    def initStorage(self):
        """
        Initialize the storage
        """
        try:
            if not os.path.exists(self.adpDataPath):
                os.mkdir(self.adpDataPath, 0o755)
                self.trace("adapters storage created")
        except Exception as e:
            self.trace("folder creation error: %s" % str(e))

    def zipDataV2(self, dirToday, dirTest, destPathZip,
                  replayId, projectId=0, virtualName=""):
        """
        Zip data by adapters and notify users in just one zip
        """
        self.trace("Starting to zip all adapters logs")
        ret = False
        try:
            mainDir = "%s/%s/%s" % (self.adpDataPath, projectId, dirToday)
            testDir = "%s/%s" % (mainDir, dirTest)
            testDir = os.path.normpath(testDir)

            # prepare the file name
            tp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(time.time())) \
                + ".%3.3d" % int((time.time() * 1000) % 1000)
            fileName = "%s_%s_%s" % (self.prefixAdaptersAll, tp, replayId)

            # zip the folder
            zipped = self.zipFolder(folderPath=testDir,
                                    zipName="%s.zip" % fileName,
                                    zipPath=destPathZip)

            if zipped == self.context.CODE_OK:
                # notify users
                if Settings.getInt('Notifications', 'archives'):
                    size_ = os.path.getsize(
                        "%s/%s.zip" %
                        (destPathZip, fileName))
                    notif = {}
                    m = [{"type": "folder",
                          "name": dirToday,
                          "project": "%s" % projectId,
                          "content": [{"type": "folder",
                                       "name": dirTest,
                                       "project": "%s" % projectId,
                                       "virtual-name": virtualName,
                                       "content": [{"type": "file",
                                                    "name": "%s.zip" % fileName,
                                                    'size': str(size_),
                                                    "project": "%s" % projectId}]}]}]
                    notif['archive'] = m
                    data = ('archive', (None, notif))
                    ESI.instance().notifyByUserTypes(body=data,
                                                     admin=True,
                                                     monitor=False,
                                                     tester=True)
                ret = True
            else:
                self.error('error to zip data adapters')
                ret = False
        except Exception as e:
            self.error('unable to zip data adapters v2: %s' % str(e))
        return ret


SDAMng = None


def instance():
    """
    Returns the singleton
    """
    return SDAMng


def initialize(context):
    """
    Instance creation
    """
    global SDAMng
    SDAMng = StorageDataAdapters(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global SDAMng
    if SDAMng:
        SDAMng = None
