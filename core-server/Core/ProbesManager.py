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

import base64
import zlib
try:
    # python 2.4 support
    import simplejson as json
except ImportError:
    import json

import ProbeServerInterface as PSI
import EventServerInterface as ESI
import Context
import Common

from Libs import Settings, Logger

import ConfigParser
import os
import signal
import shlex
import subprocess
import sys
import time
import shutil
import tarfile


class ProbesManager(Logger.ClassLogger):    
    def __init__(self):
        """
        Construct Probes Manager
        """
        self.pkgsProbesPath = "%s/%s/%s/linux2/" % ( Settings.getDirExec(),   Settings.get( 'Paths', 'packages' ), 
                                        Settings.get( 'Paths', 'probes' ) )

        self.configsFile = None
        self.__pids__ = {}

    def encodeData(self, data):
        """
        Encode data
        """
        ret = ''
        try:
            tasks_json = json.dumps(data)
        except Exception as e:
            self.error( "Unable to encode in json: %s" % str(e) )
        else:
            try: 
                tasks_zipped = zlib.compress(tasks_json)
            except Exception as e:
                self.error( "Unable to compress: %s" % str(e) )
            else:
                try: 
                    ret = base64.b64encode(tasks_zipped)
                except Exception as e:
                    self.error( "Unable to encode in base 64: %s" % str(e) )
        return ret

    def getStats(self, b64=False):
        """
        Constructs some statistics on probes
            - Licence definition

        @return: probes statistics
        @rtype: dict
        """
        ret= {}
        try:
            ret['max-reg'] = Context.instance().getLicence()[ 'probes' ] [ 'instance' ]
            ret['max-def'] = Context.instance().getLicence()[ 'probes' ] [ 'default' ]
        except Exception as e:
            self.error( "unable to get probes stats: %s" % e )
        else:
            if b64:
                ret = self.encodeData(data=ret)
        return ret

    def getDefaultProbes(self, b64=False):
        """
        Read default probes to start on boot

        @return: probes to start on boot
        @rtype: list
        """
        probes = []
        if not os.path.isfile( "%s/probes.ini" % Settings.getDirExec() ):
            self.error( 'config file (probes.ini) is missing' )
        else:
            self.configsFile = ConfigParser.ConfigParser()
            self.configsFile.read( "%s/probes.ini" % Settings.getDirExec() )
            for p in self.configsFile.sections():
                tpl = {'name': p }
                for optKey,optValue in self.configsFile.items(p):
                    tpl[optKey] = optValue
                # {'enable': '1', 'type': 'textual', 'name': 'textual01', 'description': 'default probe'},
                probes.append( tpl )  
        if b64:
            probes = self.encodeData(data=probes)
        return probes

    def addDefaultProbe(self, pName, pType, pDescr):
        """
        Add default probe

        @type  pName:
        @param pName:

        @type  pType:
        @param pType:

        @type  pDescr:
        @param pDescr:

        @return:
        @rtype: boolean
        """
        ret = Context.CODE_ERROR
        try:
            if self.configsFile is not None:
                # check licence
                if len(self.configsFile.sections()) >=  Context.instance().getLicence()[ 'probes' ] [ 'default' ]:
                    ret = Context.CODE_FORBIDDEN
                else:
                    # add the section in the config file object
                    self.configsFile.add_section(pName)
                    self.configsFile.set( pName, 'enable', 1)
                    self.configsFile.set( pName, 'type', pType)
                    self.configsFile.set( pName, 'description', pDescr)
                    
                    # write date the file 
                    f = open(  "%s/probes.ini" % Settings.getDirExec() , 'w')
                    self.configsFile.write(f)
                    f.close()

                    # notify all admin and tester
                    notif = ( 'probes-default', ( 'add', self.getDefaultProbes() ) )
                    ESI.instance().notifyByUserTypes(body = notif, admin=True, leader=False, tester=True, developer=False)
                    
                    # return OK
                    ret = Context.CODE_OK
        except ConfigParser.DuplicateSectionError:
            self.error( "probe already exist %s" % str(pName) ) 
            ret = Context.CODE_ALLREADY_EXISTS
        except Exception as e:
            self.error( "unable to add default probe: %s" % str(e) )
            ret = Context.CODE_FAILED
        return ret
    
    def delDefaultProbe(self, pName):
        """
        Delete a default probe

        @type  pName:
        @param pName:

        @return:
        @rtype: boolean
        """
        ret = Context.CODE_ERROR
        try:
            if self.configsFile is not None:
                # remove the section in the config file object
                self.configsFile.remove_section(pName)

                # write date the file 
                f = open(  "%s/probes.ini" % Settings.getDirExec() , 'w')
                self.configsFile.write(f)
                f.close()

                # notify all admin and tester
                notif = ( 'probes-default', ( 'del', self.getDefaultProbes() ) )
                ESI.instance().notifyByUserTypes(body = notif, admin=True, leader=False, tester=True, developer=False)

                runningProbe = PSI.instance().getProbe(pname=pName)
                if runningProbe is not None:
                    runningProbe['auto-startup'] = False
                notif2 = ( 'probes', ( 'del', PSI.instance().getProbes() ) )
                ESI.instance().notifyByUserTypes(body = notif2, admin=True, leader=False, tester=True, developer=False)


                # return OK
                ret = Context.CODE_OK
        except ConfigParser.NoSectionError:
            self.error( "probe not found: %s" % str(pName) )    
            ret = Context.CODE_NOT_FOUND
        except Exception as e:
            self.error( "unable to delete default probe: %s" % str(e) )
            ret = Context.CODE_FAILED
        return ret

    def getRunning (self, b64=False):
        """
        Returns all registered probes

        @return: all registered probes
        @rtype: list
        """
        self.trace("get running probes" )
        ret = PSI.instance().getProbes()
        if b64:
            ret = self.encodeData(data=ret)
        return ret

    def getInstalled (self, b64=False):
        """
        Returns all registered probes

        @return: all registered probes
        @rtype: list
        """
        self.trace("get probes installed" )
        pluginsInstalled = []
        if os.path.exists( '%s/%s/Embedded/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tools' )) ):
            files = os.listdir( '%s/%s/Embedded/' % ( Settings.getDirExec(), Settings.get( 'Paths', 'tools' )) )
            for f in files:
                if f.endswith('Probe.py'):
                    p = {}
                    # open plugin to get probe type and description
                    fp = open( '%s/%s/Embedded/%s' % (Settings.getDirExec(), Settings.get( 'Paths', 'tools' ), f) , 'r')
                    data = fp.read()
                    fp.close()
                    #
                    probeType = data.split('__TYPE__="""')
                    if len(probeType) == 2:
                        probeType = probeType[1].split('"""', 1)[0]
                        p['type'] = probeType
                    probeDescr = data.split('__DESCRIPTION__="""')
                    if len(probeDescr) == 2:
                        probeDescr = probeDescr[1].split('"""', 1)[0]
                        p['description'] = probeDescr
                    if  len(p) > 0:
                        pluginsInstalled.append( p )
        if b64:
            pluginsInstalled = self.encodeData(data=pluginsInstalled)
        return pluginsInstalled

    def disconnectProbe(self, name):
        """
        Disconnect probe
        """
        self.info( "Disconnect probe Name=%s" % name )
        if not name in PSI.instance().probesRegistered:
            self.trace( "disconnect probe, probe %s not found" % name )
            return Context.CODE_NOT_FOUND
        else:
            probeProfile =  PSI.instance().probesRegistered[name]
            PSI.instance().stopClient(client=probeProfile['address'] )
        return Context.CODE_OK
    
    def stopProbe(self, pname):
        """
        Stop the probe gived in argument

        @type  pname:
        @param pname:

        @return: 
        @rtype: 
        """
        self.trace( "stop probe %s" % pname )
        ret = False
        try:
            client = PSI.instance().getProbe( pname=pname )
            if client is None:
                self.trace( "probe %s not found" % pname )
                ret = False
            else:
                self.trace( "probe %s found" % pname )
                # Stop remote probes or manual: start a probe manually is equal to a remote probe
                if not client['auto-startup']:
                    PSI.instance().stopClient( client = client['address'] )
                else:
                    # Stop local probes
                    if pname in self.__pids__:
                        try:
                            p = self.__pids__[pname]
                            p_id = p.pid
                            os.kill(p_id, signal.SIGKILL)
                            p.wait()
                            self.__pids__.pop(pname)
                        except Exception as e:
                            self.error( "Unable to kill %d: %s" % (p_id, str(e)) )
                    else:
                        self.error( "probe not found on pids: %s" % pname )
                ret = True
        except Exception as e:
            self.error( "unable to stop probe: %s" % e )
        return ret

    def startProbe(self, ptype, pname, pdescr, pdefault=False):
        """
        Start the probe passed as argument

        @type  ptype:
        @param ptype:

        @type  pname:
        @param pname:

        @type  pdescr:
        @param pdescr:

        @type  pdefault:
        @param pdefault:

        @return: 
        @rtype: 
        """
        ret = -1
        try:
            self.trace( "start probe %s of type %s" % (pname,ptype) )
            controllerIp = Settings.get( 'Bind', 'ip-psi' )
            controllerPort = Settings.get( 'Bind', 'port-psi' )
            sslSupport = False
            if int(Settings.get( 'Probe_Channel', 'channel-ssl' )): sslSupport = True
            __cmd_str__ = "%s/%s/toolprobe '%s' '%s' '%s' '%s' '%s' '%s' %s" % ( 
                                                                Settings.getDirExec(), Settings.get( 'Paths', 'tools' ),
                                                                controllerIp,
                                                                controllerPort,
                                                                sslSupport,
                                                                ptype, 
                                                                pname,
                                                                pdescr,
                                                                pdefault
                                                            ) 
            self.trace( "call %s" % __cmd_str__ )
            __cmd_args__ = shlex.split( __cmd_str__ )   
            p = subprocess.Popen(__cmd_args__, stdin=sys.stdout, stdout=sys.stdout, stderr=sys.stdout )
            time.sleep(1) # not clean at all....
            ret = p.poll()
            if ret is None:
                self.__pids__[pname] = p
            self.trace( "start probe, return code %s" % ret ) 
            if ret is None:
                ret = 0
        except Exception as e:
            self.error( "unable to start agent properly: %s" % e )
        return ret

    def trace(self, txt):
        """
        Trace message
        """
        Logger.ClassLogger.trace(self, txt="PBM - %s" % txt)

###############################
PM = None
def instance ():
    """
    Returns the singleton

    @return: One instance of the class Context
    @rtype: Context
    """
    return PM

def initialize ():
    """
    Instance creation
    """
    global PM
    PM = ProbesManager()

def finalize ():
    """
    Destruction of the singleton
    """
    global PM
    if PM:
        PM = None