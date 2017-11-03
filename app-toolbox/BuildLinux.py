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

"""
Build binary for linux
"""

import sys

try:
    xrange
except NameError: # support python3
    xrange = range

import cx_Freeze
from cx_Freeze import setup, Executable
from Libs import Settings
import os
import datetime

# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# Reset settings with default values
Settings.set( section='Trace', key='level', value='INFO' )

Settings.set( section='Server', key='ip', value='127.0.0.1' )
Settings.set( section='Server', key='port', value='443' )
Settings.set( section='Server', key='port-proxy-http', value='' )
Settings.set( section='Server', key='addr-proxy-http', value='' )
Settings.set( section='Server', key='proxy-active', value='False' )
Settings.set( section='Server', key='connect-on-startup', value='False' )

# remove all tool sections
for i in xrange(50):
    Settings.removeSection('Tool_%s' % i )

with open("%s/settings.ini" % Settings.getDirExec(), 'wb') as configfile:
    Settings.instance().write(configfile)

# read the main python file to change some constant
fd = open( "%s/Systray.py" % Settings.getDirExec() ,"r")
mainLines = fd.readlines()
fd.close()

# prepare the build date
today = datetime.datetime.today()
buildTime = today.strftime("%d/%m/%Y %H:%M:%S")
buildYear = today.strftime("%Y")

# parse all lines
newLines = []
for line in mainLines:
    if line.startswith("__END__"):
        newLines.append( "__END__=\"%s\"\n" % buildYear )
    elif line.startswith("__BUILDTIME__"):
        newLines.append( "__BUILDTIME__=\"%s\"\n" % buildTime )
    else:
        newLines.append( line )

# write changes
fd = open( "%s/Systray.py" % Settings.getDirExec() ,"w")
fd.writelines( "".join(newLines) )
fd.close()

# Continue with exe creation and inspect all files to package
mainIcon = "%s/Resources/%s.ico" % ( Settings.getDirExec(), Settings.get( section = 'Common', key='acronym' ).lower() )
rnFile = "%s/releasenotes.txt" % Settings.getDirExec()
settingsFile = "%s/settings.ini" % Settings.getDirExec()
versionFile = "%s/VERSION" % Settings.getDirExec()

# adding java setup
Java_Path = "%s/Bin/Java/" % Settings.getDirExec()
Java_Files = [ f for f in os.listdir(Java_Path) if os.path.isfile(os.path.join(Java_Path,f)) ]

# adding sikuli files
Sikuli_Path = "%s/Bin/Sikuli/" % Settings.getDirExec()
Sikuli_Files = [ f for f in os.listdir(Sikuli_Path) if os.path.isfile(os.path.join(Sikuli_Path,f)) ]

# adding selenium
Selenium_Path = "%s/Bin/Selenium/" % Settings.getDirExec()
Selenium_Files = [ f for f in os.listdir(Selenium_Path) if os.path.isfile(os.path.join(Selenium_Path,f)) ]
Selenium2_Path = "%s/Bin/Selenium2/" % Settings.getDirExec()
Selenium2_Files = [ f for f in os.listdir(Selenium2_Path) if os.path.isfile(os.path.join(Selenium2_Path,f)) ]

# adding apk
Apk_Path = "%s/Bin/Apk/" % Settings.getDirExec()
Apk_Files = [ f for f in os.listdir(Apk_Path) if os.path.isfile(os.path.join(Apk_Path,f)) ]

# adding ddl
Dlls_Path = "%s/Dlls/" % Settings.getDirExec()
Dlls_Files = [ f for dp, dn, filenames in os.walk(Dlls_Path) for f in filenames]

# adding license
licenseFile = "%s/LICENSE-LGPLv21" % ( Settings.getDirExec() )
historyFile = "%s/HISTORY" % ( Settings.getDirExec() )

smallBmpInstaller = "%s/Resources/small_installer.bmp" % Settings.getDirExec()

includeFiles = [   
                    (mainIcon,'%s.ico' % Settings.get( section = 'Common', key='acronym' ).lower() ),
                    (settingsFile, 'settings.ini'),
                    (versionFile, 'VERSION'),
                    (rnFile, 'releasenotes.txt'),
                    (smallBmpInstaller, 'small_installer.bmp'),
                    (licenseFile, 'LICENSE-LGPLv21'),
                    (historyFile, 'HISTORY')
                ]

# ddl
for f in Dlls_Files:
    includeFiles.append( ('%s/%s' % (Dlls_Path, f), f ), ) 
    
# apk
for f in Apk_Files:
    includeFiles.append( ( 'Bin/Apk/', [ '%s/%s' % (Apk_Path, f) ] ) ) 

# selenium
for f in Selenium_Files:
    includeFiles.append( ('%s/%s' % (Selenium_Path, f), 'Bin/Selenium/%s' % f ), ) 
    
# selenium2
for f in Selenium2_Files:
    includeFiles.append( ('%s/%s' % (Selenium2_Path, f), 'Bin/Selenium2/%s' % f ), ) 

# java
for f in Java_Files:
    includeFiles.append( ('%s/%s' % (Java_Path, f), 'Bin/Java/%s' % f ), ) 

# sikuli
for f in Sikuli_Files:
    includeFiles.append( ('%s/%s' % (Sikuli_Path, f), 'Bin/Sikuli/%s' % f ), ) 

print(includeFiles)


# Prepare the build options
base = None
if sys.platform == "win32":
    base = "Win32GUI"

if cx_Freeze.__version__.startswith("5."):
    buildOptions =   dict( 
                                include_files = includeFiles
                         )
else:
    buildOptions =   dict( include_files = includeFiles,
                                optimize = 2,
                                compressed = True ,  
                                create_shared_zip  = False,
                                append_script_to_exe = True,
                                include_in_shared_zip = False
                         )

# Prepare the setup options
setup(
        version = Settings.getVersion(),
        options =  dict(build_exe = buildOptions),
        description=Settings.get( section = 'Common', key='name'  ),
        name=Settings.get( section = 'Common', key='name' ),
        executables = [  
                        Executable(
                            script="../Systray.py",
                            base = base,
                            icon = "../Resources/%s.ico" % Settings.get( section = 'Common', key='acronym' ).lower()    ,
                            targetName="%s.exe" % Settings.get( section = 'Common', key='acronym' )                 
                        )
        
                ]
    )

# Create folders 
sub_dirs = os.listdir("build/")[0]
print("Makes dirs Tmp and Logs")
os.mkdir( "build/%s/Tmp" % sub_dirs )
os.mkdir( "build/%s/Logs" % sub_dirs )
os.mkdir( "build/%s/Plugins" % sub_dirs )

# Finalize settings
Settings.finalize()