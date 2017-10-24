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

"""
Server explorer 
Handle all plugins
"""

import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
 
try:
    from PyQt4.QtGui import (QWidget, QVBoxLayout, QProgressBar, QFont, QHBoxLayout, QLabel, 
                            QComboBox, QSizePolicy, QLineEdit, QIntValidator, QCheckBox, QGridLayout, 
                            QFrame, QPushButton, QMessageBox, QTabWidget, QIcon, QDialog)
    from PyQt4.QtCore import (pyqtSignal, Qt, QRect, QUrl, QByteArray, QObject)
    from PyQt4.QtNetwork import (QHttp, QNetworkProxy, QHttpRequestHeader, 
                                QNetworkAccessManager, QNetworkRequest )
except ImportError:
    from PyQt5.QtGui import (QFont, QIntValidator, QIcon)
    from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QProgressBar, QHBoxLayout, QLabel, 
                                QComboBox, QSizePolicy, QLineEdit, QCheckBox, QGridLayout, 
                                QFrame, QPushButton, QMessageBox, QTabWidget, QDialog)
    from PyQt5.QtCore import (pyqtSignal, Qt, QRect, QUrl, QByteArray, QObject)
    from PyQt5.QtNetwork import (QNetworkProxy, QNetworkAccessManager, QNetworkRequest)
    
import UserClientInterface as UCI
import RestClientInterface as RCI
from Libs import QtHelper, Logger
import Settings

# Plugins
try:
    import Miscellaneous
    import TestManager
    import Archives
    import Probes
    import Agents
    import ReleaseNotes
    import Repositories
    import Counters
except ImportError:
    from . import Miscellaneous
    from . import TestManager
    from . import Archives
    from . import Probes
    from . import Agents
    from . import ReleaseNotes
    from . import Repositories
    from . import Counters

# import standard library
import hashlib
import base64
import json
import zlib
try:
    import xmlrpclib
except ImportError: # support python3
    import xmlrpc.client as xmlrpclib
    
from Libs import PyBlowFish

NETWORK_ERRORS = {}
NETWORK_ERRORS[1] = "The remote server refused the connection."
NETWORK_ERRORS[2] = "The remote server closed the connection prematurely, before the entire reply was received and processed."
NETWORK_ERRORS[3] = "The remote host name was not found (invalid hostname)."
NETWORK_ERRORS[4] = "The connection to the remote server timed out."
NETWORK_ERRORS[5] = "The operation was canceled  before it was finished."
NETWORK_ERRORS[6] = "The SSL/TLS handshake failed and the encrypted channel could not be established."
NETWORK_ERRORS[7] = "The connection was broken due to disconnection from the network."
NETWORK_ERRORS[99] = "An unknown network-related error was detected."
NETWORK_ERRORS[101] = "The connection to the proxy server was refused (the proxy server is not accepting requests)."
NETWORK_ERRORS[102] = "The proxy server closed the connection prematurely, before the entire reply was received and processed."
NETWORK_ERRORS[103] = "The proxy host name was not found (invalid proxy hostname)."
NETWORK_ERRORS[104] = "The connection to the proxy timed out or the proxy did not reply in time to the request sent."
NETWORK_ERRORS[105] = "The proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)."
NETWORK_ERRORS[199] = "An unknown proxy-related error was detected."
NETWORK_ERRORS[201] = "The access to the remote content was denied (similar to HTTP error 401)."
NETWORK_ERRORS[202] = "The operation requested on the remote content is not permitted."
NETWORK_ERRORS[203] = "The remote content was not found at the server (similar to HTTP error 404)."
NETWORK_ERRORS[204] = "The remote server requires authentication to serve the content but the credentials provided were not accepted (if any)."
NETWORK_ERRORS[205] = "The request needed to be sent again, but this failed for example because the upload data could not be read a second time."
NETWORK_ERRORS[299] = "An unknown error related to the remote content was detected."
NETWORK_ERRORS[301] = "The Network Access API cannot honor the request because the protocol is not known."
NETWORK_ERRORS[302] = "The requested operation is invalid for this protocol."
NETWORK_ERRORS[399] = "A breakdown in protocol was detected (parsing error, invalid or unexpected responses."

class XmlrpcNetworkHandler(QObject, Logger.ClassLogger):
    """
    Xmlrpc network handler
    """
    StartWorking = pyqtSignal()
    StartWorkingChannel = pyqtSignal()
    StopWorking = pyqtSignal()
    InProgress = pyqtSignal(int, int)
    def __init__(self, parent = None):
        """
        Constructor

        @param dialogName: 
        @type dialogName:

        @param parent: 
        @type parent:
        """
        QObject.__init__(self, parent)

        self.WsAddress = ''

        self.httpPostReq = []
        self.reqInProgress= None

        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.onNetworkFinished)
        self.manager.sslErrors.connect(self.onNetworkSslErrors)

    def onNetworkProgress(self, bytesRead, totalBytes):
        """
        """
        self.InProgress.emit(bytesRead, totalBytes)

    def onNetworkSslErrors(self, reply, errors):
        """
        Ignore SSL errors, not good ...
        """
        self.trace('WS ignore ssl errors')
        reply.ignoreSslErrors()

    def onNetworkFinished(self, reply):
        """
        """

        if reply in NETWORK_ERRORS:
            self.error( 'XmlRPC response error: %s' % NETWORK_ERRORS[reply] )
            self.stopWorking()
            UCI.instance().onError( title=self.tr("XmlRPC - Connection Error"), err=self.tr( "%s" % NETWORK_ERRORS[reply] ) )
        else:
            # read the body
            rsp = reply.readAll()
            
            # read the http response code
            httpCode = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if sys.version_info < (3,): httpCode = httpCode.toString()
                
            self.trace("http code response: %s" % httpCode)
            if httpCode is None: return
            
            if int(httpCode) != 200:
                self.error("bad code response %s, http body content for xmlrpc: %s" % (httpCode,rsp) )
                self.stopWorking()
                UCI.instance().onError( title=self.tr("XmlRPC Error"), err="Error Code: %s\n\nError details:\n%s" % (httpCode,rsp) )
            else:
                if len(rsp):
                    try:
                        self.trace('XmlRPC response received (truncated): %s' % rsp[:500])
                        # decode xml rpc response and strip it
                        if sys.version_info > (3,):
                            xml_rsp = xmlrpclib.loads( str(rsp, 'utf8').strip() )
                        else:
                            xml_rsp = xmlrpclib.loads( unicode(rsp).strip() )
                    except xmlrpclib.Fault as e:
                        self.error("XmlRPC Fault code: %d" % e.faultCode)
                        self.error("XmlRPC Fault string: %s" % e.faultString)
                        self.error("XmlRPC Data received: %s" % rsp)
                        self.stopWorking()
                        UCI.instance().onError( title=self.tr("XmlRPC Error"), err=self.tr("Unable to read XML response")  )
                    except Exception as e:
                        self.trace("XmlRPC data received: %s" % rsp)
                        self.error( "XmlRPC generic error: %s" % e)
                        self.stopWorking()
                        UCI.instance().onError( title=self.tr("XmlRPC Generic Error"), err=self.tr("Unexpected response received") )
                    else:
                        self.stopWorking()
                        UCI.instance().onResponse(value=tuple(xml_rsp[0][0]) )

        reply.close()
        reply.deleteLater()
        
        self.reqInProgress = None
        if len(self.httpPostReq):
            self.__NetworkCall( postData=self.httpPostReq.pop(0) )
            
    def closeEvent(self, event):
        """
        On close event
        """
        self.httpPostId = None
        if self.reply is not None:
            self.reply.abort()
        self.reply = None
        
        event.accept()

    def setWsAddress(self, address, port, scheme, webpath, hostname ):
        """
        Set webservice address
        """
        self.WsAddress = address
        self.WsHostname = hostname 
        self.WsPort = int(port)
        self.WsScheme = scheme 
        self.WsWebpath = webpath
        self.trace("configure address=%s:%s scheme=%s webpath=%s hostname=%s for xmlrpc" % (address, port, scheme, webpath, hostname) )

    def setWsProxy(self, ip, port, login=None, password=None):
        """
        Set webservice proxy
        """
        if len(ip):
            if port:
                proxy = QNetworkProxy()
                proxy.setType(3); # http
                proxy.setHostName(ip)
                proxy.setPort(int(port))
                
                if login is not None:
                    proxy.setUser(login)
                if password is not None:
                    proxy.setPassword(password)

                self.manager.setProxy(proxy)
                self.trace("configure proxy address for xmlrpc: %s:%s" % (ip, port) )
                
    def unsetWsProxy(self):
        """
        Unset webservice proxy
        """
        proxy = QNetworkProxy()
        proxy.setType(2); # no proxy
        self.manager.setProxy(proxy)

    def startWorking(self):
        """
        Start working, emit signal
        """
        self.StartWorking.emit()
        return True

    def startWorkingChannel(self):
        """
        Start working on channel, emit signal
        """
        self.StartWorkingChannel.emit()
        return True

    def stopWorking(self):
        """
        Stop working, emit signal
        """
        self.StopWorking.emit()

    def NetworkCall(self, postData ):
        """
        """
        self.httpPostReq.append( postData )
        if self.reqInProgress is None:
            self.__NetworkCall( postData=self.httpPostReq.pop(0) )
            
    def __NetworkCall(self, postData):
        """
        """
        self.startWorking()

        self.trace('prepare post request for xmlrpc api' )
        try:
            url   = QUrl("%s://%s:%s/%s" % (self.WsScheme.lower(), self.WsAddress, self.WsPort, self.WsWebpath) )
            
            req   = QNetworkRequest (url)
            if sys.version_info > (3,):
                req.setRawHeader( b"Host", bytes(self.WsHostname, 'utf8') )
                req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym'), "utf8") )
                req.setRawHeader( b"Connexion", b"Keep-Alive" )
                req.setRawHeader( b"Content-Type", b"text/xml" )
            else:
                req.setRawHeader( b"Host", bytes(self.WsHostname) )
                req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym' )) )
                req.setRawHeader( b"Connexion", b"Keep-Alive" )
                req.setRawHeader( b"Content-Type", b"text/xml" )
            
            if sys.version_info > (3,):
                reply = self.manager.post(req, bytes(postData, "utf8") )
            else:
                reply = self.manager.post(req, bytes(postData) )

            reply.downloadProgress.connect(self.onNetworkProgress)

        except Exception as e:
            self.error( str(e) )
            self.stopWorking()
            UCI.instance().onError(err='XmlRPC Call Error: %s' % str(e) )
            
class RestNetworkHandler(QObject, Logger.ClassLogger):
    """
    Webservice network handler
    """
    StartWorking = pyqtSignal()
    StopWorking = pyqtSignal()
    InProgress = pyqtSignal(int, int)
    def __init__(self, parent = None):
        """
        Constructor

        @param dialogName: 
        @type dialogName:

        @param parent: 
        @type parent:
        """
        QObject.__init__(self, parent)

        self.WsAddress = ''
        self.WsCookie = None
        
        self.httpPostReq = []
        self.reqInProgress= None

        self.manager = QNetworkAccessManager()
        self.manager.finished.connect(self.onNetworkFinished)
        self.manager.sslErrors.connect(self.onNetworkSslErrors)

    def onNetworkProgress(self, bytesRead, totalBytes):
        """
        """
        self.InProgress.emit(bytesRead, totalBytes)

    def onNetworkSslErrors(self, reply, errors):
        """
        Ignore SSL errors, not good ...
        """
        self.trace('WS ignore ssl errors')
        reply.ignoreSslErrors()

    def onNetworkFinished(self, reply):
        """
        """

        if reply in NETWORK_ERRORS:
            self.error( 'REST response error: %s' % NETWORK_ERRORS[reply] )
            self.stopWorking()
            UCI.instance().onError( title=self.tr("REST - Connection Error"), err=self.tr( "%s" % NETWORK_ERRORS[reply] ) )
        else:
            # read the body
            rsp = reply.readAll()
            
            # read the http response code
            httpCode = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
            if sys.version_info < (3,): httpCode = httpCode.toString()
                
            self.trace("rest http code response: %s" % httpCode)
            if httpCode is None: return
            
            if int(httpCode) in [ 401 ]:
                self.error("rest authentication failed, http body content for REST: %s" % (rsp) )
                self.stopWorking()
                try:
                    if sys.version_info > (3,):
                        auth = json.loads( str(rsp, 'utf8').strip() )
                    else:
                        auth = json.loads( unicode(rsp).strip() )
                except Exception as e:
                    print(e)
                    RCI.instance().onGenericError( title=self.tr("API Decode Error"), 
                                                    err="Error Code: %s\n\nError details:\n%s" % (httpCode,rsp) )
                else:
                    RCI.instance().onAuthenticationFailed( title=self.tr("Authentication Error"), 
                                                            err="%s" % auth['error'] )
            elif int(httpCode) != 200:
                self.error("bad code response %s, http body content for REST: %s" % (httpCode,rsp) )
                self.stopWorking()
                RCI.instance().onGenericError( title=self.tr("REST Error"), 
                                                err="Error Code: %s\n\nError details:\n%s" % (httpCode,rsp) )
            
            else:
                if len(rsp):
                    try:
                        self.trace('REST response received (truncated): %s' % rsp[:500])
                        if sys.version_info > (3,):
                            json_rsp = json.loads( str(rsp, 'utf8').strip() )
                        else:
                            json_rsp = json.loads( unicode(rsp).strip() )
                    except Exception as e:
                        self.trace("REST data received: %s" % rsp)
                        self.error( "REST generic error: %s" % e)
                        self.stopWorking()
                        RCI.instance().onGenericError( title=self.tr("API Decode Error"), 
                                                        err=self.tr("Unexpected response received") )
                    else:
                        self.stopWorking()
                        if RCI.instance() is not None:
                            RCI.instance().onGenericResponse( response=json_rsp )

        reply.close()
        reply.deleteLater()
        
        self.reqInProgress = None
        if len(self.httpPostReq):
            self.__NetworkCall( postData=self.httpPostReq.pop(0) )
            
    def closeEvent(self, event):
        """
        On close event
        """
        self.httpPostId = None
        if self.reply is not None:
            self.reply.abort()
        self.reply = None
        
        event.accept()

    def setWsAddress(self, address, port, scheme, webpath, hostname ):
        """
        Set webservice address
        """
        self.WsAddress = address
        self.WsHostname = hostname 
        self.WsPort = int(port)
        self.WsScheme = scheme 
        self.WsWebpath = webpath
        self.trace("configure address=%s:%s scheme=%s webpath=%s hostname=%s for REST" % (address, port, scheme, webpath, hostname) )

    def setWsProxy(self, ip, port, login=None, password=None):
        """
        Set webservice proxy
        """
        if len(ip):
            if port:
                proxy = QNetworkProxy()
                proxy.setType(3); # http
                proxy.setHostName(ip)
                proxy.setPort(int(port))
                
                if login is not None:
                    proxy.setUser(login)
                if password is not None:
                    proxy.setPassword(password)

                self.manager.setProxy(proxy)
                self.trace("configure proxy address for REST: %s:%s" % (ip, port) )
         
    def unsetWsProxy(self):
        """
        Unset webservice proxy
        """
        proxy = QNetworkProxy()
        proxy.setType(2); # no proxy
        self.manager.setProxy(proxy)

    def setWsCookie(self, cook):
        """
        """
        self.WsCookie = cook

    def unsetWsCookie(self):
        """
        """
        self.WsCookie = None
        
    def startWorking(self):
        """
        Start working, emit signal
        """
        self.StartWorking.emit()
        return True

    def stopWorking(self):
        """
        Stop working, emit signal
        """
        self.StopWorking.emit()

    def NetworkCall(self, req ):
        """
        """
        self.httpPostReq.append( req )
        if self.reqInProgress is None:
            self.__NetworkCall( req=self.httpPostReq.pop(0) )
            
    def __NetworkCall(self, req):
        """
        """
        self.startWorking()

        self.trace('prepare post request for REST api %s' % str(req) )
        
        uri, request, postData = req
        try:
            url   = QUrl("%s://%s:%s/%s/%s" % (self.WsScheme.lower(), self.WsAddress, 
                                                self.WsPort, self.WsWebpath, uri) )
            
            req   = QNetworkRequest (url)
            if request == "POST":
                if sys.version_info > (3,):
                    req.setRawHeader( b"Host", bytes(self.WsHostname, 'utf8') )
                    req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym'), "utf8") )
                    req.setRawHeader( b"Connexion", b"Keep-Alive" )
                    req.setRawHeader( b"Content-Type", b"application/json" )
                    if self.WsCookie is not None:
                        req.setRawHeader( b"Cookie", bytes(self.WsCookie, 'utf8')  )
                else:
                    req.setRawHeader( b"Host", bytes(self.WsHostname) )
                    req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym' )) )
                    req.setRawHeader( b"Connexion", b"Keep-Alive" )
                    req.setRawHeader( b"Content-Type", b"application/json" )
                    if self.WsCookie is not None:
                        req.setRawHeader( b"Cookie", bytes(self.WsCookie)  )
                        
                if sys.version_info > (3,):
                    reply = self.manager.post(req, bytes(postData, "utf8") )
                else:
                    reply = self.manager.post(req, bytes(postData) )
                    
            elif request == "GET":
                if sys.version_info > (3,):
                    req.setRawHeader( b"Host", bytes(self.WsHostname, 'utf8') )
                    req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym'), "utf8") )
                    req.setRawHeader( b"Connexion", b"Keep-Alive" )
                    if self.WsCookie is not None:
                        req.setRawHeader( b"Cookie", bytes(self.WsCookie, 'utf8')  ) 
                        
                else:
                    req.setRawHeader( b"Host", bytes(self.WsHostname) )
                    req.setRawHeader( b"User-Agent", bytes(Settings.instance().readValue( key = 'Common/acronym' )) )
                    req.setRawHeader( b"Connexion", b"Keep-Alive" )
                    if self.WsCookie is not None:
                        req.setRawHeader( b"Cookie", bytes(self.WsCookie)  ) 
                        
                reply = self.manager.get(req)  
            else:
                raise Exception("request not yet supported" % request)
                
            reply.downloadProgress.connect(self.onNetworkProgress)

        except Exception as e:
            self.error( str(e) )
            self.stopWorking()
            if RCI.instance() is not None:
                RCI.instance().onGenericError(err='REST Call Error: %s' % str(e) )
            
class WServerProgress(QWidget, Logger.ClassLogger):
    """
    Server status widget
    """
    def __init__(self, parent):
        """
        """
        QWidget.__init__(self, parent)
        
        self.createWidget()

    def progress(self):
        """
        """
        return self.progressBar
        
    def createWidget(self):
        """
        Create qt widget
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 2, 0)

        self.progressBar = QProgressBar(self)
        self.progressBar.setTextVisible(False)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        
        self.progressBar2 = QProgressBar(self)
        self.progressBar2.setTextVisible(False)
        self.progressBar2.setMaximum(100)
        self.progressBar2.setProperty("value", 0)
        self.progressBar2.setAlignment(Qt.AlignCenter)
        self.progressBar2.setObjectName("progressBar")

        layout.addWidget( QLabel("| Data Transfer:") )
        
        layout2 = QVBoxLayout()
        layout2.setSpacing(0)
        layout2.setContentsMargins(0, 0, 0, 0)
        layout2.addWidget( self.progressBar )
        layout2.addWidget( self.progressBar2 )
        
        layout.addLayout(layout2)
        
        self.setLayout(layout)
        self.setFixedWidth(150)
        self.setFixedHeight(15)

    def stopWorking(self):
        """
        Stop working, emit signal
        """
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        
    def startWorking(self):
        """
        Start working, emit signal
        """
        self.progressBar.setMaximum(0)
        self.progressBar.setProperty("value", 0)
        
    def updateProgress(self, bytesRead, totalBytes):
        """
        Start working, emit signal
        """
        self.progressBar.setMaximum(totalBytes)
        self.progressBar.setValue(bytesRead)

    def stopWorkingRest(self):
        """
        Stop working, emit signal
        """
        self.progressBar2.setMaximum(100)
        self.progressBar2.setProperty("value", 0)
        
    def startWorkingRest(self):
        """
        Start working, emit signal
        """
        self.progressBar2.setMaximum(0)
        self.progressBar2.setProperty("value", 0)
        
    def updateProgressRest(self, bytesRead, totalBytes):
        """
        Start working, emit signal
        """
        self.progressBar2.setMaximum(totalBytes)
        self.progressBar2.setValue(bytesRead)
        
class WServerStatus(QWidget, Logger.ClassLogger):
    """
    Server status widget
    """
    def __init__(self, parent):
        """
        Constructs WServerStatus widget
         _____________________________________________
        |                                             |
        | Server: Disconnected/Connected (IP address) |
        |_____________________________________________|

        @param parent: WServerExplorer
        @type parent: QWidget
        """
        QWidget.__init__(self, parent)
        self.OFFLINE = self.tr("Disconnected")
        self.ONLINE = self.tr("Connected")

        self.createWidgets()

    def createWidgets(self):
        """
        QtWidgets creation
         ________________________________
        |                                |
        | QLabel:  QIcon   QLabel        |
        |________________________________|
        """
        font = QFont()
        font.setItalic(True)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.status = QLabel( "%s |" % self.OFFLINE )
        layout.addWidget(self.status)
        self.serverLogin = QLabel("%s: |" % self.tr("Login"))
        layout.addWidget(self.serverLogin)
        self.serverLabel = QLabel("%s: |" % self.tr("Remote"))
        layout.addWidget(self.serverLabel)
        self.proxyLabel = QLabel("%s: " % self.tr("Proxy"))
        layout.addWidget(self.proxyLabel)
        self.setLayout(layout)
        
    def setStatus(self, status, serverIp = None, rightUser = None, userLogin=None, proxyIp=None, serverPort=None):
        """
        Called to change the status of the connection

        @param status: 
        @type status: string    

        @param serverIp: 
        @type serverIp: 

        @param rightUser: 
        @type rightUser:    

        @param userLogin: 
        @type userLogin:    
        """
        if serverIp is not None:
            if serverPort is not None:
                self.serverLabel.setText( "%s: %s:%s |" % (self.tr("Remote"), serverIp, serverPort) )
            else:
                self.serverLabel.setText( "%s: %s |" % (self.tr("Remote"), serverIp) )
            self.serverLogin.setText( "%s: %s |" % (self.tr("Login"), userLogin) )
            if proxyIp is not None:
                self.proxyLabel.setText( "%s: %s" % (self.tr("Proxy"), proxyIp) )
            else:
                self.proxyLabel.setText("%s: " % self.tr("Proxy") )
            self.status.setText("%s as %s |" % (status, ",".join(rightUser) ) )
            
        else:
            self.serverLabel.setText("%s: |" % self.tr("Login") )
            self.status.setText( "%s |" % status)
            self.serverLogin.setText("%s: |" % self.tr("Remote") )
            self.proxyLabel.setText("%s: " % self.tr("Proxy") )

class DServerConnection(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Dialog dialog
    """
    def __init__(self, parent): 
        """
        Constructs server connection dialog

        @param parent: 
        @type parent:
        """     
        super(DServerConnection, self).__init__(parent)

        self.defaultPort = Settings.instance().readValue( key = 'Server/port-api' )

        # proxy http
        self.defaultProxyHttpAddr = Settings.instance().readValue( key = 'Server/addr-proxy-http' )
        self.defaultProxyHttpPort = Settings.instance().readValue( key = 'Server/port-proxy-http' )
        # decryptor
        self.oEncryptor = PyBlowFish.BlowfishEncryptor()
        self.createDialog()
        self.createConnections()

    def createDialog(self):
        """
        Create qt dialog
        """
        self.setWindowTitle(self.tr("Login on the test center"))
        self.resize(400, 100)
        
        layout = QVBoxLayout()
        
        lastAddr = Settings.instance().readValue( key = 'Server/last-addr')
        addrList = Settings.instance().readValue( key = 'Server/addr-list', rType = 'qlist')
        lastUsername = Settings.instance().readValue( key = 'Server/last-username')
        if not int(Settings.instance().readValue( key = 'Server/save-credentials')):
            lastPassword = ''
            lastUsername = ''
        else:
            try:
                # set key for decryption
                self.oEncryptor.setHexKey( hashlib.md5(lastUsername.encode('utf8')).hexdigest() )
                
                # decrypt password from config file
                lastPassword = Settings.instance().readValue( key = 'Server/last-pwd')
                if lastPassword != '':
                    lastPassword = self.oEncryptor.decrypt( lastPassword.encode('utf8') ) 
            except Exception as e:
                self.error( "decrypt user password %s" % str(e) )
                lastPassword = ''

        self.addrComboBox = QComboBox()
        self.addrComboBox.setMinimumWidth(250)
        self.addrComboBox.setEditable(1)
        if isinstance(addrList, str):
            addrList = [ addrList ]
        self.addrComboBox.addItems(addrList)
        self.addrComboBox.setEditText(lastAddr)
        self.addrComboBox.setMaxCount(5)
        self.addrComboBox.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )

        self.usernameEdit = QLineEdit(lastUsername)
        self.usernameEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.passwordEdit = QLineEdit(lastPassword)
        self.passwordEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.passwordEdit.setEchoMode( QLineEdit.Password )

        # proxy http support
        self.proxyHttpAddrEdit = QLineEdit(self.defaultProxyHttpAddr)
        self.proxyHttpAddrEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.proxyHttpAddrEdit.setDisabled(True)
        self.proxyHttpPortEdit = QLineEdit(self.defaultProxyHttpPort)
        self.proxyHttpPortEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        self.proxyHttpPortEdit.setDisabled(True)
        validatorProxy = QIntValidator (self)
        self.proxyHttpPortEdit.setValidator(validatorProxy)
        self.proxyHttpPortEdit.setMinimumWidth(60)

        self.proxyLoginEdit = QLineEdit()
        self.proxyLoginEdit.setDisabled(True)
        self.proxyPasswordEdit = QLineEdit()
        self.proxyPasswordEdit.setEchoMode( QLineEdit.Password )
        self.proxyPasswordEdit.setDisabled(True)
        
        self.savePassCheckBox = QCheckBox( self.tr("Saving credentials" ) )
        if int(Settings.instance().readValue( key = 'Server/save-credentials')):
            self.savePassCheckBox.setChecked(True)
            
        # main form
        layout = QHBoxLayout()
        paramLayout = QGridLayout()
        paramLayout.addWidget(QLabel(self.tr("Address:")), 0, 0, Qt.AlignRight)
        paramLayout.addWidget(self.addrComboBox, 0, 1)

        paramLayout.addWidget(QLabel(self.tr("Username:")), 2, 0, Qt.AlignRight)
        paramLayout.addWidget(self.usernameEdit, 2, 1)
        paramLayout.addWidget(QLabel(self.tr("Password:")), 3, 0, Qt.AlignRight)
        paramLayout.addWidget(self.passwordEdit, 3, 1)
        paramLayout.addWidget(self.savePassCheckBox, 4, 1)
 
        self.sep1 = QFrame()
        self.sep1.setGeometry(QRect(110, 221, 51, 20))
        self.sep1.setFrameShape(QFrame.HLine)
        self.sep1.setFrameShadow(QFrame.Sunken)
        
        # proxy support
        self.withProxyCheckBox = QCheckBox( self.tr("Use a HTTPS proxy server" ) )
        if QtHelper.str2bool( Settings.instance().readValue( key = 'Server/proxy-active') ):
            self.withProxyCheckBox.setChecked(True)
            self.proxyHttpAddrEdit.setDisabled(False)
            self.proxyHttpPortEdit.setDisabled(False)
        
        paramLayout.addWidget( self.sep1, 5, 1)
        paramLayout.addWidget( self.withProxyCheckBox, 6, 1)
        
        proxyLayout = QGridLayout()
        proxyLayout.addWidget(QLabel(self.tr("Proxy Address:")), 0, 0)
        proxyLayout.addWidget(self.proxyHttpAddrEdit, 0, 1)
        proxyLayout.addWidget(QLabel(self.tr("Proxy Port:")), 1, 0)
        proxyLayout.addWidget(self.proxyHttpPortEdit, 1, 1)
        proxyLayout.addWidget(QLabel(self.tr("Login:")), 2, 0)
        proxyLayout.addWidget(self.proxyLoginEdit, 2, 1)
        proxyLayout.addWidget(QLabel(self.tr("Password:")), 3, 0)
        proxyLayout.addWidget(self.proxyPasswordEdit, 3, 1)
        
        paramLayout.addLayout(proxyLayout, 7,1)
        layout.addLayout(paramLayout)
        
        # Buttons
        buttonLayout = QVBoxLayout()
        self.okButton = QPushButton( QIcon(":/ok.png"), self.tr("Connection"), self)
        self.cancelButton = QPushButton( QIcon(":/test-close-black.png"), self.tr("Cancel"), self)
        buttonLayout.addWidget(self.okButton)
        buttonLayout.addWidget(self.cancelButton)
        buttonLayout.addStretch()
        layout.addLayout(buttonLayout)

        self.setLayout(layout)

    def createConnections (self):
        """
        Create qt connections
         * ok
         * cancel
         * with proxy
        """
        self.okButton.clicked.connect(self.acceptClicked)
        self.cancelButton.clicked.connect(self.reject)
        self.withProxyCheckBox.stateChanged.connect(self.enableProxy)
        self.savePassCheckBox.stateChanged.connect(self.savePassword)

    def savePassword(self, state):
        """
        Save password
        """
        if state != 0:
            Settings.instance().setValue( key = 'Server/save-credentials', value = "1" )
        else:
            Settings.instance().setValue( key = 'Server/save-credentials', value = "0" )
            
    def enableProxy(self, state):
        """
        Enable proxy
        """
        if state != 0:
            self.proxyHttpAddrEdit.setEnabled(True)
            self.proxyHttpPortEdit.setEnabled(True)
        else:
            self.proxyHttpAddrEdit.setEnabled(False)
            self.proxyHttpPortEdit.setEnabled(False)
    
    def acceptClicked (self):
        """
        Called on connect button
        """
        if not len(self.addrComboBox.currentText()):
            QMessageBox.warning(self, self.tr("Connection") , self.tr("Please to set a destination address!") )
            return
        if self.withProxyCheckBox.checkState() :
            if not len(self.proxyHttpAddrEdit.text()):
                QMessageBox.warning(self, self.tr("Connection") , self.tr("Please to set a http proxy!") )
                return
            if not len(self.proxyHttpPortEdit.text()):
                QMessageBox.warning(self, self.tr("Connection") , self.tr("Please to set a port the http proxy!") )
                return
            
        self.accept()

    def getCtx (self):
        """
        Return (ip,port) of the server, username and password
        Saves to settings

        @return: ( address, username, password )
        @rtype: tuple
        """
        destPort = None
        try:
            address = str(self.addrComboBox.currentText())

            # workaround to detect special characters, same limitation as with python2 because of the server
            # this limitation will be removed when the server side will be ported to python3
            if sys.version_info > (3,): # python3 support only 
                address.encode("ascii") 
                
            # remove https:// or http:// 
            if address.startswith("http://"):
                address = address.split('http://')[1]
            if address.startswith("https://"):
                address = address.split('https://')[1]
                
            
            # new in v12.2, detect destination port if provided
            try:
                if ":" in address:
                    address, destPort = address.split(':', 1)
                if destPort is not None:
                    destPort = int(destPort)
                    # save address in config file
                    Settings.instance().setValue( key = 'Server/port-api', value = "%s" % destPort )
                    Settings.instance().setValue( key = 'Server/port-data', value = "%s" % destPort )
            except Exception as e :
                QMessageBox.critical(self, self.tr("Address") , self.tr("Invalid destination address.") )
                return False
            # end of new
            
            # save address in config file
            addr2save = address
            if destPort is not None:
                addr2save = "%s:%s" % (address, destPort)
            Settings.instance().setValue( key = 'Server/last-addr', value = addr2save )
        except UnicodeEncodeError as e:
            QMessageBox.critical(self, self.tr("Address") , self.tr("Invalid address.") )
            return False
            
        else:
            addrlist = [ addr2save ]
            for i in range(self.addrComboBox.count()):
                if self.addrComboBox.itemText(i) !=  self.addrComboBox.currentText():
                    addrlist.append(self.addrComboBox.itemText(i))
            addrlist.append("") # workaround to avoid to save a qvariant
            Settings.instance().setValue( key = 'Server/addr-list', value = addrlist )
            
        
        # handle proxy
        portProxyHttp = 0
        addressProxyHttp = ''
        proxyActivated = False
        if self.withProxyCheckBox.checkState():
            proxyActivated = True
            
        Settings.instance().setValue( key = 'Server/proxy-active', value = "%s" % proxyActivated )
        
        if self.withProxyCheckBox.checkState() :

            # in this case, active also proxy for the internal web browser and test report
            Settings.instance().setValue( key = 'Server/proxy-web-active', value = "%s" % proxyActivated )

            # retrieve http connection
            portProxyHttp = self.proxyHttpPortEdit.text()
            Settings.instance().setValue( key = 'Server/port-proxy-http', value = portProxyHttp )
            addressProxyHttp = self.proxyHttpAddrEdit.text()
            Settings.instance().setValue( key = 'Server/addr-proxy-http', value = addressProxyHttp )
        
      
            
        # login/password
        try:
            username = str(self.usernameEdit.text())
            
            # workaround to detect special characters, same limitation as with python2 because of the server
            # this limitation will be removed when the server side will be ported to python3
            if sys.version_info > (3,): # python3 support only 
                username.encode("ascii") 
        except UnicodeEncodeError as e:
            QMessageBox.critical(self, self.tr("Login") , self.tr("Invalid login.") )
            return False
        else:
            if int(Settings.instance().readValue( key = 'Server/save-credentials')):
                Settings.instance().setValue( key = 'Server/last-username', value = username )
    
            try:
                password = str(self.passwordEdit.text())
            except UnicodeEncodeError as e:
                QMessageBox.critical(self, self.tr("Login") , self.tr("Invalid password.") )
                return False
            else:
                if int(Settings.instance().readValue( key = 'Server/save-credentials')):
                    # set key for decryption
                    self.oEncryptor.setHexKey( hashlib.md5( username.encode("utf-8") ).hexdigest() ) # for python3 support
                    
                    # encrypt password to config file
                    if password != '':
                        Settings.instance().setValue( key = 'Server/last-pwd', value = self.oEncryptor.encrypt( password )  )
                    else:
                        Settings.instance().setValue( key = 'Server/last-pwd', value ='' )
                ret = ( address, username, password, self.withProxyCheckBox.checkState(), addressProxyHttp, portProxyHttp)
        return ret

TAB_ARCHIVES_POS        =   0
TAB_REPO_POS            =   1
TAB_TESTMGR_POS         =   2
TAB_AGENTS_POS          =   3
TAB_PROBES_POS          =   4
TAB_MISC_POS            =   5
TAB_CT_POS              =   6
TAB_RN_POS              =   7

class WServerExplorer(QWidget, Logger.ClassLogger):
    """
    Server explorer widget
    """
    SERVER_EXPLORER = 1
    BusyCursor = pyqtSignal() 
    BusyCursorChannel = pyqtSignal() 
    ArrowCursor = pyqtSignal() 
    Disconnect = pyqtSignal() 
    ConnectCancelled = pyqtSignal() 
    def __init__(self, parent = None):
        """
        Constructs WServerExplorer widget

        @param parent: 
        @type parent:
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.type = self.SERVER_EXPLORER
        self.name = self.tr("Explorer")

        self.isXmlRpcWorking = False
        self.isRestWorking = False
        
        self.createWidgets()
        self.createActions()
        self.createConnections()
    
    def createConnections(self):
        """
        Create qt connections
        """
        # xmlrpc
        self.wWebService.StartWorking.connect(self.OnWsStartWorking)
        self.wWebService.StartWorkingChannel.connect(self.OnChannelStartWorking)
        self.wWebService.StopWorking.connect(self.OnWsStopWorking)
        self.wWebService.InProgress.connect(self.onNetworkProgress)
        
        # rest
        self.RestService.StartWorking.connect(self.OnRestStartWorking)
        self.RestService.StopWorking.connect(self.OnRestStopWorking)
        self.RestService.InProgress.connect(self.onRestNetworkProgress)
        
    def onRestNetworkProgress(self, bytesRead, totalBytes):
        """
        """
        self.wServerProgress.updateProgressRest(bytesRead, totalBytes)
        
    def OnRestStartWorking(self):
        """
        Called on web service start working
        Emit th qt signal BusyCursor
        """
        self.isRestWorking = True
        self.wServerProgress.startWorkingRest()
        self.BusyCursor.emit()    

    def OnRestStopWorking(self):
        """
        Called on webservice stop working
        Emit the qt signal ArrowCursor
        """
        self.isRestWorking = False
        self.wServerProgress.stopWorkingRest()
        if self.isXmlRpcWorking: return
        self.ArrowCursor.emit()
        
    def onNetworkProgress(self, bytesRead, totalBytes):
        """
        """
        self.wServerProgress.updateProgress(bytesRead, totalBytes)

    def OnWsStartWorking(self):
        """
        Called on web service start working
        Emit th qt signal BusyCursor
        """
        self.isXmlRpcWorking = True
        self.wServerProgress.startWorking()
        self.BusyCursor.emit()    

    def OnChannelStartWorking(self):
        """
        Called on start working of channel
        Emit th qt signal BusyCursorChannel
        """
        self.wServerProgress.startWorking()
        self.BusyCursorChannel.emit()

    def OnWsStopWorking(self):
        """
        Called on webservice stop working
        Emit the qt signal ArrowCursor
        """
        self.isXmlRpcWorking = False
        self.wServerProgress.stopWorking()
        if self.isRestWorking: return
        self.ArrowCursor.emit()

    def createWidgets(self):
        """
        Create qt widget

        QTabWidget:
          ________  ________
         /        \/        \___________
        |                               |
        |                               |
        |                               |
        |_______________________________|
        """
        layout = QHBoxLayout()
        self.wServerStatus = WServerStatus(self)
        self.parent.addWidgetToStatusBar( self.wServerStatus, 0 )

        self.wWebService = XmlrpcNetworkHandler(self)
        self.RestService = RestNetworkHandler(self)

        self.wServerProgress = WServerProgress(self)
        self.parent.addWidgetToStatusBar( self.wServerProgress, 0 )

        
        self.serverTab = QTabWidget()

        Miscellaneous.initialize( parent = self.serverTab ) 
        TestManager.initialize( parent = self.serverTab )
        Probes.initialize( parent = self.serverTab )
        Agents.initialize( parent = self.serverTab )
        Archives.initialize( parent = self.serverTab, mainParent=self.parent )
        ReleaseNotes.initialize( parent = self.serverTab )
        Repositories.initialize( parent = self.serverTab )
        Counters.initialize( parent = self.serverTab )

        Miscellaneous.instance().setEnabled(False)
        TestManager.instance().setEnabled(False)
        Probes.instance().setEnabled(False)
        Agents.instance().setEnabled(False)
        Archives.instance().setEnabled(False)
        ReleaseNotes.instance().setEnabled(False)
        Repositories.instance().setEnabled(False)
        Counters.instance().setEnabled(False)

        self.serverTab.addTab( Archives.instance(), QIcon(":/archives.png") , Archives.instance().name )
        self.serverTab.setTabEnabled( TAB_ARCHIVES_POS, False )
        self.serverTab.addTab( Repositories.instance() , QIcon(":/repositories.png"), Repositories.instance().name  )
        self.serverTab.setTabEnabled( TAB_REPO_POS, False )
        self.serverTab.addTab( TestManager.instance() , QIcon(":/processes.png"), TestManager.instance().name )
        self.serverTab.setTabEnabled( TAB_TESTMGR_POS, False )
        self.serverTab.addTab( Agents.instance() , QIcon(":/agent.png") , Agents.instance().name )
        self.serverTab.setTabEnabled( TAB_AGENTS_POS, False )
        self.serverTab.addTab( Probes.instance() , QIcon(":/probe.png") , Probes.instance().name )
        self.serverTab.setTabEnabled( TAB_PROBES_POS, False )
        self.serverTab.addTab( Miscellaneous.instance(), QIcon(":/server-config.png") , Miscellaneous.instance().name )
        self.serverTab.setTabEnabled( TAB_MISC_POS, False )
        self.serverTab.addTab( Counters.instance(), QIcon(":/reset-counter.png") , Counters.instance().name )
        self.serverTab.setTabEnabled( TAB_CT_POS, False )
        self.serverTab.addTab( ReleaseNotes.instance(), QIcon(":/releasenotes.png") , ReleaseNotes.instance().name )
        self.serverTab.setTabEnabled( TAB_RN_POS, False )
        self.serverTab.setCurrentIndex(-1)

        layout.addWidget(self.serverTab)
        self.setLayout(layout)

    def createActions (self):
        """
        create qt actions
         * connect to the server
         * disconnect from the server
         * check update of the client
        """
        self.connectAction = QtHelper.createAction(self, self.tr("Connect"), self.startConnection, 
                                            icon = QIcon(":/ok.png"))
        self.disconnectAction = QtHelper.createAction(self, self.tr("Disconnect"), self.stopConnection, 
                                            icon = QIcon(":/ko.png"))
        self.disconnectAction.setEnabled( False )
        self.checkUpdateAction = QtHelper.createAction(self, self.tr("Check for update"), self.checkUpdate)
        self.checkUpdateAction.setEnabled(False)

    def checkUpdateAuto(self):
        """
        Call the server to verify if an update is needed for the client
        Update auto
        """
        UCI.instance().getClientUpdateAuto()
        
    def checkUpdate (self):
        """
        Call the server to verify if an update is needed for the client
        """
        UCI.instance().getClientUpdate()
    
    def decodeData(self, b64data):
        """
        Decode data
        """
        data_json = ''
        try:
            data_decoded = base64.b64decode(b64data)
        except Exception as e:
            self.error( 'unable to decode from base64 structure: %s' % str(e) )
        else:
            try:
                data_uncompressed = zlib.decompress(data_decoded)
            except Exception as e:
                self.error( 'unable to decompress: %s' % str(e) )
            else:
                try:
                    if sys.version_info > (3,): # python3 support
                        try:
                            # not nice at all, server can return data encoded with latin1 ...
                            # just a workaround
                            data_tmp = data_uncompressed.decode('latin1').encode('utf-8')
                        except Exception as e:
                            data_tmp = data_uncompressed.decode('utf-8')
                        
                        data_json = json.loads( data_tmp.decode('utf-8') )
                    else:
                        data_json = json.loads( data_uncompressed )
                except Exception as e:
                    self.error( 'unable to decode from json structure: %s' % str(e) )
        return data_json

    def onConnection (self, data):
        """
        Called on successful authentication with the server

        @param data: 
        @type data: dict
        """
        try:
            self.wServerStatus.setStatus( status = self.wServerStatus.ONLINE,
                                          serverIp = UCI.instance().address,
                                          rightUser =  UCI.instance().userRights,
                                          userLogin = UCI.instance().login,
                                          proxyIp = UCI.instance().addressProxyHttp,
                                          serverPort = UCI.instance().portWs )
            # update actions
            self.connectAction.setEnabled(False)
            self.disconnectAction.setEnabled(True)
            self.checkUpdateAction.setEnabled(True)
            
            if UCI.RIGHTS_ADMIN in UCI.instance().userRights or  UCI.RIGHTS_TESTER in UCI.instance().userRights:

                TestManager.instance().active()
                TestManager.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_TESTMGR_POS, True )
                TestManager.instance().loadProjects( data= self.decodeData(data['projects']) )
                TestManager.instance().loadRunning( data = self.decodeData(data['tasks-running']) )
                TestManager.instance().loadWaiting( data = self.decodeData(data['tasks-waiting']) )
                TestManager.instance().loadHistory( data = self.decodeData(data['tasks-history']) )
                TestManager.instance().loadEnqueued( data = self.decodeData(data['tasks-enqueued']) )

                Probes.instance().active()
                Probes.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_PROBES_POS, True )
                Probes.instance().loadData( data = self.decodeData(data['probes']), dataInstalled=self.decodeData(data['probes-installed']) )
                Probes.instance().loadStats( data = self.decodeData(data['probes-stats']) )
                Probes.instance().loadDefault( data = self.decodeData(data['probes-default']) )
    
                Agents.instance().active()
                Agents.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_AGENTS_POS, True )
                Agents.instance().loadData( data = self.decodeData(data['agents']), dataInstalled=self.decodeData(data['agents-installed']) )
                Agents.instance().loadStats( data = self.decodeData(data['agents-stats']) )
                Agents.instance().loadDefault( data = self.decodeData(data['agents-default']) )

            if UCI.RIGHTS_ADMIN in UCI.instance().userRights or  UCI.RIGHTS_TESTER in UCI.instance().userRights or  UCI.RIGHTS_LEADER in UCI.instance().userRights:

                Archives.instance().active()
                Archives.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_ARCHIVES_POS, True )
                self.serverTab.setCurrentIndex(TAB_ARCHIVES_POS)
                Archives.instance().cleanTreeView()
                Repositories.instance().cleanStatsArchives()
                rootItem = Archives.instance().createRootItem()
                Archives.instance().loadData( data = self.decodeData(data['archives']), parent=rootItem )
                Archives.instance().initializeProjects( projects=self.decodeData(data['projects']), defaultProject=data['default-project'] )

            if UCI.RIGHTS_ADMIN in UCI.instance().userRights :

                Miscellaneous.instance().active()
                Miscellaneous.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_MISC_POS, True )
                Miscellaneous.instance().loadData( data = self.decodeData(data['informations']) )
                Miscellaneous.instance().loadStats( data = self.decodeData(data['stats-server']) )
                
                Repositories.instance().active()
                Repositories.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_REPO_POS, True )
                
                Repositories.instance().initializeProjects( projects=self.decodeData(data['projects']), defaultProject=data['default-project'] )
                Repositories.instance().loadData(   data = data['stats-repo-tests'], 
                                                    backups=self.decodeData(data['backups-repo-tests']) )
                Repositories.instance().loadDataAdapters(   data = data['stats-repo-adapters'],
                                                            backups=self.decodeData(data['backups-repo-adapters'])   )
                Repositories.instance().loadDataLibraries(  data = data['stats-repo-libraries'],
                                                            backups=self.decodeData(data['backups-repo-libraries'])   )
                Repositories.instance().loadDataArchives( data = data['stats-repo-archives'],
                                                            backups=self.decodeData(data['backups-repo-archives']) )
                
            if UCI.RIGHTS_ADMIN in UCI.instance().userRights or  UCI.RIGHTS_TESTER in UCI.instance().userRights or \
                UCI.RIGHTS_DEVELOPER in UCI.instance().userRights or  UCI.RIGHTS_LEADER in UCI.instance().userRights:

                Settings.instance().setServerContext( self.decodeData(data['informations']) )
                ReleaseNotes.instance().active()
                ReleaseNotes.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_RN_POS, True )
                if len(UCI.instance().userRights) == 1 and UCI.instance().userRights[0] == UCI.RIGHTS_DEVELOPER:
                    self.serverTab.setCurrentIndex(TAB_RN_POS)
                
                rnDecoded = base64.b64decode( data['rn'] )
                rnAdpDecoded = base64.b64decode( data['rnAdp'] )
                rnLibAdpDecoded = base64.b64decode( data['rnLibAdp'] )
                rnToolboxDecoded =  base64.b64decode( data['rnToolbox'] )
                ReleaseNotes.instance().loadData(   data = rnDecoded, 
                                                    dataAdp = rnAdpDecoded,
                                                    dataLibAdp=rnLibAdpDecoded, 
                                                    dataToolbox=rnToolboxDecoded  )

                Counters.instance().active()
                Counters.instance().setEnabled(True)
                self.serverTab.setTabEnabled( TAB_CT_POS, True )

                Counters.instance().loadData(counters=data['stats'] )
            
            if UCI.RIGHTS_TESTER in UCI.instance().userRights or UCI.RIGHTS_DEVELOPER in UCI.instance().userRights:
                Counters.instance().deactivate()
            else:
                Counters.instance().active()
                
        except Exception as e:
            self.error('error on connection: %s' % str(e) )
            self.stopConnection()
            self.wWebService.stopWorking()
            self.RestService.stopWorking()
            
    def onDisconnection (self):
        """
        Called on disconnection with the server
        Deactivates all tabs
        """
        
        self.wServerStatus.setStatus( status = self.wServerStatus.OFFLINE )
        
        # update actions
        self.connectAction.setEnabled(True)
        self.disconnectAction.setEnabled(False)
        self.checkUpdateAction.setEnabled(False)

        Miscellaneous.instance().deactivate()
        TestManager.instance().deactivate()
        Probes.instance().deactivate()
        Agents.instance().deactivate()
        Archives.instance().deactivate()
        ReleaseNotes.instance().deactivate()
        Repositories.instance().deactivate()

        Miscellaneous.instance().setEnabled(False)
        TestManager.instance().setEnabled(False)
        Probes.instance().setEnabled(False)
        Agents.instance().setEnabled(False)
        Archives.instance().setEnabled(False)
        ReleaseNotes.instance().setEnabled(False)
        Repositories.instance().setEnabled(False)
        Counters.instance().setEnabled(False)

        self.serverTab.setTabEnabled( TAB_ARCHIVES_POS, False )
        self.serverTab.setTabEnabled( TAB_REPO_POS, False )
        self.serverTab.setTabEnabled( TAB_TESTMGR_POS, False )
        self.serverTab.setTabEnabled( TAB_PROBES_POS, False )
        self.serverTab.setTabEnabled( TAB_AGENTS_POS, False )
        self.serverTab.setTabEnabled( TAB_MISC_POS, False )
        self.serverTab.setTabEnabled( TAB_RN_POS, False )
        self.serverTab.setTabEnabled( TAB_CT_POS, False )
        self.serverTab.setCurrentIndex(-1)
    
    def startConnection (self):
        """
        Open dialog to retrieve credential and server url 
        and starts the connection
        """
        dConnect = DServerConnection( self )
        if dConnect.exec_() == QDialog.Accepted:
            retCtx = dConnect.getCtx()
            if retCtx:
                started = self.wWebService.startWorking()
                addr, login, pwd, supportProxy, addrProxyHttp, portProxyHttp  = retCtx
                if started:
                    ret = UCI.instance().setCtx(address = addr, login = login, password = pwd, 
                                                supportProxy=supportProxy, addressProxyHttp=addrProxyHttp,
                                                portProxyHttp=portProxyHttp)
                    if ret is not None:
                        self.connectAction.setEnabled(False)
                        self.disconnectAction.setEnabled(True)
                        UCI.instance().connectChannel()
                    else:
                        self.wWebService.stopWorking()
                        self.RestService.stopWorking()
            else:
                self.ConnectCancelled.emit()
        else:
            self.ConnectCancelled.emit()
            
    def enableConnect(self):
        """
        Enable connect button
        """
        self.connectAction.setEnabled(True)
        self.disconnectAction.setEnabled(False)

    def stopConnection (self):
        """
        Stops the connection with the server
        """
        self.Disconnect.emit()

    def notifyReceived (self, data):
        """
        Dispatchs notify between all plugins

        @param data: expected values in ( 'task', ( action, {} ) )
        @type data: tuple
        """ 
        action, event = data[1]
        if data[0] == 'progressbar':    
            cur_progress, max_progress = event
            self.wWebService.WsUpdateDataReadProgress(cur_progress, max_progress)
        elif data[0] == 'context-server':       
            Settings.instance().setServerContext( event )
            Miscellaneous.instance().cleanContext()
            Miscellaneous.instance().loadData( data=event )
        elif data[0] == 'task':         
            TestManager.instance().refreshData( data = event, action = action ) 
        elif data[0] == 'task-running': 
            TestManager.instance().refreshRunningTask( data = event, action = action )
        elif data[0] == 'task-waiting': 
            TestManager.instance().refreshWaitingTask( data = event, action = action )
        elif data[0] == 'task-history': 
            TestManager.instance().refreshHistoryTask( data = event, action = action )
        elif data[0] == 'task-enqueued': 
            TestManager.instance().refreshEnqueuedTask( data = event, action = action )
        elif data[0] == 'archive':
            if action == 'reset':
                Archives.instance().cleanTreeView()
                Archives.instance().createRootItem()
                Archives.instance().resetPreview()
            else:
                if 'stats-repo-archives' in event:
                    Archives.instance().refreshData(data = event['archive'], data_stats=event['stats-repo-archives'], action = action )
                else:
                    Archives.instance().refreshData(data = event['archive'], data_stats=None, action = action )
        elif data[0] == 'archives':
            if action == 'reset-backups':
                Repositories.instance().resetBackupArchivesPart()
            elif action == 'add-backup':
                Repositories.instance().newBackupArchives(data = event )
            else:
                self.error( 'repo to reset unknwon: %s' % str(event) )
        elif data[0] == 'stats':
            Counters.instance().refreshData(data = event, action = action )
        elif data[0] == 'probes':
            Probes.instance().refreshData(data = event, action = action )
        elif data[0] == 'probes-default':
            Probes.instance().refreshDataDefault(data = event, action = action )
        elif data[0] == 'agents':
            Agents.instance().refreshData(data = event, action = action )
        elif data[0] == 'agents-default':
            Agents.instance().refreshDataDefault(data = event, action = action )
        elif data[0] == 'repositories':
            if action == 'reset':
                if 'repo-adapters' in event:
                    Repositories.instance().resetBackupAdpsPart()
                elif 'repo-libraries' in event:
                    Repositories.instance().resetBackupLibsPart()
                elif 'repo-tests' in event:
                    Repositories.instance().resetBackupArchivesPart()
                else:
                    self.error( 'repo to reset unknwon: %s' % str(event) )
            else:
                Repositories.instance().newBackup(data = event )
        else:
            self.error( "notify received unknown: %s" % str(data) )

    def onRefreshStatsRepo(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        Repositories.instance().loadData(   data = data['stats-repo-tests'],
                                            backups=self.decodeData(data['backups-repo-tests']) )   

    def onRefreshStatsRepoAdapters(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        Repositories.instance().loadDataAdapters( data = data['stats-repo-adapters'], 
                                                    backups=self.decodeData(data['backups-repo-adapters']) )    

    def onRefreshStatsRepoLibraries(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        Repositories.instance().loadDataLibraries( data = data['stats-repo-libraries'], 
                                                    backups=self.decodeData(data['backups-repo-libraries']) )   
                                                    
    def onRefreshStatsRepoArchives(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        Repositories.instance().loadDataArchives(   data = data['stats-repo-archives'], 
                                                    backups=self.decodeData(data['backups-repo-archives']) )   

    def onRefreshStatsServer(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        Miscellaneous.instance().loadStats( data = self.decodeData(data) )

    def onRefreshContextServer(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:
        """
        data_decoded =  self.decodeData(data)
        Settings.instance().setServerContext(data_decoded)
        Miscellaneous.instance().cleanContext()
        Miscellaneous.instance().loadData( data = data_decoded )

    def onRefreshArchives(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:     
        """
        Archives.instance().cleanTreeView()
        rootItem = Archives.instance().createRootItem()
        Archives.instance().loadData( data = self.decodeData(data), parent=rootItem )
        
    def onRefreshRunningAgents(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:     
        """
        Agents.instance().resetNbProbes()
        Agents.instance().loadData(data = self.decodeData(data) )
    
    def onRefreshDefaultAgents(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:     
        """
        Agents.instance().loadDefault(data = self.decodeData(data) )

    def onRefreshRunningProbes(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:     
        """
        Probes.instance().loadData(data = self.decodeData(data) )
    
    def onRefreshDefaultProbes(self, data):
        """
        Refresh data on xml rpc call

        @param data: 
        @type data:     
        """
        Probes.instance().loadDefault(data = self.decodeData(data) )

    def onRefreshTasksWaiting(self, data):
        """
        Called on refresh tasks waiting
        """
        if len(data['tasks-waiting']):
            TestManager.instance().updateWaiting( data = self.decodeData(data['tasks-waiting']) )

    def onRefreshTasksRunning(self, data):
        """
        Called on refresh task running
        """
        if len(data['tasks-running']):
            TestManager.instance().updateRunning( data = self.decodeData(data['tasks-running']) )

    def onRefreshTasksHistory(self, data):
        """
        Called on refresh task history
        """
        if len(data['tasks-history']):
            TestManager.instance().updateHistory( data = self.decodeData(data['tasks-history']) )

    def onWebCall(self, data):
        """
        """
        self.wWebService.NetworkCall(postData=data)
        
    def onRestCall(self, uri, request, body=''):
        """
        """
        self.RestService.NetworkCall(req=(uri, request, body) )
       
    def configureServer(self, address, port, scheme, hostname):
        """
        Configure server for network handler
        """
        self.wWebService.setWsAddress( address= address, port = port,
                                        scheme=scheme, 
                                        webpath=Settings.instance().readValue( key = 'Server/xmlrpc-path' ),
                                        hostname=hostname )
        self.RestService.setWsAddress( address= address, port = port,
                                        scheme=scheme, 
                                        webpath=Settings.instance().readValue( key = 'Server/rest-path' ),
                                        hostname=hostname )

    def configureProxy(self, ip, port):
        """
        Configure proxy for network handler
        """
        self.wWebService.setWsProxy(ip=ip, port=port)
        self.RestService.setWsProxy(ip=ip, port=port)
        
    def stopWorking(self):
        """
        Stop working
        """
        self.wWebService.stopWorking()
        self.RestService.stopWorking()
        
    def rest(self):
        """
        """
        return self.RestService
        
    def xmlrpc(self):
        """
        """
        return self.wWebService
        
        
ServerExplorer = None # Singleton
def instance ():
    """
    Returns Singleton

    @return:
    @rtype:
    """
    return ServerExplorer

def initialize (parent):
    """
    Initialize WServerExplorer widget
    """
    global ServerExplorer
    ServerExplorer = WServerExplorer(parent)

def finalize ():
    """
    Destroy Singleton
    """
    global ServerExplorer
    if ServerExplorer:
        ServerExplorer = None