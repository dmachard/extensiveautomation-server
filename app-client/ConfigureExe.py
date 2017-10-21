#!/usr/bin/python3
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

import datetime
import sys
import Settings


PORTABLE_VERSION=False
if "portable" in sys.argv: 
    PORTABLE_VERSION=True

# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# Reset settings with default values
if PORTABLE_VERSION:
    settings.setValue( key='Common/portable', value="True" )
else:
    settings.setValue( key='Common/portable', value="False" )

settings.setValue( key='Common/language', value='us_US' )

settings.setValue( key='Repositories/local-repo', value='Undefined' )
settings.setValue( key='TestArchives/download-directory', value='Undefined' )

settings.setValue( key='Server/addr-list', value='' )
settings.setValue( key='Server/last-addr', value='' )
settings.setValue( key='Server/last-username', value='tester' )
settings.setValue( key='Server/last-pwd', value='' )
settings.setValue( key='Server/port-data', value='443' )
settings.setValue( key='Server/port-api', value='443' )

settings.setValue( key='Editor/code-folding', value='True' )
settings.setValue( key='Editor/find-wrap', value='True' )

settings.setValue( key='Trace/level', value='INFO' )

settings.setValue( key='TestRun/auto-focus', value='True' )
settings.setValue( key='TestRun/auto-save', value='False' )
settings.setValue( key='TestRun/new-window', value='False' )
settings.setValue( key='TestRun/event-filter-pattern', value='^(?!DEBUG)' )
settings.setValue( key='TestRun/event-filter-column', value='4' )
settings.setValue( key='TestRun/default-tab-run', value='0' )

settings.setValue( key='TestRun/textual-selection-color', value='#ffffff' )
settings.setValue( key='TestRun/textual-text-selection-color', value='#ff3019' )


settings.setValue( key='Server/proxy-active', value='False' )
settings.setValue( key='Server/proxy-web-active', value='False' )
settings.setValue( key='Server/port-proxy-http', value='' )
settings.setValue( key='Server/addr-proxy-http', value='' )

# Writes any unsaved changes
settings.settings.sync()
settings.settingsTools.sync()

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

# Finalize settings
Settings.finalize()