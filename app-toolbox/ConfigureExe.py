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

"""
Configure binary
"""

import datetime
import os
import sys

from Libs import Settings

PORTABLE_VERSION=False
if "portable" in sys.argv: 
    PORTABLE_VERSION=True

    
# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# Reset settings with default values
if PORTABLE_VERSION:
    Settings.set( section='Common', key='portable', value="True" )
else:
    Settings.set( section='Common', key='portable', value="False" )
    
Settings.set( section='Trace', key='level', value='INFO' )

Settings.set( section='Server', key='ip', value='127.0.0.1' )
Settings.set( section='Server', key='port', value='443' )
Settings.set( section='Server', key='port-xmlrpc', value='443' )
Settings.set( section='Server', key='port-proxy-http', value='' )
Settings.set( section='Server', key='addr-proxy-http', value='' )
Settings.set( section='Server', key='proxy-active', value='False' )
Settings.set( section='Server', key='connect-on-startup', value='False' )

Settings.set( section='Server', key='reconnect-on-inactivity', value='True' )
Settings.set( section='Server', key='reconnect-on-timeout', value='True' )
Settings.set( section='Server', key='reconnect-on-refused', value='True' )
Settings.set( section='Server', key='reconnect-on-disconnect', value='True' )
Settings.set( section='Server', key='reconnect-on-error', value='True' )

# remove all tool sections
for i in range(50):
    Settings.removeSection('Tool_%s' % i )

# Writes any unsaved changes
with open("%s/settings.ini" % Settings.getDirExec(), 'w') as configfile:
    Settings.instance().write(configfile)

# read the systray python file to change some constant
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
    elif line.startswith("REDIRECT_STD"):
        newLines.append( "REDIRECT_STD=True\n" )
    else:
        newLines.append( line )

# write changes
fd = open( "%s/Systray.py" % Settings.getDirExec() ,"w")
fd.writelines( "".join(newLines) )
fd.close()

# Finalize settings
Settings.finalize()