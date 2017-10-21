#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2015 Denis Machard
# This file is part of the extensive testing project
# -------------------------------------------------------------------

"""
Module innosetup
"""

# import standard modules
import os
import sys
import platform

import Main
import Settings
from Libs import QtHelper

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

Settings.initialize()
settings = Settings.instance()

# destination folder
PACKAGE_DEST = sys.argv[1]

# path to innosetup ISCC.exe
INNOSETUP_COMPILER = 'C://Program Files (x86)//Inno Setup 5//ISCC.exe'

class InnoScript:
    """
    Class to create an innosetup script
    """
    def __init__ (self, pathName):
        """
        Constructor
        """
        self.scriptName = 'script_ino.iss'
        self.pathName = "%s\%s" % ( pathName, self.scriptName )
        self.path = pathName

    def create(self):
        """
        Create the script
        """
        appName = settings.readValue( key = 'Common/name' )
        appAcronym = settings.readValue( key = 'Common/acronym' )
        appVersion = Main.__VERSION__
        appAuthor = settings.readValue( key = 'Common/author' )

        print("InnoSetup script: %s" % self.pathName)

        ofi = open(self.pathName, "w")
        
        d = [ "[Setup]" ]
        d.append( "AppName=%s" % appName ) 
        d.append( "AppVersion=%s" % appVersion )
        d.append( "AppVerName=%s %s" % ( appName, appVersion ) )
        d.append( "AppPublisher=%s" % appAuthor )
        d.append( "AppPublisherURL=http://%s" % settings.readValue( key = 'Common/url' ) )
        d.append( "VersionInfoVersion=%s" % appVersion )
        d.append( "DefaultDirName={pf}\%s" % appName )
        d.append( "DefaultGroupName=\%s" % appName )
        d.append( "Compression=lzma" )
        d.append( "OutputDir=%s" % PACKAGE_DEST )
        d.append( "OutputBaseFilename=%s_%s_%s_Setup" % ( appAcronym, appVersion, platform.architecture()[0]) )
        d.append( "WizardSmallImageFile=small_installer.bmp" )
        d.append( "UninstallDisplayIcon={app}\%s.ico" % appAcronym.lower() )
        d.append( "LicenseFile=LICENSE-LGPLv21" )
        if platform.architecture()[0] == "64bit":
            d.append( "ArchitecturesInstallIn64BitMode=x64" )
        d.append( "" )

        d.append( "[Dirs]" )
        d.append( r'Name: "{app}\imageformats\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Update\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\ResultLogs\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Tmp\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Plugins\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Files\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Logs\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Externals\"; Permissions: users-modify' )
        d.append( "" )

        d.append( "[Files]" )
        for f in os.listdir(self.path):
            if f not in [ 'Externals', 'imageformats', 'Files', 'Logs', 'ResultLogs', 'Tmp', 'Plugins', 'Update', 'small_installer.bmp', self.scriptName ]:
                d.append( r'Source: "%s"; DestDir: "{app}"; Flags: ignoreversion' % f )
                
        for f in os.listdir("%s/Files/" % self.path):
            d.append( r'Source: "Files/%s"; DestDir: "{app}\Files\"; Flags: ignoreversion; Permissions: users-modify' % f) 

        # adding qt file
        # if sys.version_info < (3,):
        for f in os.listdir("%s/imageformats/" % self.path):
            d.append( r'Source: "imageformats/%s"; DestDir: "{app}\imageformats\"; Flags: ignoreversion; Permissions: users-modify' % f )
        d.append( "" )

        d.append( "[Icons]" )
        d.append( r'Name: "{group}\%s"; Filename:  "{app}\%s.exe"; WorkingDir: "{app}"; IconFilename: "{app}\%s.ico"' % \
            ( appName, appAcronym, appAcronym.lower() ) )
        d.append( r'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"; IconFilename: "{app}\%s.ico"' % (appName,appAcronym.lower()) )
        d.append( r'Name: "{commondesktop}\%s"; Filename: "{app}\%s.exe"; IconFilename: "{app}\%s.ico"' % \
            ( appName, appAcronym, appAcronym.lower() ) )
        d.append( r'Name: "{group}\Update"; Filename: "{app}\Update";' ) 
        d.append( r'Name: "{group}\Plugins"; Filename: "{app}\Plugins";' ) 
        d.append( '' )

        d.append( '[Run]' )
        d.append( r'Filename: {app}\releasenotes.txt; Description: View the release notes; Flags: postinstall shellexec skipifsilent' )
        d.append( r'Filename: "{app}\%s.exe"; Description: "Launch %s"; Flags: nowait postinstall skipifsilent' %  (appAcronym, appName) )
        d.append( "" )

        ofi.write( "\n".join(d) )
        ofi.close()

    def compile(self):
        """
        Compile the script innosetup
        """
        cmd = '"%s" "%s"' % (INNOSETUP_COMPILER, self.pathName)
        print("Running InnoSetup: %s" % cmd)
        errorlevel = os.system('"%s"' % cmd)
        print("InnoSetup returned errorlevel: %s" % errorlevel)

# Init the class, create the script and compile-it
if sys.version_info > (3,):
    script = InnoScript( pathName= "%s/__build__/" % QtHelper.dirExec() )
else:
    sub_dirs = os.listdir("build/")[0]
    script = InnoScript( pathName= "%s/Scripts/build/%s" % ( QtHelper.dirExec(), sub_dirs ) )
    
script.create()
script.compile()

# finalize settings
Settings.finalize()