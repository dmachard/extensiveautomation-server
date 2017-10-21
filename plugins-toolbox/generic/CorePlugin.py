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

import sys
import time
import base64
import json
import os
import uuid

from .Libs import Logger

try:
    from PyQt4.QtGui import (QApplication)
    from PyQt4.QtCore import (QThread, pyqtSignal, Qt)
except ImportError:
    from PyQt5.QtCore import (QThread, pyqtSignal, Qt)
    from PyQt5.QtWidgets import (QApplication)
    
class ClientAlive(QThread):
    """
    Thread for alive client
    """
    ClientDead = pyqtSignal()
    def __init__(self, parent):
        """
        Constructor
        """
        super(ClientAlive, self).__init__()
        self.maxAlive = 15
        self.lastTimestamp = time.time()
        
    def run(self):
        """
        Update last activated
        Emit Qt signal if timeout raised
        """
        timeout = False
        while (not timeout):
            time.sleep(0.1)
            if (time.time() - self.lastTimestamp) >= self.maxAlive:
                timeout = True 
        Logger.instance().info("no packet received")
        self.ClientDead.emit()
        
class ReadStdin(QThread):
    """
    Read STD in
    """
    DataIn = pyqtSignal(str)
    def __init__(self, parent):
        """
        Constructor
        """
        super(ReadStdin, self).__init__()

    def run(self):
        """
        Read STD in in loop
        Emit qt signal on data
        """
        while True:
            time.sleep(0.1)

            data = sys.stdin.readline()
            if len(data):
                self.DataIn.emit(data)
                
class GenericPlugin(object):
    """
    Main window
    """
    def __init__(self, pluginName='undefined', pluginType='agent'):
        """
        Constructor
        """
        self.bufSdtIn = ''
        self.clientTmpPath = ''
        self.pluginName = pluginName
        self.pluginType = pluginType

        # connect sdtin
        self.stdClient = ReadStdin(self)
        self.stdClient.DataIn.connect(self.on_stdinReadyRead)
        self.stdClient.start()
        
        self.aliveClient = ClientAlive(self)
        self.aliveClient.ClientDead.connect(self.onClientDead)
        self.aliveClient.start()
        
        # register the plugin
        self.sendMessage(cmd='register')

        self.onStartingPlugin()
        
    def finalize(self):
        """
        """

        try:
            self.aliveClient.stop()
            self.aliveClient.join()
        except Exception as e: 
            print(e)

        try:
            self.stdClient.stop()
            self.stdClient.join()
        except Exception as e: 
            print(e)

    def onClientDead(self):
        """"
        On client terminattion, no more keepalive received from the client
        """
        self.stdClient.terminate()
        self.stdClient.wait()
        
        self.aliveClient.terminate()
        self.aliveClient.wait()
        
        QApplication.quit()

    def on_stdinReadyRead(self, data):
        """
        On data in  STD in
        """
        try:
            self.bufSdtIn += data

            pdus = self.bufSdtIn.split("\n\n")
            for pdu in pdus[:-1]:
                try:
                    datagramDecoded = base64.b64decode(pdu)
                    if sys.version_info > (3,): # python 3 support
                        messageJson = json.loads( str(datagramDecoded, "utf8") )
                    else:
                        messageJson = json.loads( datagramDecoded )
                except Exception as e:
                    Logger.instance().error("error decode - %s" % e)
                else:
                    self.onPluginMessage(msg=messageJson)
            self.bufSdtIn = pdus[-1]
        except Exception as e:
            Logger.instance().error("error - %s" % e)

    def getTmpArea(self):
        """
        Return the tmp area
        """
        return self.clientTmpPath
        
    def onPluginMessage(self, msg):
        """
        On message received from the client
        """
        try:
            if msg['cmd'] == 'registered':
                self.clientTmpPath = msg['tmp-path']
                self.onPluginStarted()

            elif msg['cmd'] == 'keepalive':
                self.aliveClient.lastTimestamp = time.time()

            elif msg['cmd'] in [ 'notify', 'reset', 'init', 'alive' ] :

                # read data
                request = {}
                
                if msg['in-data']:
                    # read the file
                    f = open( "%s/%s" % ( self.clientTmpPath, msg['data-id'] ), 'r')
                    all = f.read()
                    f.close()
                    
                    request = json.loads( all )

                    # delete them
                    os.remove( "%s/%s" % ( self.clientTmpPath, msg['data-id']  ) )
                
                if msg["cmd"] == 'notify':
                    self.onAgentNotify(client=msg['client'], tid=msg['tid'], request=request)
                if msg["cmd"] == 'reset':
                    self.onAgentReset(client=msg['client'], tid=msg['tid'], request=request)
                if msg["cmd"] == 'init':
                    self.onAgentInit(client=msg['client'], tid=msg['tid'], request=request)
                if msg["cmd"] == 'alive':
                    self.onAgentAlive(client=msg['client'], tid=msg['tid'], request=request)
                    
            elif msg['cmd'] == 'start-probe':
                self.onStartingProbe(callid=msg['callid'], tid=msg['tid'], data=msg['data'])
                
            elif msg['cmd'] == 'stop-probe':
                self.onStoppingProbe(tid=msg['tid'], data=msg['data'])
                
            else:
                pass
        except Exception as e:
            Logger.instance().error("error plugin msg - %s" % e)

    def sendMessage(self, cmd, data='', more={}):
        """
        Send a message to the client
        """
        inData = False
        msg = {'cmd': cmd }
        
        # save data to temp area
        idFile = ''
        
        
        if len(data):
            try:
                idFile = "%s" % uuid.uuid4()
                pluginDataFile = '%s/%s' % (self.clientTmpPath, idFile)
                with open( pluginDataFile, mode='w') as myfile:
                    myfile.write( json.dumps( data ) )
                inData = True
            except Exception as e:
                Logger.instance().error("unable to write data file from plugin: %s" % e)

        msg.update( { 'in-data': inData } )
        
        # add data parameters
        if inData: msg.update( { 'data-id': idFile } )
             
        # add more params
        msg.update(more)
        
        # adding reference
        msg.update( { 'id': self.pluginName, 'name': self.pluginName, 'type': self.pluginType } )

        # encode message and send to stdout
        datagram = json.dumps( msg ) 

        datagramEncoded = base64.b64encode( bytes(datagram, "utf8")  )
        print( str(datagramEncoded, "utf8") )
        sys.stdout.flush()
        
    # functions to log messages on toolbox
    def logWarning(self, msg):
        """
        """
        self.sendMessage(cmd="log-warning", more={'msg': msg})
        
    def logSuccess(self, msg):
        """
        """
        self.sendMessage(cmd="log-success", more={'msg': msg})
        
    def logError(self, msg):
        """
        """
        self.sendMessage(cmd="log-error", more={'msg': msg})
        
    # functions to send data or error to the server
    def sendData(self, request, data):
        """
        Send data to the test server
        """
        self.sendMessage(cmd="send-data", data=data, more={'request': request})
        
    def sendError(self, request, data):
        """
        Send error to the test server
        """
        self.sendMessage(cmd="send-error", data=data, more={'request': request})
        
    def sendNotify(self, request, data):
        """
        Send notify to the test server
        """
        self.sendMessage(cmd="send-notify", data=data, more={'request': request})
        
    def onProbeStarted(self, tid, body):
        """
        """
        self.sendMessage(cmd="probe-started", more={'tid': tid, 'body': body})
        
    def onProbeStopped(self, tid, body, additional, dataToSend):
        """
        """
        self.sendMessage(cmd="probe-stopped", more={'tid': tid, 'body': body, 'additional': additional, 'dataToSend': dataToSend}) 
        
    # functions to reimplement
    def onStartingProbe(self, callid, tid, data):
        """
        """
        pass
        
    def onStoppingProbe(self, tid, data):
        """
        """
        pass
        
    def onAgentNotify(self, client, tid, request): 
        """
        Function to overwrite
        """
        pass
        
    def onAgentReset(self, client, tid, request): 
        """
        Function to overwrite
        """
        pass

    def onAgentInit(self, client, tid, request): 
        """
        Function to overwrite
        """
        pass

    def onAgentAlive(self, client, tid, request): 
        """
        Function to overwrite
        """
        pass
        
    def onStartingPlugin(self):
        """
        Function to overwrite
        """
        pass
        
    def onPluginStarted(self):
        """
        Function to overwrite
        """
        pass