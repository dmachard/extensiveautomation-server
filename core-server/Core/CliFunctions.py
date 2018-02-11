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

from Libs import  Settings, Logger

import sys
import os
import signal
import subprocess

import requests
import json
import hashlib

class CliFunctions(Logger.ClassLogger):
    """
    """
    def __init__(self, parent):
        """
        """
        self.parent=parent
        
    def deployclients(self, portable=False):
        """
        Reconstruct symlinks for clients, agents and probe from commande line
        """
        if portable:
            sys.stdout.write( "Deploying portable clients...")
        else:
            sys.stdout.write( "Deploying clients...")
        
        # remove all symbolic links
        self.trace('Removing client symbolic links...')
        # try:
        if portable:
            try:
                os.unlink('%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                Settings.get( 'Misc', 'client-win-portable' )) )
            except Exception as e:
                pass
            try:
                os.unlink('%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                            Settings.get( 'Misc', 'client-win-portable' )) )
            except Exception as e:
                pass
        else:
            try:
                os.unlink('%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                            Settings.get( 'Misc', 'client-win' )) )
            except Exception as e:
                pass
            try:
                os.unlink('%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                            Settings.get( 'Misc', 'client-win' )) )
            except Exception as e:
                pass
        # except Exception as e:
            # pass
            
           
        try:
            if portable:
                pass
            else:
                os.unlink('%s/%s/linux2/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), 
                                    Settings.get( 'Misc', 'client-linux' )) )
        except Exception as e:
            pass

        # add symbolic links for client 32 bits
        # create the symbolic link for the window package
        latestPkg = (0,0,0)
        latestPkgName = None
        try:
            for pkg in os.listdir( '%s/%s/win32/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' )) ):
                # ExtensiveTestingClient_11.0.0_64bit_Setup.exe
                pkg_split = pkg.split("_")
                if len(pkg_split) != 4: # ignore all bad files
                    continue
                else:
                    (n, v, a, t) = pkg_split
                if portable and t.lower() != 'portable.zip':
                    continue
                if not portable and t.lower() != 'setup.exe':
                    continue
                ver = v.split(".")
                digits = map( int, ver )
                if tuple(digits) > latestPkg:
                    latestPkg = tuple(digits)
                    latestPkgName = pkg
        except Exception as e:
            self.error("unable to find the latest client windows version: %s" % str(e) )

        if latestPkgName is None:
            sys.stdout.write( " [No windows client 32-bit]" )
            self.trace('No win 32-bit client detected')
        else:
            sys.stdout.write( "(%s)" % latestPkgName)
            self.trace('Creating symbolic link for the latest windows client...')
            if portable:
                os.symlink(
                            '%s/%s/win32/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), latestPkgName ),
                            '%s/%s/win32/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                Settings.get( 'Misc', 'client-win-portable' ))
                           )
            else:
                os.symlink(
                            '%s/%s/win32/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), latestPkgName ),
                            '%s/%s/win32/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                Settings.get( 'Misc', 'client-win' ))
                           )
                           
        # add symbolic links for client 64 bits
        # create the symbolic link for the window package
        latestPkg = (0,0,0)
        latestPkgName = None
        try:
            for pkg in os.listdir( '%s/%s/win64/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' )) ):
                # ExtensiveTestingClient_11.0.0_64bit_Setup.exe
                pkg_split = pkg.split("_")
                if len(pkg_split) != 4: # ignore all bad files
                    continue
                else:
                    (n, v, a, t) = pkg_split
                if portable and t.lower() != 'portable.zip':
                    continue
                if not portable and t.lower() != 'setup.exe':
                    continue
                ver = v.split(".")
                digits = map( int, ver )
                if tuple(digits) > latestPkg:
                    latestPkg = tuple(digits)
                    latestPkgName = pkg
        except Exception as e:
            self.error("unable to find the latest client windows version: %s" % str(e) )

        if latestPkgName is None:
            sys.stdout.write( " [No windows client 64-bit]" )
            self.trace('No win 64-bit client detected')
        else:
            sys.stdout.write( "(%s)" % latestPkgName)
            self.trace('Creating symbolic link for the latest windows client 64bits...')
            if portable:
                os.symlink(
                            '%s/%s/win64/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), latestPkgName ),
                            '%s/%s/win64/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                Settings.get( 'Misc', 'client-win-portable' ))
                           )
            else:
                os.symlink(
                            '%s/%s/win64/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), latestPkgName ),
                            '%s/%s/win64/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ),
                                                Settings.get( 'Misc', 'client-win' ))
                           )
                           
        if portable:
            self.trace('No portable version for linux')
        else:
            # create the symbolic link for the linux package
            latestPkg = (0,0,0)
            latestPkgName = None
            try:
                for pkg in os.listdir( '%s/%s/linux2/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' )) ):
                    ver = pkg.split("_")[1].split(".")
                    digits = map( int, ver )
                    if tuple(digits) > latestPkg:
                        latestPkg = tuple(digits)
                        latestPkgName = pkg
            except Exception as e:
                self.error("unable to find the latest client linux version: %s" % str(e) )

            if latestPkgName is not None:
                sys.stdout.write( " [%s]" % latestPkgName)
                self.trace('Creating symbolic link for the latest linux client...')
                os.symlink(
                            '%s/%s/linux2/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), latestPkgName), 
                            '%s/%s/linux2/%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'clt-package' ), Settings.get( 'Misc', 'client-linux' ))
                           )
            else:
                sys.stdout.write( " [No linux client]" )
                self.trace('No linux client detected')
        
        sys.stdout.write( "\n" )
        
        sys.stdout.flush()
        
    def deploytools(self, portable=False):
        """
        Reconstruct symlinks for clients, agents and probe from commande line
        """
        if portable:
            sys.stdout.write( "Deploying portable tools...")
        else:
            sys.stdout.write( "Deploying tools...")
        
        # remove all symbolic links
        self.trace('Removing tools symbolic links...')
        # try:
        if portable:
            try:
                os.unlink('%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                            Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win-portable' )) )
            except Exception as e:
                pass
            try:
                os.unlink('%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                            Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win-portable' )) )
            except Exception as e:
                pass
        else:
            try:
                os.unlink('%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                            Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win' )) )
            except Exception as e:
                pass
            try:
                os.unlink('%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                            Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win' )) )
            except Exception as e:
                pass
        # except Exception as e:
            # pass
            
        try:
            if portable:
                pass
            else:
                os.unlink('%s/%s/%s/linux2/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-linux' )) )
        except Exception as e:
            pass

         # Find the latest version to install for windows
        pkgs = os.listdir( '%s/%s/%s/win32/' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), Settings.get( 'Paths', 'tools' )) )
        latestPkg = (0,0,0)
        latestPkgName = None
        try:
            for pkg in pkgs:
                pkg_split = pkg.split("_")
                if len(pkg_split) != 4: # ignore bad file
                    continue
                else:
                    (n, v, a, t) = pkg_split
                if portable and t.lower() != 'portable.zip':
                    continue
                if not portable and t.lower() != 'setup.exe':
                    continue
                ver = v.split(".")
                digits = map( int, ver )
                if tuple(digits) > latestPkg:
                    latestPkg = tuple(digits)
                    latestPkgName = pkg
        except Exception as e:
            self.error("unable to find the latest tools windows version: %s" % str(e) )


        if latestPkgName is None:
            sys.stdout.write( " [No windows toolbox 32-bit]")
            self.trace('No win tools 32-bit detected')
        else:
            sys.stdout.write( "(%s)" % latestPkgName)
            self.trace('Creating symbolic link for the latest windows tools...')
            if portable:
                os.symlink(
                            '%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), latestPkgName ),
                            '%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win-portable' ))
                           )
            else:
                os.symlink(
                            '%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), latestPkgName ),
                            '%s/%s/%s/win32/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win' ))
                           )
                           
         # Find the latest version to install for windows
        pkgs = os.listdir( '%s/%s/%s/win64/' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), Settings.get( 'Paths', 'tools' )) )
        latestPkg = (0,0,0)
        latestPkgName = None
        try:
            for pkg in pkgs:
                pkg_split = pkg.split("_")
                if len(pkg_split) != 4: # ignore bad file
                    continue
                else:
                    (n, v, a, t) = pkg_split
                if portable and t.lower() != 'portable.zip':
                    continue
                if not portable and t.lower() != 'setup.exe':
                    continue
                ver = v.split(".")
                digits = map( int, ver )
                if tuple(digits) > latestPkg:
                    latestPkg = tuple(digits)
                    latestPkgName = pkg
        except Exception as e:
            self.error("unable to find the latest tools windows version: %s" % str(e) )


        if latestPkgName is None:
            sys.stdout.write( " [No windows toolbox 64-bit]")
            self.trace('No win tools 64-bit detected')
        else:
            sys.stdout.write( "(%s)" % latestPkgName)
            self.trace('Creating symbolic link for the latest windows tools...')
            if portable:
                os.symlink(
                            '%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), latestPkgName ),
                            '%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win-portable' ))
                           )
            else:
                os.symlink(
                            '%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), latestPkgName ),
                            '%s/%s/%s/win64/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                    Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-win' ))
                           )

        if portable:
            self.trace('No portable version for linux')
        else:
             # Find the latest version to install for linux
            pkgs = os.listdir( '%s/%s/%s/linux2/' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ),
                                    Settings.get( 'Paths', 'tools' )) )
            latestPkg = (0,0,0)
            latestPkgName = None
            try:
                for pkg in pkgs:
                    ver = pkg.split("_")[1].split(".")
                    digits = map( int, ver )
                    if tuple(digits) > latestPkg:
                        latestPkg = tuple(digits)
                        latestPkgName = pkg
            except Exception as e:
                self.error("unable to find the latest tools linux version: %s" % str(e) )

            if latestPkgName is not None:
                sys.stdout.write( " [%s]" % latestPkgName)
                self.trace('Creating symbolic link for the latest linux tools...')
                os.symlink(
                            '%s/%s/%s/linux2/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                        Settings.get( 'Paths', 'tools' ), latestPkgName ),
                            '%s/%s/%s/linux2/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'packages' ), 
                                                        Settings.get( 'Paths', 'tools' ), Settings.get( 'Misc', 'toolbox-linux' ))
                           )
            else:
                sys.stdout.write( " [No linux]")
                self.trace('No linux tools detected')
        sys.stdout.write( "\n" )
        
        sys.stdout.flush()
    
    def generate(self):
        """
        Generate all tar.gz (adapters, libraries, samples) from command line
        """
        DEVNULL = open(os.devnull, 'w')
        sys.stdout.write( "Generate all adapters, libraries packages...\n")
        __cmd__ = "%s/Scripts/generate-adapters.sh %s/Scripts/" % (Settings.getDirExec(), Settings.getDirExec())
        subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
        __cmd__ = "%s/Scripts/generate-libraries.sh %s/Scripts/" % (Settings.getDirExec(), Settings.getDirExec())
        subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)  
        __cmd__ = "%s/Scripts/generate-samples.sh %s/Scripts/" % (Settings.getDirExec(), Settings.getDirExec())
        subprocess.call(__cmd__, shell=True, stdout=DEVNULL, stderr=DEVNULL)
        
        sys.stdout.flush()
        
    def version(self):
        """
        Get version of the server
        """
        serverVersion = Settings.getVersion()
        sys.stdout.write( "Server version: %s\n" % serverVersion)
        
    def runTest(self, testsList=[]):
        """
        Run test
        """
        payload = { "login": Settings.get('Default','user-sys'), 
                    "password":  hashlib.sha1( Settings.get('Default','user-sys-password') ).hexdigest() }
        headers = {'content-type': 'application/json'}
        url = "http://%s:%s" % ( Settings.get('Bind','ip-rsi'), Settings.get('Bind','port-rsi')) 
        r = requests.post( "%s/session/login" % url, data=json.dumps(payload), proxies={},
                            headers=headers, verify=False)
        if r.status_code != 200:
            print("Error login")
        else:
            login = json.loads(r.text)
            sessionId = login['session_id']
                
            for t in testsList:
                if ":" not in t:
                    continue # ignore the test
                    
                _prj, _tst = t.split(":", 1)

                payload = { "project-name": _prj }
                headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % sessionId}
                url = "http://%s:%s" % ( Settings.get('Bind','ip-rsi'), Settings.get('Bind','port-rsi')) 
                r = requests.post( "%s/administration/projects/search/by/name" % url, 
                                   data=json.dumps(payload),
                                   headers=headers, verify=False)
                if r.status_code != 200:
                    print("Error search project: %s" % r.text)
                else:
                    project = json.loads(r.text)
                    _projectid = project['project']['id']
                    
                    _testpath, _test = os.path.split(_tst)
                    _testname, _testextension = os.path.splitext(_test)
                    _testextension = _testextension[1:]
                    
                    payload = {"test-execution": "", "test-definition": "",
                               "test-properties": "",
                                "test-path": _testpath, 
                                "test-name": _testname,
                                "test-extension": _testextension,
                                "project-id": _projectid,
                                'schedule-id': -1,
                                'schedule-at': [0,0,0,0,0,0]}
                    headers = {'content-type': 'application/json', 'cookie': 'session_id=%s' % sessionId}
                    url = "http://%s:%s" % ( Settings.get('Bind','ip-rsi'), Settings.get('Bind','port-rsi')) 
                    
                    if t.endswith("tpx") or t.endswith("tgx"):
                        uri = "%s/tests/schedule/tpg" % url
                    else:
                        uri = "%s/tests/schedule" % url
                    r = requests.post( uri, data=json.dumps(payload), proxies={},
                                       headers=headers, verify=False)
                    if r.status_code != 200:
                        print("Error to run")
                    else:
                        print("Test running...")

            # logout from rest api
            headers = {'cookie': 'session_id=%s' % sessionId}
            url = "http://%s:%s" % ( Settings.get('Bind','ip-rsi'), Settings.get('Bind','port-rsi')) 
            r = requests.get( "%s/session/logout" % url, headers=headers, verify=False)
            if r.status_code != 200:
                print("Error logout")
            
    def reload(self):
        """
        Reload configuration
        Send a signal to the process
        """
        sys.stdout.write( "Reloading configuration...\n")
        if not self.parent.status():
            sys.stdout.write( "Server not started...\n")
        else:
            pid = self.parent.getPid()
            if pid is not None:
                self.parent.sendSignal(pid, signal.SIGHUP)
                sys.stdout.write( "Configuration reloaded!\n" )
        
        sys.stdout.flush()
        
CLI = None # singleton
def instance ():
    """
    Returns the singleton

    @return: server singleton
    @rtype: object
    """
    return CLI

def initialize (parent):
    """
    Instance creation
    """
    global CLI
    CLI = CliFunctions(parent=parent) 

def finalize ():
    """
    Destruction of the singleton
    """
    global CLI
    if CLI: CLI = None