#!/usr/bin/python3
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2015 Denis Machard
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
Build the windows portable version with py2exe
"""

from distutils.core import setup
import py2exe
import datetime
import os
import sys
import platform

# Retrieve the version of the main file
from Main import __VERSION__
import Settings

# Initialize settings module
Settings.initialize()
settings = Settings.instance()

# prepare the build date
today = datetime.datetime.today()
buildYear = today.strftime("%Y")

print("Output: %s" % settings.dirExec)

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
        Copy the target
        """
        return Target(**self.__dict__)

    def __setitem__(self, name, value):
        """
        Set item on the dict
        """
        self.__dict__[name] = value

RT_BITMAP = 2
RT_MANIFEST = 24

# Continue with exe creation
mainIcon = "%s/%s/%s" % (  settings.dirExec,   settings.readValue( key = 'Common/icon-dir' ),settings.readValue( key =  'Common/icon-name' )  )
smallBmpInstaller = "%s/%s/small_installer.bmp" % (  settings.dirExec, settings.readValue( key = 'Common/icon-dir' )   )
rnFile = "%s/%s/releasenotes.txt" % (   settings.dirExec,  settings.readValue( key = 'Common/icon-dir' )  )
licenseFile = "%s/LICENSE-LGPLv21" % ( settings.dirExec )
historyFile = "%s/HISTORY" % ( settings.dirExec )
settingsFile = "%s" % settings.fileName
toolsFile = "%s" % settings.fileNameTools

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

	
Csvs_Path = "%s/Files/" % settings.dirExec
Csvs_Files = [f for dp, dn, filenames in os.walk(Csvs_Path) for f in filenames if os.path.splitext(f)[1] == '.csv']

Tpls_Path = "%s/Files/" % settings.dirExec
Tpls_Files = [f for dp, dn, filenames in os.walk(Tpls_Path) for f in filenames if os.path.splitext(f)[1] == '.tpl']


Mydata_files = [    
                    ( '', [ licenseFile ] ),
                    ( '', [ historyFile ] ),
                    ( '', [ mainIcon ] ) ,
                    ( 'Files', [ settingsFile ] ),
                    ( 'Files', [ toolsFile ] ),
                    ( '', [ smallBmpInstaller ] ),
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

for f in Csvs_Files:
    Mydata_files.append( ( 'Files', [ '%s/%s' % (Csvs_Path, f) ] ) ) 

for f in Tpls_Files:
    Mydata_files.append(  ( 'Files', [ '%s/%s' % (Tpls_Path, f) ] ) ) 
    
print("All files successfully prepared")
Main = Target(
    # We can extend or override the VersionInfo of the base class:
    version = __VERSION__,
    company_name = settings.readValue( key = 'Common/product-name' ),
    copyright = "Copyright %s © %s" % (settings.readValue( key = 'Common/product-name' ), buildYear),
    legal_copyright = "Copyright %s © %s" % (settings.readValue( key = 'Common/product-name' ), buildYear),
    description = settings.readValue( key = 'Common/name' ),
    
    product_version = __VERSION__,
    product_name = settings.readValue( key = 'Common/product-name' ),

    script="Main.py", # path of the main script

    # Allows to specify the basename of the executable, if different from 'Main'
    dest_base = settings.readValue( key = 'Common/acronym' ),

    # Icon resources:[(resource_id, path to .ico file), ...]
    icon_resources=[
                       (1, "%s\Resources\%s" % (settings.dirExec, settings.readValue( key = 'Common/icon-name' )) ), 
                    ]
    )

print("Target initialized")
py2exe_options = dict(
    packages = [],
    optimize=0,
    compressed=False, # uncompressed may or may not have a faster startup
    bundle_files=1,
    dist_dir='__build__',
    )
print("py2exe options prepared")

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
print("py2exe executed with success")

# adding folders
os.mkdir( "%s/__build__/ResultLogs" % settings.dirExec )
os.mkdir( "%s/__build__/Plugins" % settings.dirExec )
os.mkdir( "%s/__build__/Update" % settings.dirExec )
os.mkdir( "%s/__build__/Logs" % settings.dirExec )
os.mkdir( "%s/__build__/Tmp" % settings.dirExec )
os.mkdir( "%s/__build__/PyQt5" % settings.dirExec )
print("additionnal folders addeds")

# rename the __build__ folder if in portable mode
portable = settings.readValue( key = 'Common/portable' )
if portable == "True":
    os.rename( 
                "%s/__build__/" % settings.dirExec, 
                "%s/%s_%s_%s_Portable" % (settings.dirExec, settings.readValue( key = 'Common/acronym' ), 
											 __VERSION__, platform.architecture()[0]) 
            )
    
# Finalize settings
Settings.finalize()