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

"""
Lib to build as executable
"""

import sys
import os
import datetime

from cx_Freeze import setup, Executable
    
# Retrieve the version of the main file
from Main import __VERSION__
import Settings


# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

print("1. Preparing settings file")

# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# Reset settings with default values
settings.setValue( key='Common/local-repo', value='Undefined' )
settings.setValue( key='Common/language', value='us_US' )

settings.setValue( key='Server/addr-list', value='' )
settings.setValue( key='Server/last-addr', value='' )
settings.setValue( key='Server/last-username', value='tester' )
settings.setValue( key='Server/last-pwd', value='' )

settings.setValue( key='Editor/code-folding', value='True' )
settings.setValue( key='Editor/find-wrap', value='True' )

settings.setValue( key='Trace/level', value='INFO' )

settings.setValue( key='TestRun/auto-focus', value='True' )
settings.setValue( key='TestRun/auto-save', value='False' )
settings.setValue( key='TestRun/new-window', value='False' )
settings.setValue( key='TestRun/event-filter-pattern', value='' )
settings.setValue( key='TestRun/event-filter-column', value='4' )
settings.setValue( key='TestRun/default-tab-run', value='0' )

settings.setValue( key='TestRun/textual-selection-color', value='#ffffff' )
settings.setValue( key='TestRun/textual-text-selection-color', value='#ff3019' )

settings.setValue( key='Server/proxy-active', value='0' )
settings.setValue( key='Server/port-proxy-http', value='' )
settings.setValue( key='Server/addr-proxy-http', value='' )

# Writes any unsaved changes
settings.settings.sync()
settings.settingsTools.sync()

print("2. Adding build time and date")

# read the main python file to change some constant
fd = open( "%s/Main.py" % settings.dirExec ,"r")
mainLines = fd.readlines()
fd.close()

# prepare the build date
today = datetime.datetime.today()
buildTime = today.strftime("%d/%m/%Y %H:%M:%S")
buildYear = today.strftime("%Y")

# parse all lines
newLines = []
for line in mainLines:
    if line.startswith("WORKSPACE_OFFLINE"):
        newLines.append( "WORKSPACE_OFFLINE=False\n" )
    elif line.startswith("QT_WARNING_MODE"):
        newLines.append( "QT_WARNING_MODE=False\n" )
    elif line.startswith("__END__"):
        newLines.append( "__END__=\"%s\"\n" % buildYear )
    elif line.startswith("__BUILDTIME__"):
        newLines.append( "__BUILDTIME__=\"%s\"\n" % buildTime )
    elif line.startswith("REDIRECT_STD"):
        newLines.append( "REDIRECT_STD=True\n" )
    else:
        newLines.append( line )

# write changes
fd = open( "%s/Main.py" % settings.dirExec ,"w")
fd.writelines( "".join(newLines) )
fd.close()

print("3. Preparing ressources")
# Continue with exe creation
mainIcon = "%s/%s/%s" % (   
                            settings.dirExec,
                            settings.readValue( key = 'Common/icon-dir' ),
                            settings.readValue( key =  'Common/icon-name' )
                        )
smallBmpInstaller = "%s/%s/small_installer.bmp" % (   
                            settings.dirExec,
                            settings.readValue( key = 'Common/icon-dir' ) 
                            )

rnFile = "%s/%s/releasenotes.txt" % (   
                            settings.dirExec,
                            settings.readValue( key = 'Common/icon-dir' ),
                        )

licenseFile = "%s/LICENSE-LGPLv21" % (   
                            settings.dirExec,
                            )
historyFile = "%s/HISTORY" % (   
                            settings.dirExec,
                            )
                            
settingsFile = "%s" % settings.fileName
toolsFile = "%s" % settings.fileNameTools

Csvs_Path = "%s/Files/" % settings.dirExec
Csvs_Files = [f for dp, dn, filenames in os.walk(Csvs_Path) for f in filenames if os.path.splitext(f)[1] == '.csv']

Tpls_Path = "%s/Files/" % settings.dirExec
Tpls_Files = [f for dp, dn, filenames in os.walk(Tpls_Path) for f in filenames if os.path.splitext(f)[1] == '.tpl']


includeFiles = [    (mainIcon, settings.readValue( key =  'Common/icon-name' ) ) ,
                    (settingsFile, 'Files/settings.ini'),
                    (toolsFile, 'Files/tools.ini'),
                    (smallBmpInstaller, 'small_installer.bmp'),
                    (rnFile, 'releasenotes.txt'),
                    (licenseFile, 'LICENSE-LGPLv21'),
                    (historyFile, 'HISTORY')
                ]

for f in Csvs_Files:
    includeFiles.append( ('%s/%s' % (Csvs_Path, f), 'Files/%s' % f ) ) 

for f in Tpls_Files:
    includeFiles.append( ('%s/%s' % (Tpls_Path, f), 'Files/%s' % f ) ) 

print("4. Preparing build options")
# Prepare the build options
base = None
if sys.platform == "win32":
    base = "Win32GUI"
    exeName = "%s.exe" % settings.readValue( key = 'Common/acronym' )       
else:
    exeName = "%s" % settings.readValue( key = 'Common/acronym' )   

buildOptions =   dict( 
                            include_files = includeFiles,
                            # optimize = 2,
                            # compressed = True ,  
                            # create_shared_zip  = True,
                            # append_script_to_exe = False,
                            # include_in_shared_zip = True,
                     )
                     
print("5. Building executable")
# Prepare the setup options
setup(
        version = __VERSION__,
        options =  dict(build_exe = buildOptions),
        description=str(settings.readValue( key = 'Common/name' )),
        name=str(settings.readValue( key = 'Common/name' )),
        executables = [  
                        Executable(
                            script="%s/Main.py" % settings.dirExec,
                            base = base,
                            icon = "%s/Resources/%s.ico" % ( settings.dirExec, settings.readValue( key = 'Common/acronym' )),
                            targetName= exeName 
                        )
                ]
    )

print("6. Adding additional folders")
# Create folders 
os.mkdir( "__build__/ResultLogs"  )
os.mkdir( "__build__/Update"  )
os.mkdir( "__build__/Logs" )
os.mkdir( "__build__/Plugins" )
os.mkdir( "__build__/Tmp"  )

# Finalize settings
Settings.finalize()