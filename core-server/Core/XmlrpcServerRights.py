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

from Libs import Settings, Logger

class XmlRpcRights(object):
    """
    XmlRPC rights
    """
    def __init__(self):
        """
        Constructor
        """
        ADMINISTRATOR = Settings.get('Server', 'level-admin')
        TESTER = Settings.get('Server', 'level-tester')
        DEVELOPER = Settings.get('Server', 'level-developer')
        LEADER = Settings.get('Server', 'level-leader')
        SYSTEM = Settings.get('Server', 'level-system')
        
        self.XMLRPC_RIGHTS = {
            "xmlrpc_authenticateClient":        [ ],
            "xmlrpc_checkUpdateAuto":           [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_checkUpdate":               [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_replayTest":                [ ADMINISTRATOR, TESTER ],
            "xmlrpc_addDevTime":                [ ADMINISTRATOR, TESTER ],
            "xmlrpc_checkDesignTest":           [ ADMINISTRATOR, TESTER ],
            "xmlrpc_checkSyntaxTest":           [ ADMINISTRATOR, TESTER ],
            "xmlrpc_checkSyntaxAdapter":        [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_checkSyntaxAdapters":       [ ADMINISTRATOR, DEVELOPER ] , 
            "xmlrpc_checkSyntaxLibrary":        [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_checkSyntaxLibraries":      [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_scheduleTests":             [ ADMINISTRATOR, TESTER, SYSTEM ],
            "xmlrpc_scheduleTest":              [ ADMINISTRATOR, TESTER, SYSTEM],
            "xmlrpc_rescheduleTest":            [ ADMINISTRATOR, TESTER, SYSTEM ],
            "xmlrpc_loadTestCache":             [ ADMINISTRATOR, TESTER],
            "xmlrpc_unauthenticateClient":      [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_getServerUsage":            [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_getServerInformations":     [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_getReleaseNotes":           [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_getAdvancedInformations":   [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_cancelTask":                [ ADMINISTRATOR, TESTER ],
            "xmlrpc_killTask":                  [ ADMINISTRATOR, TESTER ],
            "xmlrpc_refreshHelper":             [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_refreshRepo":               [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_openFileRepo":              [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_getFileRepo":               [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_importFileRepo":            [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_unlockFileRepo":            [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_putFileRepo":               [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_addDirRepo":                [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_delDirRepo":                [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_delDirAllRepo":             [ ADMINISTRATOR ],
            "xmlrpc_renameDirRepo":             [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_duplicateDirRepo":          [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_delFileRepo":               [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_renameFileRepo":            [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_duplicateFileRepo":         [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_resetTestsStats":           [ ADMINISTRATOR, LEADER ],
            "xmlrpc_emptyRepo":                 [ ADMINISTRATOR, LEADER ],
            "xmlrpc_zipRepoArchives":           [ ADMINISTRATOR, TESTER ],
            "xmlrpc_refreshStatsRepo":          [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_refreshContextServer":      [ ADMINISTRATOR ],
            "xmlrpc_refreshStatsServer":        [ ADMINISTRATOR ],
            "xmlrpc_stopAgent":                 [ ADMINISTRATOR, TESTER ],
            "xmlrpc_startAgent":                [ ADMINISTRATOR, TESTER ],
            "xmlrpc_refreshRunningAgents":      [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_refreshDefaultAgents":      [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_addAgent":                  [ ADMINISTRATOR, TESTER ],
            "xmlrpc_delAgent":                  [ ADMINISTRATOR, TESTER ],
            "xmlrpc_stopProbe":                 [ ADMINISTRATOR, TESTER ],
            "xmlrpc_startProbe":                [ ADMINISTRATOR, TESTER ],
            "xmlrpc_refreshRunningProbes":      [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_refreshDefaultProbes":      [ ADMINISTRATOR, TESTER ],
            "xmlrpc_addProject":                [ ADMINISTRATOR, LEADER ],
            "xmlrpc_delProject":                [ ADMINISTRATOR, LEADER ],
            "xmlrpc_addProbe":                  [ ADMINISTRATOR, TESTER ],
            "xmlrpc_delProbe":                  [ ADMINISTRATOR, TESTER ],
            "xmlrpc_genCacheHelp":              [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_delTasksHistory":           [ ADMINISTRATOR ],
            "xmlrpc_refreshTasks":              [ ADMINISTRATOR, TESTER ],
            "xmlrpc_addCommentArchive":         [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_loadCommentsArchive":       [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_delCommentsArchive":        [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_backupRepo":                [ ADMINISTRATOR ],
            "xmlrpc_deleteBackupsRepo":         [ ADMINISTRATOR ],
            "xmlrpc_addLibraryRepo":            [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_addAdapterRepo":            [ ADMINISTRATOR, DEVELOPER ],
            "xmlrpc_setGenericAdapter":         [ ADMINISTRATOR, TESTER ],
            "xmlrpc_setGenericLibrary":         [ ADMINISTRATOR, TESTER ],
            "xmlrpc_setDefaultAdapterV2":       [ ADMINISTRATOR, TESTER ],
            "xmlrpc_setDefaultLibraryV2":       [ ADMINISTRATOR, TESTER ],
            "xmlrpc_moveDirRepo":               [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_moveFileRepo":              [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_exportTestVerdict":         [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_exportTestReport":          [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_prepareAssistant":          [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_generateAdapterFromWSDL":   [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_setDefaultVersionForTests": [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_genAllPackages":            [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_genAdapters":               [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_genLibraries":              [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_genSamples":                [ ADMINISTRATOR, LEADER, DEVELOPER ],
            "xmlrpc_refreshTestEnvironment" :   [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_exportTestDesign":          [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_disconnectAgent":           [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_cleanupLockFilesRepo":      [ ADMINISTRATOR ],
            "xmlrpc_createSnapshotTest":        [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_deleteSnapshotTest":        [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_restoreSnapshotTest":       [ ADMINISTRATOR, TESTER, DEVELOPER ],
            "xmlrpc_deleteAllSnapshotsTest":    [ ADMINISTRATOR ],
            "xmlrpc_disconnectProbe":           [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_downloadTestResult":        [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_downloadBackup":            [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_downloadClient":            [ ADMINISTRATOR, TESTER, DEVELOPER, LEADER ],
            "xmlrpc_uploadLogs":                [ ],
            "xmlrpc_shiftLocalTime":            [ ADMINISTRATOR, TESTER ],
            "xmlrpc_getImagePreview":           [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_getTestPreview":            [ ADMINISTRATOR, TESTER, LEADER ],
            "xmlrpc_deleteTestResult":          [ ADMINISTRATOR, LEADER ],
            "xmlrpc_killAllTasks":              [ ADMINISTRATOR ],
            "xmlrpc_cancelAllTasks":            [ ADMINISTRATOR ]
        }

        
XRR = None # singleton
def instance ():
    """
    Returns the singleton

    @return:
    @rtype:
    """
    return XRR
    
def initialize ():
    """
    Instance creation
    """
    global XRR
    XRR = XmlRpcRights()

    
def finalize ():
    """
    Destruction of the singleton
    """
    global XRR
    if XRR:
        XRR = None

