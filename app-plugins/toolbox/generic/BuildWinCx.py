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
Lib to build as executable
"""

import platform
import sys
import os
import datetime

from cx_Freeze import setup, Executable
    
# import Settings
from . import Settings

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

def run(pluginName, pluginVersion): 
    """
    """
    # Initialize settings module
    Settings.initialize()
    settings = Settings.instance()

    # prepare the build date
    today = datetime.datetime.today()
    buildTime = today.strftime("%d/%m/%Y %H:%M:%S")
    buildYear = today.strftime("%Y")

    # Continue with exe creation
    mainIcon = "%s/Resources/plugin.ico" % ( settings.dirExec )
    mainIconPng = "%s/Resources/plugin.png" % ( settings.dirExec )
    rnFile = "%s/Resources/releasenotes.txt" % ( settings.dirExec  )
    licenseFile = "%s/LICENSE-LGPLv21" % ( settings.dirExec )
    historyFile = "%s/HISTORY" % ( settings.dirExec )
    configFile = "%s/CONFIG.json" % ( settings.dirExec )
    settingsFile = "%s" % settings.fileName
    
    msvcpDll = "%s/Core/Dlls/msvcp100.dll" % ( settings.dirExec )
    msvcrDll  = "%s/Core/Dlls/msvcr100.dll" % ( settings.dirExec )
    msvcpDll64 = "%s/Core/Dlls/msvcp100.dll" % ( settings.dirExec )
    msvcrDll64  = "%s/Core/Dlls/msvcr100.dll" % ( settings.dirExec )
    
    # Inspect all files to package
    Mydata_files = [    (licenseFile, 'LICENSE-LGPLv21' ) ,
                        (historyFile, 'HISTORY'),
                        (mainIcon, 'plugin.ico'),
                        (mainIconPng, 'plugin.png'),
                        (settingsFile, 'Core/Files/settings.ini'),
                        (rnFile, 'releasenotes.txt'),
                        (configFile, 'config.json'),
                    ]
    if platform.architecture()[0] == "64bit":
        Mydata_files.extend( [(msvcpDll64, 'msvcp100.dll'), (msvcrDll64, 'msvcr100.dll') ] )
    else:
        Mydata_files.extend( [(msvcpDll, 'msvcp100.dll'), (msvcrDll, 'msvcr100.dll') ] )
        
    # Prepare the build options  
    base = None
    buildOptions =   dict(	include_files = Mydata_files,
                            optimize = 2,
                            compressed = True,
                            # create_shared_zip  = True,
                            append_script_to_exe = True,
                            include_in_shared_zip = True,
                            build_exe = "%s/build/%s_%s_%s_%s" % (settings.dirExec, 
                                                                settings.readValue( key = 'Common/acronym' ), 
                                                                pluginName, pluginVersion, platform.architecture()[0])
                        )            

    setup(
            version = pluginVersion,
            options =  dict(build_exe = buildOptions),
            executables = [	Executable("%s/MyPlugin.py" % settings.dirExec, 
                                        base = base, targetName="%s_%s.exe" % ( settings.readValue( key = 'Common/acronym' ), pluginName ) 
                                       )
                            ]
        )

    # adding folders
    os.mkdir( "%s/build/%s_%s_%s_%s/Core/Logs" % (settings.dirExec, settings.readValue( key = 'Common/acronym' ), 
                                                pluginName, pluginVersion, platform.architecture()[0]) )

    # Finalize settings
    Settings.finalize()