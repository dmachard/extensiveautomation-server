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

"""
Http replay extension for the extensive client
Write test automatically from network trace
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError: # support python3
    xrange = range
    
try:
    from PyQt4.QtGui import (QIcon, QMenu, QToolBar, QLineEdit, QRegExpValidator, QSizePolicy, 
                            QIntValidator, QProgressBar, QGroupBox, QRadioButton, QHBoxLayout, 
                            QVBoxLayout, QGridLayout, QLabel, QTextEdit, QTextCursor, QMessageBox, 
                            QFileDialog)
    from PyQt4.QtCore import (Qt, QRegExp, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QRegExpValidator, QIntValidator, QTextCursor)
    from PyQt5.QtWidgets import (QMenu, QToolBar, QLineEdit, QSizePolicy, QProgressBar, QGroupBox, 
                                QRadioButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLabel, 
                                QTextEdit, QMessageBox, QFileDialog)
    from PyQt5.QtCore import (Qt, QRegExp, QSize)
    
from Libs import QtHelper, Logger

import UserClientInterface as UCI
import RestClientInterface as RCI

import Workspace as WWorkspace
import Settings
import DefaultTemplates

if sys.version_info > (3,):
    import Libs.Pcap.parse as PcapParse
    import Libs.Pcap.pcap as PcapReader
    import Libs.Pcap.pcapng as PcapngReader
else:
    import dpkt

import socket

TU=0
TS=1

WINDOW_TITLE = "Capture HTTP"
 
HTTP_METHOD = {b'GET': b'', b'POST': b'', b'PUT': b'', b'DELETE': b'', b'HEAD': b'', b'TRACE': b'', 
                b'OPTIONS': b'', b'PATCH': b'', b'SUBSCRIBE': b'', b'NOTIFY': b'', b'M-SEARCH': b''}

def isRequest(body):
    """
    check if is http request by the first line
    """
    idx = body.find(b' ')
    if idx < 0:
        return False
    method = body[0:idx]
    return method in HTTP_METHOD
    
class DHttpReplay(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Http replay dialog
    """
    def __init__(self, parent = None, offlineMode=False):
        """
        Constructor

        @param parent: 
        @type parent:
        """
        super(DHttpReplay, self).__init__(parent)
        self.offlineMode = offlineMode
        self.defaultIp = "127.0.0.1"
        self.defaultPort = "80"
        self.newTest = ''
        self.newTestExec = ''
        self.newInputs = []
        self.requests = []
        self.responses = []
        self.defaultTemplates = DefaultTemplates.Templates()
        self.testType = None

        self.createDialog()
        self.createConnections()
        self.createActions()
        self.createToolbar()

    def createActions (self):
        """
        Create qt actions
        """
        self.openAction = QtHelper.createAction(self, "&Open", self.importTrace, icon=QIcon(":/folder_add.png"), tip = 'Open network trace.')
        self.exportTUAction = QtHelper.createAction(self, "&Test Unit", self.exportToTU, icon=QIcon(":/%s.png" % WWorkspace.TestUnit.TYPE),
                                            tip = 'Export to Test Unit')
        self.exportTSAction = QtHelper.createAction(self, "&Test Suite", self.exportToTS, icon=QIcon(":/%s.png" % WWorkspace.TestSuite.TYPE),
                                            tip = 'Export to Test Suite')
        self.cancelAction = QtHelper.createAction(self, "&Cancel", self.reject, tip = 'Cancel')
        
        menu = QMenu(self)
        menu.addAction( self.exportTUAction )
        menu.addAction( self.exportTSAction )

        self.exportToAction = QtHelper.createAction(self, "&Export to", self.exportToTU, icon=QIcon(":/%s.png" % WWorkspace.TestUnit.TYPE),   tip = 'Export to tests' )
        self.exportToAction.setMenu(menu)
        self.exportToAction.setEnabled(False)

    def createDialog(self):
        """
        Create dialog
        """

        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

        self.setWindowTitle(WINDOW_TITLE)
        self.resize(500, 400)

        self.ipEdit = QLineEdit(self.defaultIp)
        ipRegExpVal = QRegExpValidator(self)
        ipRegExp = QRegExp("\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
        ipRegExpVal.setRegExp(ipRegExp)
        self.ipEdit.setValidator(ipRegExpVal)

        self.portEdit = QLineEdit(self.defaultPort)
        self.portEdit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Fixed )
        validatorPort = QIntValidator (self)
        self.portEdit.setValidator(validatorPort)

        self.progressBar = QProgressBar(self)
        self.progressBar.setMaximum(100)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setAlignment(Qt.AlignCenter)
        self.progressBar.setObjectName("progressBar")
        
        self.guiSikuliGroupBox = QGroupBox("")
        self.guiSikuliGroupBox.setFlat(True)
        self.automaticAdp = QRadioButton("Automatic")
        self.automaticAdp.setChecked(True)
        self.defaultAdp = QRadioButton("Default")
        self.genericAdp = QRadioButton("Generic")
        vbox = QHBoxLayout()
        vbox.addWidget(self.automaticAdp)
        vbox.addWidget(self.defaultAdp)
        vbox.addWidget(self.genericAdp)
        vbox.addStretch(1)
        self.guiSikuliGroupBox.setLayout(vbox)

        
        layout = QVBoxLayout()
        layout.addWidget(self.dockToolbar)
        layout.addSpacing(12)
        paramLayout = QGridLayout()
        paramLayout.addWidget(QLabel("Destination IP:"), 0, 0, Qt.AlignRight)
        paramLayout.addWidget(self.ipEdit, 0, 1)
        paramLayout.addWidget(QLabel("Destination Port:"), 1, 0, Qt.AlignRight)
        paramLayout.addWidget(self.portEdit, 1, 1)
        paramLayout.addWidget( QLabel( self.tr("Gui adapter selector:") ), 2, 0, Qt.AlignRight)
        paramLayout.addWidget(self.guiSikuliGroupBox, 2, 1)
        layout.addLayout(paramLayout)

        self.logsEdit = QTextEdit()
        self.logsEdit.setReadOnly(True)
        self.logsEdit.setTextInteractionFlags(Qt.NoTextInteraction)

        layout.addSpacing(12)
        layout.addWidget(self.logsEdit)
        layout.addSpacing(12)
        layout.addWidget(self.progressBar)

        self.setLayout(layout)

    def createToolbar(self):
        """
        Create toolbar
        """
        self.dockToolbar.setObjectName("File toolbar")
        self.dockToolbar.addAction(self.openAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.exportToAction)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))
        
    def createConnections(self):
        """
        Create qt connections
        """
        pass

    def autoScrollOnTextEdit(self):
        """
        Automatic scroll on text edit
        """
        cursor = self.logsEdit.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.logsEdit.setTextCursor(cursor)
    
    def strip_html(self, txt):
        """
        Strip html
        """
        if "<" in txt:
            txt = txt.replace( '<', '&lt;' )
        if ">" in txt:
            txt = txt.replace( '>', '&gt;' )
        return txt
        
    def addLogSuccess(self, txt):
        """
        Add log success in the text edit
        """
        self.logsEdit.insertHtml( "<span style='color:darkgreen'>%s</span><br />" % unicode( self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()

    def addLogWarning(self, txt):
        """
        Add log warning in the text edit
        """
        self.logsEdit.insertHtml( "<span style='color:darkorange'>%s</span><br />" % unicode( self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()

    def addLogError(self, txt):
        """
        Add log error in the text edit
        """
        self.logsEdit.insertHtml( "<span style='color:red'>%s</span><br />" % unicode( self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()

    def addLog(self, txt):
        """
        Append log to the logsEdit widget
        """
        self.logsEdit.insertHtml( "%s<br />" % unicode( self.strip_html(txt) ) )
        self.autoScrollOnTextEdit()

    def importTrace(self):
        """
        Import network trace
        """
        self.logsEdit.clear()
        self.testType = None

        if not self.offlineMode:
            if not RCI.instance().isAuthenticated():
                self.addLogWarning(txt="<< Connect to the test center in first!" )
                QMessageBox.warning(self, "Import" , "Connect to the test center in first!")
                return

        self.exportToAction.setEnabled(False)
        self.newTest = ''
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)

        if sys.version_info > (3,):
            fileName = QFileDialog.getOpenFileName(self,  self.tr("Open File"), "", "Network dump (*.cap;*.pcap;*.pcapng)")
        else:
            fileName = QFileDialog.getOpenFileName(self,  self.tr("Open File"), "", "Network dump (*.cap)")
        # new in v18 to support qt5
        if QtHelper.IS_QT5:
            _fileName, _type = fileName
        else:
            _fileName = fileName
        # end of new
        
        if not _fileName:
            return
        
        if sys.version_info < (3,):
            extension = str(_fileName).rsplit(".", 1)[1]
            if not ( extension == "cap" ):
                self.addLogError(txt="<< File not supported %s" % _fileName)
                QMessageBox.critical(self, "Open" , "File not supported")
                return

        _fileName = str(_fileName)
        capName = _fileName.rsplit("/", 1)[1]

        self.addLogSuccess(txt=">> Reading the file %s" % _fileName)
        if sys.version_info > (3,):
            self.readFileV2(fileName=_fileName)
        else:
            self.readFile(fileName=_fileName)
    
    def exportToTS(self):
        """
        Export to test suite
        """
        self.testType = TS
        self.exportToTest(TS=True, TU=False)

    def exportToTU(self):
        """
        Export to test unit
        """
        self.testType = TU
        self.exportToTest(TS=False, TU=True)
        
    def searchHTTP(self):
        """
        Search HTTP module in assistant
        """
        # modules accessor
        ret = "SutAdapters"
        if self.automaticAdp.isChecked():
            isGeneric = WWorkspace.Helper.instance().isGuiGeneric(name="GUI")
            if isGeneric:
                ret =  "SutAdapters.Generic"
        elif self.defaultAdp.isChecked():
            return ret
        elif self.genericAdp.isChecked():
            ret =  "SutAdapters.Generic"
        else:
            pass
        return ret
        
    def exportToTest(self, TS=True, TU=False):
        """
        Export to test
        """
        if not RCI.instance().isAuthenticated():
            self.addLogWarning(txt="<< Connect to the test center in first!" )
            QMessageBox.warning(self, "Import" , "Connect to the test center in first!")
            return


        if TS:
            self.newTest = self.defaultTemplates.getTestDefinitionAuto()
            self.newTestExec = self.defaultTemplates.getTestExecutionAuto()
        if TU:
            self.newTest = self.defaultTemplates.getTestUnitDefinitionAuto()

        destIp = str(self.ipEdit.text()) 
        destPort = str(self.portEdit.text())

        self.newInputs = []
        self.newInputs.append( {'type': 'self-ip', 'name': 'BIND_IP' , 'description': '', 'value' : '0.0.0.0', 'color': '' } )
        self.newInputs.append( {'type': 'int', 'name': 'BIND_PORT' , 'description': '', 'value' : '0', 'color': '' } )
        self.newInputs.append( {'type': 'str', 'name': 'DEST_IP' , 'description': '', 'value' : '%s' % destIp, 'color': '' } )
        self.newInputs.append( {'type': 'int', 'name': 'DEST_PORT' , 'description': '', 'value' : '%s' % destPort, 'color': '' } )
        self.newInputs.append( {'type': 'bool', 'name': 'DEBUG' , 'description': '', 'value' : 'False', 'color': '' } )
        self.newInputs.append( {'type': 'float', 'name': 'TIMEOUT' , 'description': '', 'value' : '5.0', 'color': '' } )

        adps = """self.ADP_HTTP = %s.HTTP.Client(parent=self, bindIp=input('BIND_IP'), bindPort=input('BIND_PORT'), destinationIp=input('DEST_IP'), destinationPort=input('DEST_PORT'), debug=input('DEBUG'))""" % self.searchHTTP()

        # prepare steps
        steps = []
        j = 0
        for i in xrange(len(self.requests)):
            j = i + 1
            if sys.version_info > (3,): # python3 support
                (source, dest, source_port, dest_port, buf_req, reqDecoded) = self.requests[i]
                http_method = str(reqDecoded['method'], 'utf8')
                http_status = 'no'
                http_reason = ''
            else:
                http_method = self.requests[i]['tcp-object'].method
                http_status = 'no'
                http_reason = ''
            try:
                if sys.version_info > (3,): # python3 support
                    (sourceRsp, destRsp, sourcePortRsp, destPortRsp, bufReqRsp, reqDecodedRsp) = self.responses[i]
                    http_status = str(reqDecodedRsp['code'])
                    http_reason = str(reqDecodedRsp['phrase'], 'utf8')
                else:
                    http_status = self.responses[i]['tcp-object'].status
                    http_reason = self.responses[i]['tcp-object'].reason
            except Exception as e:
                print(e)
            steps.append( 'self.step%s = self.addStep(expected="%s %s response", description="send %s request", summary="send %s request")' % 
                            (j, http_status, http_reason, http_method, http_method) )
                            

        tests = []
        for i in xrange(len(self.requests)):
            j = i + 1
            if sys.version_info > (3,): # python3 support
                (source, dest, source_port, dest_port, buf_req, reqDecoded) = self.requests[i]
            tests.append( "# request %s"  % j )
            tests.append( 'self.step%s.start()' % j )

            if sys.version_info > (3,): # python3 support
                lines_req = buf_req.splitlines()
            else:
                lines_req = self.requests[i]['tcp-data'].splitlines()
                
            if sys.version_info > (3,): # python3 support
                tests.append( 'rawHttp = [%s]' % lines_req[0].replace(b'"', b'\\"') )
            else:
                tests.append( 'rawHttp = ["%s"]' % lines_req[0].replace(b'"', b'\\"') )
            for lreq in lines_req[1:]:
                if sys.version_info > (3,): # python3 support
                    tests.append( 'rawHttp.append(%s)' % lreq.replace(b'"', b'\\"') ) 
                else:
                    tests.append( 'rawHttp.append("%s")' % lreq.replace(b'"', b'\\"') ) 

            tests.append( '' ) 
            tests.append( 'req_tpl = self.ADP_HTTP.constructTemplateRequest(rawHttp=rawHttp)') 
            tests.append( 'req = self.ADP_HTTP.sendRequest(tpl=req_tpl)' ) 

            try:
                tests.append( '' ) 
                if sys.version_info > (3,): # python3 support
                    (sourceRsp, destRsp, sourcePortRsp, destPortRsp, bufReqRsp, reqDecodedRsp) = self.responses[i]
                    lines_res = bufReqRsp.splitlines()
                else:
                    lines_res = self.responses[i]['tcp-data'].splitlines()
                if sys.version_info > (3,): # python3 support
                    tests.append( 'rawHttpRsp = [%s]' % lines_res[0].replace( b"'", b"\\'") )
                else:
                    tests.append( 'rawHttpRsp = ["%s"]' % lines_res[0].replace(b'"', b'\\"') )
                for lres in lines_res[1:]:
                    if sys.version_info > (3,): # python3 support
                        tests.append( 'rawHttpRsp.append(%s)' % lres.replace( b"'", b"\\'") )
                    else:
                        tests.append( 'rawHttpRsp.append("%s")' % lres.replace(b'"', b'\\"') ) 
            except Exception as e:
                self.error("unable to append response: %s" % e)
            tests.append( 'rsp_tpl = self.ADP_HTTP.constructTemplateResponse(rawHttp=rawHttpRsp)') 
            tests.append( "rsp = self.ADP_HTTP.hasReceivedResponse(expected=rsp_tpl, timeout=input('TIMEOUT'))" ) 
            tests.append( 'if rsp is None:' ) 
            tests.append( '\tself.step%s.setFailed(actual="incorrect response")' % j) 
            tests.append( 'else:' ) 
            tests.append( '\tself.step%s.setPassed(actual="ok")' % j ) 
            tests.append( '' ) 
        if TS:
            init = """self.ADP_HTTP.connect()
		connected = self.ADP_HTTP.isConnected( timeout=input('TIMEOUT') )
		if not connected:
			self.abort( 'unable to connect to the tcp port %s'  )
""" % str(self.portEdit.text())

        if TU:
            init = """self.ADP_HTTP.connect()
	connected = self.ADP_HTTP.isConnected( timeout=input('TIMEOUT') )
	if not connected:
		self.abort( 'unable to connect to the tcp port %s'  )
""" % str(self.portEdit.text())

        if TS:  
            cleanup = """self.ADP_HTTP.disconnect()
		disconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
		if not disconnected:
			self.error( 'unable to disconnect from the tcp port %s' )
""" % str(self.portEdit.text())

        if TU:
            cleanup = """self.ADP_HTTP.disconnect()
	disconnected = self.ADP_HTTP.isDisconnected( timeout=input('TIMEOUT') )
	if not disconnected:
		self.error( 'unable to disconnect from the tcp port %s' )
""" % str(self.portEdit.text())

        self.newTest = self.newTest.replace( "<<PURPOSE>>", 'self.setPurpose(purpose="Replay HTTP")' )
        self.newTest = self.newTest.replace( "<<ADPS>>", adps )
        if TS:
            self.newTest = self.newTest.replace( "<<STEPS>>", '\n\t\t'.join(steps) )
        if TU:
            self.newTest = self.newTest.replace( "<<STEPS>>", '\n\t'.join(steps) )
        self.newTest = self.newTest.replace( "<<INIT>>", init )
        self.newTest = self.newTest.replace( "<<CLEANUP>>", cleanup )
        if TS:
            self.newTest = self.newTest.replace( "<<TESTS>>", '\n\t\t'.join(tests) )
        if TU:
            self.newTest = self.newTest.replace( "<<TESTS>>", '\n\t'.join(tests) )

        self.accept()

    def decodeHttpRequest(self, data):
        """
        Decode http request
        Content chunked not yet implemented
        """
        http = {"type": "request"}
        lines = data.splitlines()
        try:
            request_line = lines[0]
        except Exception:
            self.error("unable to decode http request: %s" % lines)
            return None
            
        try:
            http["method"] = request_line.split(b" ", 2)[0]
            http["uri"] = request_line.split(b" ", 2)[1]
            http["version"] = request_line.split(b" ", )[2]
        except Exception:
            self.error("unable to decode status code in the http response: %s" % request_line)
            return None

        http["body"] = data.split(b"\r\n\r\n")[1]
        
        headers = []
        contentLenght=0
        contentChunked=False
        for hdr in  data.split(b"\r\n\r\n")[0].splitlines()[1:]:
            if len(hdr):
                k, v = hdr.split(b":", 1)
                if k.lower() == b"content-length":
                    contentLenght = int(v)
                if k.lower() == b"transfer-encoding":
                    if v.lowert() == b"chunked":
                        contentChunked=True
                        
                headers.append(hdr)
                
        http["headers"] = headers

        if len(http["body"]) != contentLenght:
            return None # need more data
        return http
        
    def decodeHttpResponse(self, data):
        """
        Decode http response without body
        """
        http = {"type": "response"}
        lines = data.splitlines()
        try:
            status_line = lines[0]
        except Exception:
            self.error("unable to decode http response: %s" % lines)
            return None
            
        try:
            http["code"] = int(status_line.split(b" ")[1])
            http["phrase"] = status_line.split(b" ", 2)[2]
        except Exception:
            self.error("unable to decode status code in the http response: %s" % status_line)
            return None
        
        http["headers"] = lines[1:]
        return http

    def readFileV2(self, fileName):
        """
        Read pcap file 
        Support pcap-ng too
        """
        fd = open(fileName, 'rb')
        fileFormat, fileHead = PcapParse.extractFormat(fd)
        if fileFormat == PcapParse.FileFormat.PCAP:
            self.trace("pcap file detected")
            pcapFile = PcapReader.PcapFile(fd, fileHead).read_packet
            self.readFilePacket(pcapFile=pcapFile)
        elif fileFormat == PcapParse.FileFormat.PCAP_NG:
            self.trace("pcap-png file detected")
            pcapFile = PcapngReader.PcapngFile(fd, fileHead).read_packet
            self.readFilePacket(pcapFile=pcapFile)
        else:
            self.addLogError(txt="<< Error to open the network trace")
            self.error( 'unable to open the network trace: file format = %s' % fileFormat )
            QMessageBox.critical(self, "Import" , "File not supported")
            
    def __readRequest(self, buffer, data, request, output ):
        """
        Read request
        """
        buffer += data
        if b'\r\n\r\n' in data:
            reqDecoded = self.decodeHttpRequest(data = buffer)
            if reqDecoded is not None:
                output.append( request + (reqDecoded, ) ) 
                buffer = b''
            else:
                print( "need more data: decode request failed" )
        else:
            print( "need more data, no body separator detected on request" )
        
    def readFilePacket(self, pcapFile):
        """
        Read file packet by packet
        """
        ip_expected = str( self.ipEdit.text() )
        port_expected = int( self.portEdit.text() )

        # read packet)
        packets = pcapFile()
        ethernetPackets = list(packets)
        self.addLogSuccess(txt="<< Number of packets detected: %s " % len(ethernetPackets))

        # extract tcp packet according to the expected ip and port
        tcpPacketsSent = []
        tcpPacketsRecv = []
        i = 1
        self.progressBar.setMaximum(len(ethernetPackets))
        self.progressBar.setValue(0)
        for pkt in ethernetPackets:
            self.progressBar.setValue(i)
            i += 1
            pktDecoded = PcapParse.decodePacket(pkt, getTcp=True, getUdp=False)
            if pktDecoded is not None:
                (source, dest, source_port, dest_port, data) = pktDecoded
                # skip when no data exists
                if dest == ip_expected and int(dest_port) == int(port_expected) and len(data) > 0 :
                    tcpPacketsSent.append( pktDecoded )
                if source == ip_expected and int(source_port) == int(port_expected) and len(data) > 0:
                    tcpPacketsRecv.append( pktDecoded )
        self.addLogSuccess(txt="<< Number of TCP packets sent: %s " % len(tcpPacketsSent))
        self.addLogSuccess(txt="<< Number of TCP packets received: %s " % len(tcpPacketsRecv))        
        
        # decode https requests
        self.requests = []
        buf_req = b''
        i = 1
        self.progressBar.setMaximum(len(tcpPacketsSent))
        self.progressBar.setValue(0)
        # decode the complete packet
        for req in tcpPacketsSent:
            self.progressBar.setValue(i)
            i += 1
            (source, dest, source_port, dest_port, data) = req
            if buf_req:
                buf_req += data
                if b'\r\n\r\n' in data:
                    reqDecoded = self.decodeHttpRequest(data = buf_req)
                    if reqDecoded is not None:
                        self.requests.append( (source, dest, source_port, dest_port, buf_req, reqDecoded) ) 
                        buf_req = b''
            else:
                if isRequest(data):
                    buf_req += data
                    if b'\r\n\r\n' in data:
                        reqDecoded = self.decodeHttpRequest(data = buf_req)
                        if reqDecoded is not None:
                            self.requests.append( (source, dest, source_port, dest_port, buf_req, reqDecoded) ) 
                            buf_req = b''
                            
        self.addLogSuccess(txt="<< Number of HTTP requests extracted: %s " % len(self.requests))
        
        # decode https response
        self.responses = []
        buf_rsp = b''
        i = 1
        self.progressBar.setMaximum(len(tcpPacketsRecv))
        self.progressBar.setValue(0)
        # decode just headers for response
        for req in tcpPacketsRecv:
            self.progressBar.setValue(i)
            i += 1
            (source, dest, source_port, dest_port, data) = req
            if buf_rsp:
                buf_rsp += data
                # try to decode response without body
                if b'\r\n\r\n' in data:
                    rspDecoded = self.decodeHttpResponse(data = buf_rsp)
                    if rspDecoded is not None:
                        self.responses.append( (source, dest, source_port, dest_port, buf_rsp, rspDecoded) ) 
                        buf_rsp = b''
            else:
                # is http response ?
                if data.startswith(b'HTTP/'):
                    buf_rsp += data
                    if b'\r\n\r\n' in data:
                        rspDecoded = self.decodeHttpResponse(data = buf_rsp)
                        if rspDecoded is not None:
                            self.responses.append( (source, dest, source_port, dest_port, buf_rsp, rspDecoded) ) 
                            buf_rsp = b''
        self.addLogSuccess(txt="<< Number of HTTP responses extracted: %s " % len(self.responses))

        if self.requests:
            self.addLogSuccess( "<< Read the file finished with success!" )
            self.addLogWarning( "<< Click on the export button to generate the test!" )
            self.exportToAction.setEnabled(True)
        else:
            self.addLogWarning( "<< No http extracted!" )
                
    def readFile(self, fileName):
        """
        Read the file passed as argument
        Old function with dtpkt and python2.7
        """
        self.requests = []
        self.responses = []

        ip_expected = socket.inet_aton( str( self.ipEdit.text() ) )
        port_expected = str( self.portEdit.text() )

        try:
            f = open(fileName, 'rb')
            pcap = dpkt.pcap.Reader(f)
            tot_pkts = len(list(pcap))
        except Exception as e:
            self.addLogError(txt="<< Error to open the network trace")
            self.error( 'unable to open the network trace: %s' % str(e) )
            QMessageBox.critical(self, "Import" , "File not supported")
            return
        else:
            self.addLogSuccess(txt="<< Total packets detected: %s " % tot_pkts)
            self.progressBar.setMaximum(tot_pkts)
            
            # decode http request
            i = 1
            buf_req = ''
            for ts, buf in pcap:
                self.progressBar.setValue(i)
                i += 1

                # read ethernet layer
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type == dpkt.ethernet.ETH_TYPE_IP:
                    # continue with ip decoding layer
                    ip = eth.data
                    if ip.dst == ip_expected:
                        ip_layer = (ip.src, ip.dst)
                        if ip.p == dpkt.ip.IP_PROTO_TCP:
                            tcp = ip.data
                            if tcp.dport == int(port_expected) and len(tcp.data) > 0:
                                tcp_layer = (tcp.sport, tcp.dport)
                                buf_req += tcp.data
                                try:
                                    http_req = dpkt.http.Request(buf_req)
                                except dpkt.dpkt.NeedData as e:
                                    pass
                                except dpkt.UnpackError as e:
                                    pass
                                else:   
                                    self.requests.append( {'ip-src': ip.src, 'ip-dst': ip.dst, 
                                                            'port-src': tcp.sport, 'port-dst': tcp.dport, 
                                                            'tcp-data': buf_req, 'tcp-object': http_req } )
                                    self.addLogWarning(txt="<< %s http request(s) extracted" % len(self.requests) )
                                    buf_req = ''

            # decode http responses
            i = 1
            self.progressBar.setValue(0)
            for ts, buf in pcap:
                self.progressBar.setValue(i)
                i += 1

                # read ethernet layer
                eth = dpkt.ethernet.Ethernet(buf)
                if eth.type == dpkt.ethernet.ETH_TYPE_IP:
                    # continue with ip decoding layer
                    ip = eth.data
                    if ip.src == ip_expected:
                        ip_layer = (ip.src, ip.dst)
                        if ip.p == dpkt.ip.IP_PROTO_TCP:
                            tcp = ip.data
                            if tcp.sport == int(port_expected) and len(tcp.data) > 0:
                                tcp_layer = (tcp.sport, tcp.dport)
                                if (tcp.data).startswith('HTTP/'):
                                    try:
                                        new_res = "%s\r\n\r\n" % (tcp.data).splitlines()[0]
                                        http_res = dpkt.http.Response( new_res )
                                    except dpkt.dpkt.NeedData as e:
                                        pass
                                    except dpkt.UnpackError as e:
                                        pass
                                    else:
                                        self.responses.append( {'ip-src': ip.src, 'ip-dst': ip.dst, 
                                                                'port-src': tcp.sport, 'port-dst': tcp.dport,
                                                                'tcp-data': new_res, 'tcp-object': http_res  } )
                                        self.addLogWarning(txt="<< %s http response(s) extracted" % len(self.responses) )
            if self.requests:
                self.addLogSuccess( "<< File decoded with success!" )
                self.addLogWarning( "<< Click on the export button to generate the test!" )
                self.exportToAction.setEnabled(True)
            else:
                self.addLogWarning( "<< No http extracted!" )