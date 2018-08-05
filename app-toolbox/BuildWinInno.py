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
Build installer for windows
"""

from Libs import QtHelper, Settings
import os
import sys
import platform

Settings.initialize()
settings = Settings.instance()

# destination folder
PACKAGE_DEST = sys.argv[1]
SRC_FROM = sys.argv[2]

print(PACKAGE_DEST)
print(SRC_FROM)

# path to innosetup ISCC.exe
INNOSETUP_COMPILER = 'C://Program Files (x86)//Inno Setup 5//ISCC.exe'

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

Java8_Bin = None
Wireshark_Bin = None

VERSION_JAVA            =   "8u161"
VERSION_SIKULIX         =   "1.1.1"
VERSION_SELENIUM3       =   "3.9.0"
VERSION_SELENIUM2       =   "2.53.1"
VERSION_ADB             =   "1.0.39"

class InnoScript(object):
    """
    Inno script object
    """
    def __init__ (self, pathName):
        """
        Constructor
        """
        self.scriptName = 'script_ino.iss'
        self.pathName = "%s\%s" % ( pathName, self.scriptName )
        self.path = pathName
        
    def listdir(self, mainPath, subPath):
        """
        List all files and append it in a list with inno format
        """
        r = []
        for f in os.listdir( "%s/%s" % (mainPath, subPath) ):
            if os.path.isfile( "%s/%s/%s" % (mainPath,subPath,f) ):
                r.append( r'Source: "%s/%s"; DestDir: "{app}\%s\"; Flags: ignoreversion; Permissions: users-modify' % (subPath,f, subPath) )
            else:
                r.extend( self.listdir( mainPath, "/%s/%s" % (subPath, f)) )
        return r
        
    def create(self):
        """
        Create the inno file
        """
        appName = Settings.get( section = 'Common', key='name' )
        appAcronym = Settings.get( section = 'Common', key='acronym' )
        appVersion = Settings.getVersion()
        appAuthor = Settings.get( section = 'Common', key='author' )

        print("InnoSetup script: %s" % self.pathName)
        
        ofi = open(self.pathName, "w")
        
        d = [ r"[Setup]" ]
        d.append( r"AppName=%s" % appName )
        d.append( r"AppVersion=%s" % appVersion )
        d.append( r"AppVerName=%s %s" % ( appName, appVersion ) )
        d.append( r"AppPublisher=%s" % appAuthor )
        d.append( "AppPublisherURL=https://%s" %  Settings.get( section = "Common", key="url" ) )
        d.append( r"VersionInfoVersion=%s" % appVersion )
        d.append( r"DefaultDirName={pf}\%s" % appName )
        d.append( r"DefaultGroupName=\%s" % appName )
        d.append( r"Compression=lzma" )
        d.append( r"OutputDir=%s" % PACKAGE_DEST )
        d.append( r"OutputBaseFilename=%s_%s_%s_Setup" % ( appAcronym, appVersion, platform.architecture()[0]  ) )
        d.append( r"WizardSmallImageFile=small_installer.bmp" )
        d.append( r"UninstallDisplayIcon={app}\%s.ico" % appAcronym.lower() )
        d.append( r"LicenseFile=LICENSE-LGPLv21" )
        d.append( r"PrivilegesRequired=admin" )
        if platform.architecture()[0] == "64bit":
            d.append( "ArchitecturesInstallIn64BitMode=x64" )
        d.append( "" )

        d.append( r"[Dirs]" )
        d.append( r'Name: "{app}\imageformats\"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Bin"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Tmp"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Logs"; Permissions: users-modify' )
        d.append( r'Name: "{app}\Plugins"; Permissions: users-modify' )
        d.append( "" )
        
        # components to install, update version on changes
        d.append( r"[Components]" )
        d.append( r'Name: "main"; Description: "Engine"; Types: full compact custom; Flags: fixed;' )
        d.append( r'Name: "java8"; Description: "Java %s"; Types: full ;' % VERSION_JAVA )
        d.append( r'Name: "sikulix"; Description: "SikuliX %s"; Types: full;' % VERSION_SIKULIX )
        d.append( r'Name: "selenium3"; Description: "Selenium %s"; Types: full;' % VERSION_SELENIUM3 )
        d.append( r'Name: "selenium2"; Description: "Selenium %s"; Types: full;' % VERSION_SELENIUM2 )
        d.append( r'Name: "adb"; Description: "Android Debug Bridge %s"; Types: full;' % VERSION_ADB )
        
        d.append( r"[Files]" )
        
        d.extend( self.listdir( self.path, "") )
        
        # adding java 8
        for f in os.listdir("%s/Bin/Java8" % self.path):
            if os.path.isfile( "%s/Bin/Java8/%s" % (self.path, f) ):
                Java8_Bin = f
        if Java8_Bin is None: raise Exception("no java8 binary")
        

        d.append( "" )
        
        d.append( r"[Tasks]" )
        d.append( r'Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Components: main' )
        d.append( r'Name: startuplink; Description: "Create a &startup link"; GroupDescription: "Additional links:"; Components: main' )

        d.append( r"[Icons]" )
        d.append( r'Name: "{group}\%s"; Filename: "{app}\%s.exe"; WorkingDir: "{app}"; IconFilename: "{app}\%s.ico"' % \
            ( appName, appAcronym, appAcronym.lower() ) )
        d.append( r'Name: "{group}\Uninstall %s"; Filename: "{uninstallexe}"; IconFilename: "{app}\%s.ico"' % (appName,appAcronym.lower()) )
        d.append( r'Name: "{commondesktop}\%s"; Filename: "{app}\%s.exe"; IconFilename: "{app}\%s.ico"; Components: main; Tasks: desktopicon' % \
            ( appName, appAcronym, appAcronym.lower() ) )
        d.append( r'Name: "{commonstartup}\%s"; Filename: "{app}\%s.exe"; IconFilename: "{app}\%s.ico"; Components: main; Tasks: startuplink' % \
            ( appName, appAcronym, appAcronym.lower() ) )
        d.append( r'Name: "{group}\Plugins"; Filename: "{app}\Plugins";' ) 
        d.append( '' )

        d.append( r"[Run]" )
        d.append( r'Filename: {app}\Bin\Java8/%s; Parameters: "/s"; StatusMsg: "Installing Java 8..."; Components: java8;' % Java8_Bin )
        d.append( r'Filename: {app}\releasenotes.txt; Description: View the release notes; Flags: postinstall shellexec skipifsilent; Components: main;' )
        d.append( r'Filename: "{app}\%s.exe"; Description: "Launch %s"; Flags: nowait postinstall skipifsilent; Components: main;' %  (appAcronym, appName) )
        d.append( "" )

        ofi.write( "\n".join(d) )
        ofi.close()

    def compile(self):
        """
        Compile the ino file
        """
        cmd = '"%s" "%s"' % (INNOSETUP_COMPILER, self.pathName)
        print("Running InnoSetup: %s" % cmd)
        errorlevel = os.system('"%s"' % cmd)
        print("InnoSetup returned errorlevel: %s" % errorlevel)

# Init the class, create the script and compile-it
script = InnoScript( pathName= SRC_FROM )
script.create()
script.compile()

Settings.finalize()