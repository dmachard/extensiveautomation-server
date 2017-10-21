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
Http replay extension for the extensive client
Write test automatically from network trace
"""
import sys
import copy

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
                            QVBoxLayout, QGridLayout, QLabel, QTextEdit, QTextCursor, 
                            QMessageBox, QFileDialog)
    from PyQt4.QtCore import (Qt, QRegExp, QSize)
except ImportError:
    from PyQt5.QtGui import (QIcon, QRegExpValidator, QIntValidator, QTextCursor)
    from PyQt5.QtWidgets import (QMenu, QToolBar, QLineEdit, QSizePolicy, QProgressBar, 
                                QGroupBox, QRadioButton, QHBoxLayout, QVBoxLayout, QGridLayout, 
                                QLabel, QTextEdit, QMessageBox, QFileDialog)
    from PyQt5.QtCore import (Qt, QRegExp, QSize)
    
from Libs import QtHelper, Logger

import UserClientInterface as UCI
import Workspace as WWorkspace
import Settings
import DefaultTemplates

import Libs.Pcap.parse as PcapParse
import Libs.Pcap.pcap as PcapReader
import Libs.Pcap.pcapng as PcapngReader

TU=0
TS=1

WINDOW_TITLE="Capture UDP"

class DUdpReplay(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Http replay dialog
    """
    def __init__(self, parent = None, offlineMode=False):
        """
        Constructor

        @param parent: 
        @type parent:
        """
        super(DUdpReplay, self).__init__(parent)
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
            if not UCI.instance().isAuthenticated():
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
        if not fileName:
        #if fileName.isEmpty():
            return

        if sys.version_info < (3,):
            extension = str(fileName).rsplit(".", 1)[1]
            if not ( extension == "cap" ):
                self.addLogError(txt="<< File not supported %s" % fileName)
                QMessageBox.critical(self, "Open" , "File not supported")
                return

        fileName = str(fileName)
        capName = fileName.rsplit("/", 1)[1]

        self.addLogSuccess(txt=">> Reading the file %s" % fileName)
        self.readFileV2(fileName=fileName)

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
        
    def searchUDP(self):
        """
        Search UDP module in assistant
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
        if not UCI.instance().isAuthenticated():
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

        adps = """self.ADP_UDP = %s.UDP.Client(parent=self, bindIp=input('BIND_IP'), bindPort=input('BIND_PORT'), destinationIp=input('DEST_IP'), destinationPort=input('DEST_PORT'), debug=input('DEBUG'), separatorDisabled=True)""" % self.searchUDP()

        # prepare steps
        steps = []
        j = 0
        for i in xrange(len(self.requests)):
            j = i + 1
            sentrecv, req = self.requests[i]
            if sentrecv == 'sent':
                steps.append( 'self.step%s = self.addStep(expected="udp data sent", description="send udp data", summary="send udp data")' % j )
            else:
                steps.append( 'self.step%s = self.addStep(expected="udp data received", description="received udp data", summary="received udp data")' % j )

        tests = []
        for i in xrange(len(self.requests)):
            j = i + 1
            sentrecv, req = self.requests[i]
            (source, dest, source_port, dest_port, data) = req

            if sentrecv == 'sent':
                tests.append( "# data to sent %s"  % j )
                tests.append( 'self.step%s.start()' % j )
                if sys.version_info > (3,):
                    tests.append( 'rawSent = %s' % data.replace( b"'", b"\\'") )
                else:
                    tests.append( 'rawSent = """%s"""' % data )
                tests.append( 'SentMsg = self.ADP_UDP.sendData(data=rawSent)' ) 
                tests.append( 'if not SentMsg:' ) 
                tests.append( '\tself.step%s.setFailed(actual="unable to send data")' % j) 
                tests.append( 'else:' ) 
                tests.append( '\tself.step%s.setPassed(actual="udp data sent succesfully")' % j ) 
                tests.append( '' ) 
                
            if sentrecv == 'recv':
                tests.append( "# data to received %s"  % j )
                tests.append( 'self.step%s.start()' % j )
                if sys.version_info > (3,):
                    tests.append( 'rawRecv = %s' % data.replace( b'"', b'\\"') )
                else:
                    tests.append( 'rawRecv = """%s"""' % data )
                tests.append( 'RecvMsg = self.ADP_UDP.hasReceivedData(data=rawRecv, timeout=input("TIMEOUT"))' ) 
                tests.append( 'if RecvMsg is None:' ) 
                tests.append( '\tself.step%s.setFailed(actual="unable to received data")' % j) 
                tests.append( 'else:' ) 
                tests.append( '\tself.step%s.setPassed(actual="udp data received succesfully")' % j ) 
                tests.append( '' ) 
        if TS:
            init = """self.ADP_UDP.startListening()
		udpListening = self.ADP_UDP.isListening( timeout=input('TIMEOUT') )
		if not udpListening:
			self.abort( 'unable to listing to the udp port %s'  )
""" % str(self.portEdit.text())

        if TU:
            init = """self.ADP_UDP.startListening()
	udpListening = self.ADP_UDP.isListening( timeout=input('TIMEOUT') )
	if not udpListening:
		self.abort( 'unable to connect to the udp port %s'  )
""" % str(self.portEdit.text())

        if TS:  
            cleanup = """self.ADP_UDP.stopListening()
		udpStopped = self.ADP_UDP.isStopped( timeout=input('TIMEOUT') )
		if not udpStopped:
			self.error( 'unable to no more listen from the udp port %s' )
""" % str(self.portEdit.text())

        if TU:
            cleanup = """self.ADP_UDP.stopListening()
	udpStopped = self.ADP_UDP.isStopped( timeout=input('TIMEOUT') )
	if not udpStopped:
		self.error( 'unable to no more listen  from the udp port %s' )
""" % str(self.portEdit.text())

        self.newTest = self.newTest.replace( "<<PURPOSE>>", 'self.setPurpose(purpose="Replay UDP")' )
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
            self.error( 'unable to open the network trace: %s' % str(e) )
            QMessageBox.critical(self, "Import" , "File not supported")
        
    def readFilePacket(self, pcapFile):
        """
        Read file packet by packet
        """
        ip_expected = str( self.ipEdit.text() )
        port_expected = int( self.portEdit.text() )

        # read packet)
        packets = pcapFile()
        ethernetPackets = list(packets)
        self.addLogSuccess(txt="<< Total packets detected: %s " % len(ethernetPackets))

        # extract udp packet according to the expected ip and port
        self.requests = []
        i = 1
        self.progressBar.setMaximum(len(ethernetPackets))
        self.progressBar.setValue(0)
        for pkt in ethernetPackets:
            self.progressBar.setValue(i)
            i += 1
            pktDecoded = PcapParse.decodePacket(pkt, getTcp=False, getUdp=True)
            if pktDecoded is not None:
                (source, dest, source_port, dest_port, data) = pktDecoded
                # skip when no data exists
                if dest == ip_expected and int(dest_port) == int(port_expected) and len(data) > 0 :
                    self.requests.append( ('sent', pktDecoded) )
                if source == ip_expected and int(source_port) == int(port_expected) and len(data) > 0:
                    self.requests.append( ( 'recv', pktDecoded) )
        self.addLogSuccess(txt="<< Number of UDP packets detected: %s" % len(self.requests))

        if self.requests:
            self.addLogSuccess( "<< File decoded with success!" )
            self.addLogWarning( "<< Click on the export button to generate the test!" )
            self.exportToAction.setEnabled(True)
        else:
            self.addLogWarning( "<< No udp extracted!" )