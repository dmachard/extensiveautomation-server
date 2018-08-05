#!/usr/bin/python3
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

import datetime
import sys

from . import Settings


def run():
    # Initialize settings module
    Settings.initialize()
    settings = Settings.instance()

    # Reset settings with default values
    settings.setValue( key='Trace/level', value='INFO' )

    # Writes any unsaved changes
    settings.settings.sync()

    # read the main python file to change some constant
    fd = open( "%s/MyPlugin.py" % settings.dirExec ,"r")
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
        elif line.startswith("DEBUGMODE"):
            newLines.append( "DEBUGMODE=False\n" )
        else:
            newLines.append( line )

    # write changes
    fd = open( "%s/MyPlugin.py" % settings.dirExec ,"w")
    fd.writelines( "".join(newLines) )
    fd.close()

    # Finalize settings
    Settings.finalize()