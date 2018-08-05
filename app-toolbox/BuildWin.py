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


"""
Build binary for windows avec py2exe
"""

from distutils.core import setup
import py2exe
import datetime
import os
import platform

from Libs import Settings

# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# prepare the build date
today = datetime.datetime.today()
buildYear = today.strftime("%Y")

class Target(object):
    """
    Target is the baseclass for all executables that are created.
    It defines properties that are shared by all of them.
    """
    def __init__(self, **kw):
        """
        Constructor
        """
        self.__dict__.update(kw)

    def copy(self):
        """
        Copy the object
        """
        return Target(**self.__dict__)

    def __setitem__(self, name, value):
        """
        Set item in the dict
        """
        self.__dict__[name] = value

RT_BITMAP = 2
RT_MANIFEST = 24


# Continue with exe creation
mainIcon = "%s/Resources/%s.ico" % ( Settings.getDirExec(), Settings.get( section = 'Common', key='acronym' ).lower() )
rnFile = "%s/releasenotes.txt" % Settings.getDirExec()
settingsFile = "%s/settings.ini" % Settings.getDirExec()
versionFile = "%s/VERSION" % Settings.getDirExec()

# Inspect all files to package

# adding java8 setup
Java8_Path = "%s/Bin/Java8/" % Settings.getDirExec()
Java8_Files = [ f for f in os.listdir(Java8_Path) if os.path.isfile(os.path.join(Java8_Path,f)) ]

# adding sikuli files
Sikuli_Path = "%s/Bin/Sikuli/" % Settings.getDirExec()
Sikuli_Files = [ f for f in os.listdir(Sikuli_Path) if os.path.isfile(os.path.join(Sikuli_Path,f)) ]

# adding selenium
Selenium3_Path = "%s/Bin/Selenium3/" % Settings.getDirExec()
Selenium3_Files = [ f for f in os.listdir(Selenium3_Path) if os.path.isfile(os.path.join(Selenium3_Path,f)) ]

Selenium2_Path = "%s/Bin/Selenium2/" % Settings.getDirExec()
Selenium2_Files = [ f for f in os.listdir(Selenium2_Path) if os.path.isfile(os.path.join(Selenium2_Path,f)) ]

# adding adb
Adb_Path = "%s/Bin/Adb/" % Settings.getDirExec()
Adb_Files = [ f for f in os.listdir(Adb_Path) if os.path.isfile(os.path.join(Adb_Path,f)) ]

# system
Dlls_Path = "%s/Dlls/" % Settings.getDirExec()
Dlls_Files = []
for dp, dn, filenames in os.walk(Dlls_Path):  
    if len(dn): Dlls_Files.extend( filenames )
Dlls_Img_Files = []
for dp, dn, filenames in os.walk(Dlls_Path): 
    if not len(dn): Dlls_Img_Files.extend( filenames )
    
# to support 64 bits	
Dlls64_Path = "%s/Dlls64/" % Settings.getDirExec()
Dlls64_Files = []
for dp2, dn2, filenames2 in os.walk(Dlls64_Path):  
    Dlls64_Files.extend( filenames2 )
# end of support

# adding license
licenseFile = "%s/LICENSE-LGPLv21" % ( Settings.getDirExec() )
historyFile = "%s/HISTORY" % Settings.getDirExec()

smallBmpInstaller = "%s/Resources/small_installer.bmp" % Settings.getDirExec()

Mydata_files = [    
                    ( '', [ licenseFile ] ),
                    ( '', [ mainIcon ] ) ,
                    ( '', [ settingsFile ] ),
                    ( '', [ smallBmpInstaller ] ),
                    ( '', [ rnFile ] ),
                    ( '', [ versionFile ] ),
                    ( '', [ historyFile ] )
                ]
if platform.architecture()[0] == "64bit":
	for f in Dlls64_Files:
		Mydata_files.append( ( '', [ '%s/%s' % (Dlls64_Path, f) ] ) ) 
else:
    for f in Dlls_Files:
        Mydata_files.append( ( '', [ '%s/%s' % (Dlls_Path, f) ] ) ) 
for f in Dlls_Img_Files:
    Mydata_files.append( ( 'imageformats', [ '%s/imageformats/%s' % (Dlls_Path, f) ] ) ) 

# adb
for f in Adb_Files:
    Mydata_files.append( ( 'Bin/Adb/', [ '%s/%s' % (Adb_Path, f) ] ) ) 

# selenium
for f in Selenium3_Files:
    Mydata_files.append( ( 'Bin/Selenium3/', [ '%s/%s' % (Selenium3_Path, f) ] ) ) 
    
# selenium2
for f in Selenium2_Files:
    Mydata_files.append( ( 'Bin/Selenium2/', [ '%s/%s' % (Selenium2_Path, f) ] ) ) 

    
# java 8
for f in Java8_Files:
    Mydata_files.append( ( 'Bin/Java8/', [ '%s/%s' % (Java8_Path, f) ] ) ) 
    
# sikuli
for f in Sikuli_Files:
    Mydata_files.append( ( 'Bin/Sikuli', [ '%s/%s' % (Sikuli_Path, f) ] ) ) 
    
    
Main = Target(
    # We can extend or override the VersionInfo of the base class:
    version = Settings.getVersion(),
    company_name = Settings.get( section = 'Common', key='name'  ),
    copyright = "Copyright %s © %s" % (Settings.get( section = 'Common', key='name'  ), buildYear),
    legal_copyright = "Copyright %s © %s" % (Settings.get( section = 'Common', key='name'  ), buildYear),
    description = Settings.get( section = 'Common', key='name'  ),
    
    product_version = Settings.getVersion(),
    product_name = Settings.get( section = 'Common', key='name'  ),

    script="Systray.py", # path of the main script

    # Allows to specify the basename of the executable, if different from 'Main'
    dest_base = Settings.get( section = 'Common', key='acronym'  ),

    # Icon resources:[(resource_id, path to .ico file), ...]
    icon_resources=[
                       (1, "%s\Resources\%s.ico" % (Settings.getDirExec(), Settings.get( section = 'Common', key='acronym'  ).lower() ) ), 
                    ]
    )


py2exe_options = dict(
    packages = [ ],
    optimize=0,
    compressed=False, # uncompressed may or may not have a faster startup
    bundle_files=3,
    dist_dir='__build__',
    )


# Some options can be overridden by command line options...
setup(name="name",
      # console based executables
      console=[],

      data_files = Mydata_files,
      
      # windows subsystem executables (no console)
      windows=[Main],

      # py2exe options
      zipfile=None,
      options={"py2exe": py2exe_options},
      )

# adding folders
os.mkdir( "%s/__build__/Tmp" % Settings.getDirExec() )
os.mkdir( "%s/__build__/Logs" % Settings.getDirExec() )
os.mkdir( "%s/__build__/Plugins" % Settings.getDirExec() )

# rename the __build__ folder if in portable mode
portable = Settings.get( section = 'Common', key='portable'  )
if portable == "True":
    os.rename( 
                "%s/__build__/" % Settings.getDirExec(), 
                "%s/%s_%s_%s_Portable" % (Settings.getDirExec(), Settings.get( section = 'Common', key='acronym'  ), 
                                          Settings.getVersion(), platform.architecture()[0] ) 
            )
    
# Finalize settings
Settings.finalize()