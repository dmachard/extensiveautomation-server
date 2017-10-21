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

from distutils.core import setup
import platform
import py2exe
import datetime
import os
import sys

# import Settings
from . import Settings


class Target(object):
    """
    Target is the baseclass for all executables that are created.
    It defines properties that are shared by all of them.
    """
    def __init__(self, **kw):
        """
        """
        self.__dict__.update(kw)

    def copy(self):
        """
        """
        return Target(**self.__dict__)

    def __setitem__(self, name, value):
        """
        """
        self.__dict__[name] = value
        
def run(pluginName, pluginVersion): 
    """
    """
    # Initialize settings module
    Settings.initialize()
    settings = Settings.instance()

    # prepare the build date
    today = datetime.datetime.today()
    buildYear = today.strftime("%Y")
    
    # Continue with exe creation
    mainIcon = "%s/Resources/plugin.ico" % ( settings.dirExec )
    mainPng = "%s/Resources/plugin.png" % ( settings.dirExec )
    rnFile = "%s/Resources/releasenotes.txt" % ( settings.dirExec  )
    licenseFile = "%s/LICENSE-LGPLv21" % ( settings.dirExec )
    historyFile = "%s/HISTORY" % ( settings.dirExec )
    settingsFile = "%s" % settings.fileName
    configJson = "%s/config.json" % ( settings.dirExec )

    # Inspect all files to package
    Dlls_Path = "%s/Dlls/" % settings.dirExec
    Dlls_Files = []
    for dp, dn, filenames in os.walk(Dlls_Path):  
        if len(dn): Dlls_Files.extend( filenames )
    Dlls_Img_Files = []
    for dp, dn, filenames in os.walk(Dlls_Path): 
        if not len(dn): Dlls_Img_Files.extend( filenames )

    # to support 64 bits	
    Dlls64_Path = "%s/Dlls64/" % settings.dirExec
    Dlls64_Files = []
    for dp2, dn2, filenames2 in os.walk(Dlls64_Path):  
        if len(dn2): Dlls64_Files.extend( filenames2 )
    Dlls64_Img_Files = []
    for dp2, dn2, filenames2 in os.walk(Dlls64_Path): 
        if not len(dn2): Dlls64_Img_Files.extend( filenames2 )
    # end of support

    Mydata_files = [    
                        ( '', [ licenseFile ] ),
                        ( '', [ historyFile ] ),
                        ( '', [ mainIcon ] ) ,
                        ( '', [ mainPng ] ) ,
                        ( 'Core/Files', [ settingsFile ] ),
                        ( '', [ configJson ] ),
                        ( '', [ rnFile ] ),
                    ]
                    
    if platform.architecture()[0] == "64bit":
        for f in Dlls64_Files:
            Mydata_files.append( ( '', [ '%s/%s' % (Dlls64_Path, f) ] ) ) 
        for f in Dlls64_Img_Files:
            Mydata_files.append( ( 'imageformats', [ '%s/imageformats/%s' % (Dlls64_Path, f) ] ) ) 
    else:
        for f in Dlls_Files:
            Mydata_files.append( ( '', [ '%s/%s' % (Dlls_Path, f) ] ) ) 
        for f in Dlls_Img_Files:
            Mydata_files.append( ( 'imageformats', [ '%s/imageformats/%s' % (Dlls_Path, f) ] ) ) 
    
    Main = Target(
        # We can extend or override the VersionInfo of the base class:
        # version = __VERSION__,
        company_name = settings.readValue( key = 'Common/product-name' ),
        copyright = "Copyright %s © %s" % (settings.readValue( key = 'Common/product-name' ), buildYear),
        legal_copyright = "Copyright %s © %s" % (settings.readValue( key = 'Common/product-name' ), buildYear),
        description = settings.readValue( key = 'Common/name' ),
        
        # product_version = __VERSION__,
        product_name = settings.readValue( key = 'Common/product-name' ),

        script="MyPlugin.py", # path of the main script

        # Allows to specify the basename of the executable, if different from 'Main'
        dest_base = settings.readValue( key = 'Common/acronym' ),

        # Icon resources:[(resource_id, path to .ico file), ...]
        icon_resources=[
                           (1, "%s\Resources\plugin.ico" % settings.dirExec ), 
                        ]
        )
        
    py2exe_options = dict(
        packages = [],
        optimize=0,
        compressed=False, # uncompressed may or may not have a faster startup
        bundle_files=1,
        dist_dir='__build__',
        includes = ['PyQt4.QtNetwork']
        )
        
    # Some options can be overridden by command line options...
    setup(name="name",
          # console based executables
          console=[Main],

          data_files = Mydata_files,
          
          # windows subsystem executables (no console)
          windows=[],

          # py2exe options
          zipfile=None,
          options={"py2exe": py2exe_options},
          )
          
    # adding folders
    #  
    os.mkdir( "%s/__build__/Core/Logs" % (settings.dirExec) )
    os.rename( 
                "%s/__build__/" % settings.dirExec, 
                "%s/%s_%s_%s_%s" % (settings.dirExec, settings.readValue( key = 'Common/acronym' ),  
                                    pluginName, pluginVersion, platform.architecture()[0]) 
            )
            
    # Finalize settings
    Settings.finalize()