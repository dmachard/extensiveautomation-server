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
Detailed view module
"""
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    long = int
    
try:
    from PyQt4.QtGui import (QTextEdit, QDialogButtonBox, QVBoxLayout, QTreeWidgetItem, 
                            QColor, QTreeWidget, QTreeView, QWidget, QLabel, QFont, QDialog, 
                            QIcon, QToolBar, QPalette, QSizePolicy, QScrollArea, QPixmap, 
                            QFileDialog, QImage, QHBoxLayout, QSplitter, QTabWidget, QTableWidget, 
                            QAbstractItemView, QApplication, QMenu)
    from PyQt4.QtCore import (Qt, pyqtSignal, QSize)
    if sys.version_info < (3,):
        from PyQt4.QtCore import (QString)
except ImportError:
    from PyQt5.QtGui import (QColor, QFont, QIcon, QPalette, QPixmap, QImage)
    from PyQt5.QtWidgets import (QTextEdit, QDialogButtonBox, QVBoxLayout, QTreeWidgetItem, 
                                QTreeWidget, QTreeView, QWidget, QLabel, QDialog, QToolBar, 
                                QSizePolicy, QScrollArea, QFileDialog, QHBoxLayout, QSplitter, 
                                QTabWidget, QTableWidget, QAbstractItemView, QApplication, QMenu)
    from PyQt5.QtCore import (Qt, pyqtSignal, QSize)
    
from Libs import QtHelper, Logger
import Settings


try:
    xrange
except NameError: # support python3
    xrange = range
    
import base64
import copy

TYPE_DATA_PAYLOAD_V1            = '%payload-v1%'
TYPE_DATA_TIMER                 = 'timer'
TYPE_DATA_STEP                  = 'step'
TYPE_DATA_MATCH                 = 'match'
TYPE_DATA_MATCH_RECEIVED        = 'match-received'

#Char  Dec  Oct  Hex   WhatAreThey
#---------------------------------------
#(nul)   0 0000 0x00   Null 
#(ht)    9 0011 0x09   Horizontal Tab
#(nl)   10 0012 0x0a   New Line
#(vt)   11 0013 0x0b   Vertical Tab
#(cr)   13 0015 0x0d   Carriage Return
#(sp)   32 0040 0x20   Space
#0      48 0060 0x30   zero
#A      65 0101 0x41   capital A
#a      97 0141 0x61   lowercase a

#ascii codes and their escape sequences
#ASCII Name   Description     C Escape Sequence
#----------------------------------------------
#nul          null byte       \0 (zero)
#bel          bel character   \a
#bs           backspace       \b
#ht           horizontal tab  \t
#np           formfeed        \f
#nl           newline         \n
#cr           carriage return \r

#ascii table
#Char  Dec  Oct  Hex | Char  Dec  Oct  Hex | Char  Dec  Oct  Hex | Char Dec  Oct   Hex
#-------------------------------------------------------------------------------------
#(nul)   0 0000 0x00 | (sp)   32 0040 0x20 | @      64 0100 0x40 | `      96 0140 0x60
#(soh)   1 0001 0x01 | !      33 0041 0x21 | A      65 0101 0x41 | a      97 0141 0x61
#(stx)   2 0002 0x02 | "      34 0042 0x22 | B      66 0102 0x42 | b      98 0142 0x62
#(etx)   3 0003 0x03 | #      35 0043 0x23 | C      67 0103 0x43 | c      99 0143 0x63
#(eot)   4 0004 0x04 | $      36 0044 0x24 | D      68 0104 0x44 | d     100 0144 0x64
#(enq)   5 0005 0x05 | %      37 0045 0x25 | E      69 0105 0x45 | e     101 0145 0x65
#(ack)   6 0006 0x06 | &      38 0046 0x26 | F      70 0106 0x46 | f     102 0146 0x66
#(bel)   7 0007 0x07 | '      39 0047 0x27 | G      71 0107 0x47 | g     103 0147 0x67
#(bs)    8 0010 0x08 | (      40 0050 0x28 | H      72 0110 0x48 | h     104 0150 0x68
#(ht)    9 0011 0x09 | )      41 0051 0x29 | I      73 0111 0x49 | i     105 0151 0x69
#(nl)   10 0012 0x0a | *      42 0052 0x2a | J      74 0112 0x4a | j     106 0152 0x6a
#(vt)   11 0013 0x0b | +      43 0053 0x2b | K      75 0113 0x4b | k     107 0153 0x6b
#(np)   12 0014 0x0c | ,      44 0054 0x2c | L      76 0114 0x4c | l     108 0154 0x6c
#(cr)   13 0015 0x0d | -      45 0055 0x2d | M      77 0115 0x4d | m     109 0155 0x6d
#(so)   14 0016 0x0e | .      46 0056 0x2e | N      78 0116 0x4e | n     110 0156 0x6e
#(si)   15 0017 0x0f | /      47 0057 0x2f | O      79 0117 0x4f | o     111 0157 0x6f
#(dle)  16 0020 0x10 | 0      48 0060 0x30 | P      80 0120 0x50 | p     112 0160 0x70
#(dc1)  17 0021 0x11 | 1      49 0061 0x31 | Q      81 0121 0x51 | q     113 0161 0x71
#(dc2)  18 0022 0x12 | 2      50 0062 0x32 | R      82 0122 0x52 | r     114 0162 0x72
#(dc3)  19 0023 0x13 | 3      51 0063 0x33 | S      83 0123 0x53 | s     115 0163 0x73
#(dc4)  20 0024 0x14 | 4      52 0064 0x34 | T      84 0124 0x54 | t     116 0164 0x74
#(nak)  21 0025 0x15 | 5      53 0065 0x35 | U      85 0125 0x55 | u     117 0165 0x75
#(syn)  22 0026 0x16 | 6      54 0066 0x36 | V      86 0126 0x56 | v     118 0166 0x76
#(etb)  23 0027 0x17 | 7      55 0067 0x37 | W      87 0127 0x57 | w     119 0167 0x77
#(can)  24 0030 0x18 | 8      56 0070 0x38 | X      88 0130 0x58 | x     120 0170 0x78
#(em)   25 0031 0x19 | 9      57 0071 0x39 | Y      89 0131 0x59 | y     121 0171 0x79
#(sub)  26 0032 0x1a | :      58 0072 0x3a | Z      90 0132 0x5a | z     122 0172 0x7a
#(esc)  27 0033 0x1b | ;      59 0073 0x3b | [      91 0133 0x5b | {     123 0173 0x7b
#(fs)   28 0034 0x1c | <      60 0074 0x3c | \      92 0134 0x5c | |     124 0174 0x7c
#(gs)   29 0035 0x1d | =      61 0075 0x3d | ]      93 0135 0x5d | }     125 0175 0x7d
#(rs)   30 0036 0x1e | >      62 0076 0x3e | ^      94 0136 0x5e | ~     126 0176 0x7e
#(us)   31 0037 0x1f | ?      63 0077 0x3f | _      95 0137 0x5f | (del) 127 0177 0x7f

def removeNonPrintableCharacter( datas):
    """
    Remove non printable character for ascii
    """
    hx_str = []
    for c in datas:
        if ( ord(c) >= 32 and ord(c) <= 126) or ord(c) in [10, 13] :
            hx_str.append( c )
        else:
            hx_str.append( ' ' )
    return ''.join(hx_str)

class DescriptionDialog(QtHelper.EnhancedQDialog, Logger.ClassLogger):
    """
    Description dialog
    """
    def __init__(self, dataDescr, parent=None):
        """
        Dialog to fill parameter description

        @param dataArgs: 
        @type dataArgs: 

        @param parent: 
        @type parent:
        """
        super(DescriptionDialog, self).__init__(parent)
        self.dataDescr = dataDescr
        self.createDialog()
        self.createConnections()

    def createDialog (self):
        """
        Create qt dialog
        """
        self.descrEdit = QTextEdit()
        self.descrEdit.setPlainText(self.dataDescr)
        self.descrEdit.setReadOnly(True)

        self.buttonBox = QDialogButtonBox(self)
        self.buttonBox.setStyleSheet( """QDialogButtonBox { 
            dialogbuttonbox-buttons-have-icons: 1;
            dialog-ok-icon: url(:/ok.png);
            dialog-cancel-icon: url(:/ko.png);
        }""")
        self.buttonBox.setStandardButtons(QDialogButtonBox.Ok)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.descrEdit)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Test Result > Value")
        self.resize(650, 450)
        self.center()

    def createConnections (self):
        """
        Create qt connections
        """
        self.buttonBox.accepted.connect(self.accept)

INDEX_COL_KEY   = 0
INDEX_COL_VALUE = 1

class KeyItem(QTreeWidgetItem):
    """
    Key item
    """
    def __init__(self, key, colorKey, value = None, valueRaw=None, parent = None, colorValue = None, noLimit=False ):
        """
        Constructs KeyItem widget item

        @param key:
        @type key: 

        @param colorKey:
        @type colorKey: 

        @param value:
        @type value: 

        @param parent:
        @type parent: 

        @param colorValue:
        @type colorValue: 

        @param noLimit:
        @type noLimit: 
        """
        QTreeWidgetItem.__init__(self, parent)
        #
        self.__data__ = None
        self.dataraw = valueRaw
        self.color = colorKey

        # set key
        self.setText(INDEX_COL_KEY, key)
        self.setToolTip(INDEX_COL_KEY, key)
        self.setColor( col = INDEX_COL_KEY, color = colorKey )

        # set value
        if value is not None: 
            if isinstance(value, list):
                value = str(value)
            if sys.version_info > (3,): # python3 support 
                if isinstance(value, bytes):
                    self.setToolTip(INDEX_COL_VALUE, "binary data..." )
                else:
                    self.setToolTip(INDEX_COL_VALUE, str(value) )
            else:
                self.setToolTip(INDEX_COL_VALUE, QString(value) )
            limit = 50
            if noLimit:
                self.setText(INDEX_COL_VALUE, value)
            else:
                if isinstance(value, int) or isinstance(value, long):
                    value = str(value)
                try:
                    if sys.version_info > (3,): # python3 support
                        if isinstance(value,  bytes):
                            lines = str(value, 'utf8', errors="ignore") .splitlines()
                        else:
                            lines = value.splitlines()
                    else:        
                        lines = value.splitlines()
                        
                    # for display only
                    if len(lines) > 1:
                        if len(lines[0])> limit:
                            self.setText(1, "%s [...]" % lines[0][:limit])
                        else:
                            self.setText(1, "%s [...]" % lines[0])
                    else:
                        if len(lines) == 1:
                            if len(lines[0])> limit:
                                self.setText(INDEX_COL_VALUE, "%s [...]" % lines[0][:limit])
                            else:
                                if sys.version_info > (3,): # python3 support
                                    self.setText(INDEX_COL_VALUE, lines[0] )
                                else:
                                    try:
                                        self.setText(INDEX_COL_VALUE, lines[0].decode('utf8') )
                                    except UnicodeDecodeError as e:
                                        self.setText(INDEX_COL_VALUE, lines[0] )
                        else:
                            self.setText(INDEX_COL_VALUE, "")
                            
                except Exception as e:
                    self.setText(1, "[TEMPLATE MALFORMED (%s)]: %s" % ( type(value), "%s" % value ) )
                    self.setColor( col = INDEX_COL_VALUE, color = "r" )
                    print("template malformed: %s - %s - %s " % (e, type(value), "%s" % value ) )
                    value = ''
                    
            # save internal data       
            self.__data__ = value
        if colorValue is not None: self.setColor( col = INDEX_COL_VALUE, color = colorValue )

    def setColor (self, col, color):
        """
        Set color

        @param col:
        @type col: 

        @param color:
        @type color: 
        """
        if color == "b":
            # self.setTextColor(col, QColor(Qt.black) )
            self.setForeground(col, QColor(Qt.black) )
        elif color == "r":
            # self.setTextColor(col, QColor(Qt.white) )
            self.setForeground(col, QColor(Qt.white) )
            self.setBackgroundColor(col, QColor(Qt.red) )
            if col == INDEX_COL_KEY:
                self.setToolTip(INDEX_COL_KEY, 'mismatched')
            if col == INDEX_COL_VALUE:
                self.setToolTip(INDEX_COL_VALUE, 'mismatched')
        elif color == "g":
            # self.setTextColor(col, QColor(Qt.white) )
            self.setForeground(col, QColor(Qt.white) )
            self.setBackgroundColor(col, QColor(Qt.darkGreen) )
            if col == INDEX_COL_KEY:
                self.setToolTip(INDEX_COL_KEY, 'matched')
            if col == INDEX_COL_VALUE:
                self.setToolTip(INDEX_COL_VALUE, 'matched')
        elif color == "bl":
            # self.setTextColor(col, QColor(Qt.blue) )
            self.setForeground(col, QColor(Qt.blue) )
        elif color == "y":
            # self.setTextColor(col, QColor(Qt.black) )
            self.setForeground(col, QColor(Qt.black) )
            self.setBackgroundColor(col, QColor(Qt.yellow) )
            if col == INDEX_COL_KEY:
                self.setToolTip(INDEX_COL_KEY, 'ignored')
            if col == INDEX_COL_VALUE:
                self.setToolTip(INDEX_COL_VALUE, 'ignored')
    
    def getTextKey(self):
        """
        Returns the text of the key
        """
        return self.text(INDEX_COL_KEY)

    def getTextValue(self):
        """
        Returns the text of the value
        """
        if sys.version_info > (3,): # python3 support
            if isinstance(self.__data__, bytes):
                return 'binary data...'
            else:
                return self.__data__
        else:
            return self.__data__
            
class DeselectableTreeWidget(QTreeWidget):
    """
    Deselectable tree widget
    """
    def mousePressEvent(self, event):
        """
        On mouse press
        """
        self.clearSelection()
        QTreeView.mousePressEvent(self, event)

class QTreeWidgetTemplate(QWidget):
    """
    Tree widget template
    """
    TemplateExpanded = pyqtSignal(list)
    TemplateCollapsed = pyqtSignal(list) 
    TemplateClicked = pyqtSignal(list) 
    def __init__ (self, parent, signals=False, textHexa=None, textRaw=None, imgRaw=None, withLabel=True, 
                        signalsExpanded=False, signalsReadMore=False, signalsAutoSelect=False, xmlRaw=None, htmlRaw=None):
        """
        Qtree widget template

        @param parent:
        @type parent: 

        @param signals:
        @type signals: 

        @param textHexa:
        @type textHexa: 

        @param textRaw:
        @type textRaw: 
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        self.withLabel = withLabel
        self.textHexa = None
        self.textRaw = None
        self.imgRaw = None
        self.xmlRaw = None
        self.htmlRaw=None
        self.createWidgets()
        if signals:
            self.createConnections()
            self.textHexa = textHexa
            self.textRaw = textRaw
            self.imgRaw = imgRaw
            self.xmlRaw = xmlRaw
            self.htmlRaw = htmlRaw
        if signalsExpanded:
            self.createConnectionsTemplates()
        if signalsReadMore:
            self.createConnectionsReadMore()
        if signalsAutoSelect:
            self.createConnectionsAutoSelect()

        
    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()
        self.frameLabel = QLabel()
        if self.withLabel:
            layout.addWidget( self.frameLabel )

        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(False)

        self.labels = []
        self.setBasicLabels()
        self.tree.setColumnWidth(0, 200) # Key.


        layout.addWidget( self.tree )   
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def setStatusLabels(self):
        """
        Set the status labels
        """
        self.labels = [ self.tr("Status Key") , self.tr("Status Value") ]   
        self.tree.setHeaderLabels(self.labels)
        self.tree.setColumnWidth(1, 200)

    def setBasicLabels(self):
        """
        Set basic labels
        """
        self.labels = [  self.tr("Key") , self.tr("Value") ]
        self.tree.setHeaderLabels(self.labels)

    def setLabel (self, txt, bold = True):
        """
        Set label

        @param txt:
        @type txt: 

        @param bold:
        @type bold: boolean
        """
        self.frameLabel.setText(txt)
        font = QFont()    
        font.setBold(True)
        self.frameLabel.setFont( font )
        
    def clear (self):
        """
        Clear
        """
        self.tree.clear()
        self.frameLabel.setText('')

    def createConnectionsAutoSelect (self):
        """
        QtSignals connection
        """
        self.tree.itemClicked.connect(self.itemClickedAutoSelect)

    def createConnections (self):
        """
        QtSignals connection
        """
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)

    def createConnectionsTemplates (self):
        """
        QtSignals connection
        """
        self.tree.itemExpanded.connect(self.itemExpanded)
        self.tree.itemCollapsed.connect(self.itemCollapsed)

    def createConnectionsReadMore (self):
        """
        QtSignals connection
        """
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)

    def itemExpanded(self, itm):
        """
        On item expanded
        """        
        listKeys = [ itm.text(0) ]
        itmtmp = itm
        while self.tree.indexOfTopLevelItem (itmtmp) == - 1:
            itmParent = self.tree.itemAbove(itmtmp)
            listKeys.append( itmParent.text(0) )
            itmtmp = itmParent
        # emit the signal
        self.TemplateExpanded.emit(listKeys)
    
    def itemCollapsed(self, itm):
        """
        On item collapsed
        """
        listKeys = [ itm.text(0) ]
        itmtmp = itm
        while self.tree.indexOfTopLevelItem (itmtmp) == - 1:
            itmParent = self.tree.itemAbove(itmtmp)
            listKeys.append( itmParent.text(0) )
            itmtmp = itmParent
        # emit the signal
        self.TemplateCollapsed.emit(listKeys)

    def itemDoubleClicked(self, itm):
        """
        On item double clicked
        """
        if itm.__data__ is not None or itm.dataraw is not None:
            if  itm.__data__ is not None:
                dataRaw = itm.__data__
            if itm.dataraw is not None:
                dataRaw = itm.dataraw

            # update raw view
            if sys.version_info > (3,): # python3 support
                if isinstance(dataRaw,  bytes):
                    dataDecoded = str(dataRaw, 'utf8', errors="ignore")
                else:
                    dataDecoded = dataRaw
            else:
                try:
                    dataDecoded = dataRaw.decode('utf8')
                except Exception as e:
                    dataDecoded = dataRaw
            
            if isinstance(dataDecoded, tuple):
                self.parent.getParent().error( 'detailed view, item clicked: %s' % str(dataDecoded) )
            else:
                if sys.version_info > (3,):
                    data = dataDecoded
                else:
                    data = removeNonPrintableCharacter(datas=dataDecoded)
                editorDialog = DescriptionDialog(data)
                if editorDialog.exec_() == QDialog.Accepted:
                    pass

    def itemClickedAutoSelect(self, itm):
        """
        On item clicked for auto select
        """
        listKeys = [ itm.text(0) ]
        itmtmp = itm.parent()
        while itmtmp is not None:
            listKeys.append( itmtmp.text(0) )
            itmtmp = itmtmp.parent()
        # emit the signal
        self.TemplateClicked.emit(listKeys)

    def itemClicked(self, itm):
        """
        On item clicked

        @param itm:
        @type itm: 
        """
        if itm.__data__ is not None or itm.dataraw is not None:
            if  itm.__data__ is not None:
                dataRaw = itm.__data__
            if itm.dataraw is not None:
                dataRaw = itm.dataraw

            # update img view
            if self.imgRaw is not None:
                if sys.version_info > (3,): # python3 support
                    try:
                        self.imgRaw.setImage(content=dataRaw)
                    except UnicodeEncodeError as e:
                        pass
                else:
                    self.imgRaw.setImage(content=dataRaw)
                    
            # update raw view
            if sys.version_info > (3,): # python3 support
                if isinstance(dataRaw,  bytes):
                    dataDecoded = str(dataRaw, 'utf8', errors="ignore")
                else:
                    dataDecoded = dataRaw
            else:
                try:
                    dataDecoded = dataRaw.decode('utf8')
                except Exception as e:
                    dataDecoded = dataRaw
            
            if isinstance(dataDecoded, tuple):
                self.parent.getParent().error( 'detailed view, item clicked: %s' % str(dataDecoded) )
            else:
                if sys.version_info > (3,):
                    rawTxt = dataDecoded
                else:
                    rawTxt = removeNonPrintableCharacter(datas=dataDecoded)
                self.textRaw.setPlainText( rawTxt )  
                if self.htmlRaw is not None:
                    self.htmlRaw.setHtml( rawTxt )    
                # update xml view
                if self.xmlRaw is not None:
                    xmlTxt = rawTxt.replace('><', '>\r\n<')
                    self.xmlRaw.setText(xmlTxt)

            
            if self.textHexa is not None:
                # update hex view
                hexas = ["%02X" % (ord(ch),) for ch in dataDecoded ]
                self.textHexa.setPlainText( ' '.join(hexas) )

class ImageView(QWidget):
    """
    Image view
    """
    def __init__(self, parent):
        """
        The image view
        """
        QWidget.__init__(self, parent)
        self.scaleFactor = 0.0
        self.createWidgets()
        self.createActions()
        self.createToolbar()

    def createToolbar(self):
        """
        Toolbar creation
            
        ||------|------|||
        || Open | Save |||
        ||------|------|||
        """
        self.dockToolbar.setObjectName("Test Config toolbar")
        self.dockToolbar.addAction(self.zoomInAct)
        self.dockToolbar.addAction(self.zoomOutAct)
        self.dockToolbar.addAction(self.normalSizeAct)
        self.dockToolbar.addSeparator()
        self.dockToolbar.addAction(self.saveImageAct)
        self.dockToolbar.addSeparator()
        self.dockToolbar.setIconSize(QSize(16, 16))

    def createActions(self):
        """
        Create qc actions
        """
        self.zoomInAct = QtHelper.createAction(self, "&Zoom &In (25%.", self.zoomIn, 
                                        icon=QIcon(":/zoom-in.png") ) 
        self.zoomOutAct = QtHelper.createAction(self, "Zoom &Out (25%.", self.zoomOut, 
                                        icon=QIcon(":/zoom-out.png") ) 
        self.normalSizeAct = QtHelper.createAction(self, "&Normal Size", self.normalSize, 
                                        icon=QIcon(":/zoom-normal.png") ) 
        self.saveImageAct = QtHelper.createAction(self, "&Save", self.saveImage, 
                                        icon=QIcon(":/filesave.png") ) 

    def createWidgets(self):
        """
        Create qt widgets
        """
        self.dockToolbar = QToolBar(self)
        self.dockToolbar.setStyleSheet("QToolBar { border: 0px }") # remove 3D border

        self.imageLabel = QLabel(self)
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)

        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.scrollArea.setWidget(self.imageLabel)

        layout = QVBoxLayout()
        layout.addWidget(self.dockToolbar)
        layout.addWidget(self.scrollArea)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def saveImage(self):
        """
        Save image
        """
        graphPixmap = QPixmap.grabWidget(self.imageLabel)
        format = 'png'
        fileName = QFileDialog.getSaveFileName(self, self.tr("Save As"), "", "%s Files (*.%s);;All Files (*)" % (format.upper(), format))
        if fileName:
            graphPixmap.save(fileName, format)

    def resetView(self):
        """
        Reset the view
        """
        self.imageLabel.setText('')
        self.imageLabel.hide()

    def setEnabled(self, state):
        """
        Set enabled
        """
        self.scrollArea.setEnabled(state)
        self.dockToolbar.setEnabled(state)

    def setImage(self, content):
        """
        Set the image
        """
        image = QImage()
        ret = image.loadFromData(content)
        if image.isNull():
            self.imageLabel.setText('unable to load image')
            self.setEnabled(False)
            self.imageLabel.show()
            self.imageLabel.adjustSize()
        else:
            self.setEnabled(True)
            self.imageLabel.setText('')
            self.imageLabel.show()
            self.imageLabel.setPixmap(QPixmap.fromImage(QImage(image)))
            self.scaleFactor = 1.0
            self.imageLabel.adjustSize()

    def zoomIn(self):
        """
        Zoom in
        """
        self.scaleImage(1.25)

    def zoomOut(self):
        """
        Zoom out
        """
        self.scaleImage(0.8)

    def normalSize(self):
        """
        Normal size
        """
        self.imageLabel.adjustSize()
        self.scaleFactor = 1.0

    def adjustScrollBar(self, scrollBar, factor):
        """
        Adjust the scrollbar
        """
        scrollBar.setValue(int(factor * scrollBar.value()  + ((factor - 1) * scrollBar.pageStep()/2)))

    def scaleImage(self, factor):
        """
        Scale the image
        """
        self.scaleFactor *= factor
        if self.imageLabel.pixmap() is not None:
            self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

class RawView(QWidget):
    """
    Raw view
    """
    def __init__(self, parent):
        """
        The raw view
        """
        QWidget.__init__(self, parent)
        self.createWidgets()

    def createWidgets(self):
        """
        Create qt widgets
        """
        layout = QVBoxLayout()
        self.rawEdit = QtHelper.RawEditor(parent=self)
        self.rawEdit.setReadOnly(True)
        self.rawFind = QtHelper.RawFind(parent=self, editor=self.rawEdit)
        layout.addWidget(self.rawEdit)  
        layout.addWidget(self.rawFind)  
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)
    
    def resetView(self):
        """
        Reset the view
        """
        self.setPlainText("")
        self.rawFind.resetLine()

    def setEnabled(self, state):
        """
        Set enabled
        """
        self.rawEdit.setEnabled(state)
        self.rawFind.setEnabled(state)

    def setPlainText(self, txt):
        """
        Set plain text
        """
        if sys.version_info > (3,): # python3 support
            if isinstance(txt, bytes): txt = str(txt, 'utf8', errors="ignore")
            
        self.rawEdit.setPlainText(txt)

    def setHtml(self, html):
        """
        Set html
        """
        if sys.version_info > (3,): # python3 support
            if isinstance(html, bytes): html = str(html, 'utf8', errors="ignore")
            
        html2 = html.replace('\n', '<br />') # for backward compatibility
        self.rawEdit.setHtml(html2)

    def setReadOnly(self, readonly):
        """
        Set the text as readonly
        """
        self.rawEdit.setReadOnly(readonly)

class TreeMemory(object):
    def __init__(self, treeWidget):
        """
        """
        self.treeWidget = treeWidget
        self.treeIndexes = []
        
    def restore(self):
        """
        Expand auto
        """
        for  v in self.treeIndexes:
            i, subIdx = v
            itm = self.treeWidget.tree.topLevelItem( i)
            if itm is not None:
                itm.setExpanded(True)
                if len(subIdx):
                    self.__restore(itm=itm, indexes=subIdx)

    def __restore(self, itm, indexes):
        """
        Sub function of expand auto
        """
        for j in indexes:
            i, subIdx = j
            child = itm.child(i)
            if child is not None:
                child.setExpanded(True)
                if len(subIdx):
                    self.__restore(itm=child,indexes=subIdx)
    
    def snapshot(self):
        """
        """
        self.treeIndexes = []
        for i in xrange( self.treeWidget.tree.topLevelItemCount() ):
            itm = self.treeWidget.tree.topLevelItem( i )
            if itm.isExpanded():
            # if self.treeWidget.tree.isItemExpanded( itm ):
                subRet = self.__snapshot(itm)
                self.treeIndexes.append( (i,subRet) )

    def __snapshot(self, itm):
        """
        Sub function of on item event expanded or collapsed
        """
        subRet = []
        for j in xrange(itm.childCount()):
            child = itm.child(j)
            if child.isExpanded():
                if child.childCount():
                    subRet.append( (j, self.__snapshot(itm=child) ) )
                else:
                    subRet.append( (j,[]) )
        return subRet
        
class DetailedView(QWidget):
    """
    Detailed view
    """
    def __init__(self, parent = None):
        """
        The detailed view

        @param parent:
        @type parent: 
        """
        QWidget.__init__(self, parent)
        self.parent = parent
        # self.treeIndexes = []
        self.treeIndexesSelected = []

        self.createActions()
        self.createWidgets()
        
        self.TemplateTreeMemory = TreeMemory(treeWidget=self.treeWidgetLeft)  
        self.EventTreeMemory = TreeMemory(treeWidget=self.treeWidgetLeft2)
        
        self.createConnections()

    def getParent(self):
        """
        Return the parent
        """
        return self.parent

    def createActions(self):
        """
        Create qt actions
        """
        # left 2
        self.expandSubtreeAction = QtHelper.createAction(self, "&Expand subtree...", self.expandSubtreeIteem, 
                                    icon = None, tip = 'Expand subtree' )
        self.expandAllAction = QtHelper.createAction(self, "&Expand All", self.expandAllItems, 
                                    icon = None, tip = 'Expand all items' )
        self.collapseAllAction = QtHelper.createAction(self, "&Collapse All", self.collapseAllItems, 
                                    icon = None, tip = 'Collapse all items' )

        self.copyKeyAction = QtHelper.createAction(self, "&Copy key...", self.copyKeyIteem, 
                                    icon = None, tip = 'Copy key' )
        self.copyValueAction = QtHelper.createAction(self, "&Copy value...", self.copyValueIteem, 
                                    icon = None, tip = 'Copy value' )

        # left
        self.expandSubtreeActionLeft = QtHelper.createAction(self, "&Expand subtree...", self.expandSubtreeItemLeft, 
                                    icon = None, tip = 'Expand subtree' )
        self.expandAllActionLeft = QtHelper.createAction(self, "&Expand All", self.expandAllItemsLeft, 
                                    icon = None, tip = 'Expand all items' )
        self.collapseAllActionLeft = QtHelper.createAction(self, "&Collapse All", self.collapseAllItemsLeft, 
                                    icon = None, tip = 'Collapse all items' )

        self.copyKeyActionLeft = QtHelper.createAction(self, "&Copy key...", self.copyKeyItemLeft, 
                                    icon = None, tip = 'Copy key' )
        self.copyValueActionLeft = QtHelper.createAction(self, "&Copy value...", self.copyValueItemLeft, 
                                    icon = None, tip = 'Copy value' )

        # left 3
        self.expandSubtreeActionLeft3 = QtHelper.createAction(self, "&Expand subtree...", self.expandSubtreeItemLeft3, 
                                    icon = None, tip = 'Expand subtree' )
        self.expandAllActionLeft3 = QtHelper.createAction(self, "&Expand All", self.expandAllItemsLeft3, 
                                    icon = None, tip = 'Expand all items' )
        self.collapseAllActionLeft3 = QtHelper.createAction(self, "&Collapse All", self.collapseAllItemsLeft3, 
                                    icon = None, tip = 'Collapse all items' )

        self.copyKeyActionLeft3 = QtHelper.createAction(self, "&Copy key...", self.copyKeyItemLeft3, 
                                    icon = None, tip = 'Copy key' )
        self.copyValueActionLeft3 = QtHelper.createAction(self, "&Copy value...", self.copyValueItemLeft3, 
                                    icon = None, tip = 'Copy value' )

        # right = template right expected
        self.expandSubtreeActionRight = QtHelper.createAction(self, "&Expand subtree...", self.expandSubtreeItemRight, 
                                    icon = None, tip = 'Expand subtree' )
        self.expandAllActionRight = QtHelper.createAction(self, "&Expand All", self.expandAllItemsRight, 
                                    icon = None, tip = 'Expand all items' )
        self.collapseAllActionRight  = QtHelper.createAction(self, "&Collapse All", self.collapseAllItemsRight, 
                                    icon = None, tip = 'Collapse all items' )

        self.copyKeyActionRight = QtHelper.createAction(self, "&Copy key...", self.copyKeyItemRight, 
                                    icon = None, tip = 'Copy key' )
        self.copyValueActionRight = QtHelper.createAction(self, "&Copy value...", self.copyValueItemRight, 
                                    icon = None, tip = 'Copy value' )

        self.displayValueLeftAction = QtHelper.createAction(self, "&Display value...", self.displayTreeValueLeft, 
                                    icon = None, tip = 'Display value' )
        self.displayValueLeft2Action = QtHelper.createAction(self, "&Display value...", self.displayTreeValueLeft2, 
                                    icon = None, tip = 'Display value' )
        self.displayValueLeft3Action = QtHelper.createAction(self, "&Display value...", self.displayTreeValueLeft3, 
                                    icon = None, tip = 'Display value' )

    def createConnections (self):
        """
        QtSignals connection
         * self.logs <=> loadTest
        """
        self.treeWidgetLeft2.tree.customContextMenuRequested.connect(self.onPopupMenu)
        self.treeWidgetLeft.tree.customContextMenuRequested.connect(self.onPopupMenuLeft)
        self.treeWidgetLeft3.tree.customContextMenuRequested.connect(self.onPopupMenuLeft3)
        self.treeWidgetRight.tree.customContextMenuRequested.connect(self.onPopupMenuRight)
        
        self.treeWidgetRight.TemplateExpanded.connect(self.onTemplateExpanded)
        self.treeWidgetRight.TemplateCollapsed.connect(self.onTemplateCollapsed)
        self.treeWidgetRight.TemplateClicked.connect(self.onTemplateClicked)
        
        self.treeWidgetLeft2.tree.itemExpanded.connect(self.EventTreeMemory.snapshot)
        self.treeWidgetLeft2.tree.itemCollapsed.connect(self.EventTreeMemory.snapshot)
        self.treeWidgetLeft.tree.itemExpanded.connect(self.TemplateTreeMemory.snapshot)
        self.treeWidgetLeft.tree.itemCollapsed.connect(self.TemplateTreeMemory.snapshot)
        # self.treeWidgetLeft2.tree.itemSelectionChanged.connect(self.itemEventSelected)
        
    def displayTreeValueLeft(self):
        """
        Display the tree value of the left
        """
        currentItem = self.treeWidgetLeft.tree.currentItem()
        self.treeWidgetLeft.itemDoubleClicked(itm=currentItem)

    def displayTreeValueLeft2(self):
        """
        Display the tree value of the left
        """
        currentItem = self.treeWidgetLeft2.tree.currentItem()
        self.treeWidgetLeft2.itemDoubleClicked(itm=currentItem)

    def displayTreeValueLeft3(self):
        """
        Display the tree value of the left
        """
        currentItem = self.treeWidgetLeft3.tree.currentItem()
        self.treeWidgetLeft3.itemDoubleClicked(itm=currentItem)

    # def itemEventSelected(self):
        # """
        # On item event expanded or collapsed
        # """
        # itms = self.treeWidgetLeft2.tree.selectedItems()
        # if not len(itms):
            # return
            
        # itm = itms[0]
        
        
        # self.treeIndexesSelected = []
        
        # index = self.treeWidgetLeft2.tree.indexFromItem(itm)
        # self.treeIndexesSelected.append(index.row())

        # p = itm.parent()
        # while p is not None:
            # indexParent = self.treeWidgetLeft2.tree.indexFromItem(p)
            # self.treeIndexesSelected.append(indexParent.row())
            # p = p.parent()

    def onTemplateClicked(self, indexes):
        """
        On template clicked
        """
        itmFound = None
        searchKey = indexes.pop()

        for i in xrange( self.treeWidgetLeft.tree.topLevelItemCount() ):
            itm = self.treeWidgetLeft.tree.topLevelItem( i )
            if itm is not None:
                if searchKey == itm.text(0):
                    itmFound = itm
                    break
        while indexes and itmFound is not None:
            searchKey = indexes.pop()
            itmFound = self.__onTemplateClicked(itm=itmFound, searchKey=searchKey)
        
        if itmFound is not None:
           self.treeWidgetLeft.tree.clearSelection()
           itmFound.setSelected(True)

    def __onTemplateClicked(self, itm, searchKey):
        """
        Sub function of on template clicked
        """
        itmFound = None
        for i in xrange( itm.childCount () ):
            itmChild = itm.child( i )
            if itmChild is not None:
                if searchKey == itmChild.text(0):
                    itmFound = itmChild
                    break
        return itmFound

    def onTemplateExpanded(self, indexes):
        """
        On template expanded
        """
        itmFound = None
        searchKey = indexes.pop()
        for i in xrange( self.treeWidgetLeft.tree.topLevelItemCount() ):
            itm = self.treeWidgetLeft.tree.topLevelItem( i )
            if itm is not None:
                if searchKey == itm.text(0):
                    itm.setExpanded(True)
                    itmFound = itm
                    break
        while indexes and itmFound is not None:
            searchKey = indexes.pop()
            itmFound = self.__onTemplateExpanded(itm=itmFound, searchKey=searchKey)
            
    def __onTemplateExpanded(self, itm, searchKey):
        """
        Sub function of on template expanded
        """
        itmFound = None
        for i in xrange( itm.childCount () ):
            itmChild = itm.child( i )
            if itmChild is not None:
                if searchKey == itmChild.text(0):
                    itmChild.setExpanded(True)
                    itmFound = itmChild
                    break
        return itmFound

    def onTemplateCollapsed(self, indexes):
        """
        On template collapsed
        """
        itmFound = None
        searchKey = indexes.pop()
        for i in xrange( self.treeWidgetLeft.tree.topLevelItemCount() ):
            itm = self.treeWidgetLeft.tree.topLevelItem( i )
            if itm is not None:
                if searchKey == itm.text(0):
                    itmFound = itm
                    break
        while indexes and itmFound is not None:
            searchKey = indexes.pop()
            itmFound = self.__onTemplateCollapsed(itm=itmFound, searchKey=searchKey)
        
        if itmFound is not None:
           itmFound.setExpanded(False)

    def __onTemplateCollapsed(self, itm, searchKey):
        """
        Sub function of on template collapsed
        """
        itmFound = None
        for i in xrange( itm.childCount () ):
            itmChild = itm.child( i )
            if itmChild is not None:
                if searchKey == itmChild.text(0):
                    itmFound = itmChild
                    break
        return itmFound

    def createWidgets(self):
        """
        QtWidgets creation
        """
        layout = QHBoxLayout()
        
        self.vSplitter = QSplitter(self) # textedit | textedit
        self.vSplitter2 = QSplitter(self) # treeview | treeview
        self.vSplitter3 = QSplitter(self) # treeview | tab(hexa/ascii)
        self.vSplitter4 = QSplitter(self) # treeview | textedit

        self.textEdit = RawView(parent=self)
        self.textEdit.setReadOnly(True)

        self.text2Edit = QTextEdit() # text right
        self.text2Edit.setReadOnly(True)

        self.text3Edit = QTextEdit()
        self.text3Edit.setReadOnly(True)

        self.rightTab = QTabWidget()

        # tab construction
        self.hexEdit = QTextEdit()
        self.hexEdit.setReadOnly(True)

        self.hexEdit2 = QTableWidget()
        self.hexEdit2.setSelectionMode(QAbstractItemView.SingleSelection)
        self.hexEdit2.setColumnCount(14)
        self.hexEdit2.verticalHeader().hide()
        self.hexEdit2.horizontalHeader().hide()

        self.rawEdit = RawView(parent=self)

        self.imgEdit = ImageView(self)

        self.xmlEdit = QtHelper.RawXmlEditor(parent=self)
        self.xmlEdit.setReadOnly(True)

        self.htmlEdit = RawView(parent=self)

        self.rightTab.addTab( self.rawEdit, "Raw View" )
        self.rightTab.addTab( self.xmlEdit, "XML View" )
        self.rightTab.addTab( self.htmlEdit, "HTML View" )
        self.rightTab.addTab( self.imgEdit, "Image View" )
        self.rightTab.addTab( self.hexEdit, "Hex View" )

        defaultTab = Settings.instance().readValue( key = 'TestRun/default-tab-view' )
        self.rightTab.setCurrentIndex(int(defaultTab))   

        # tree for template on left
        self.treeWidgetLeft = QTreeWidgetTemplate( self, signalsReadMore=True ) 
        self.treeWidgetLeft.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.treeWidgetLeft.tree.setStyleSheet( """QTreeWidget { border: 1px solid %s;}""" % Settings.instance().readValue( key = 'TestRun/tree-template-received-color' ) )
        
        # tree for events
        self.treeWidgetLeft2 = QTreeWidgetTemplate( self, signals=True, textHexa=self.hexEdit, textRaw=self.rawEdit , 
                                                    imgRaw=self.imgEdit, xmlRaw=self.xmlEdit, htmlRaw=self.htmlEdit )
        self.treeWidgetLeft2.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.treeWidgetLeft2.tree.setStyleSheet( """QTreeWidget { border: 1px solid %s;}""" % Settings.instance().readValue( key = 'TestRun/tree-event-background-color' ) )
        
        self.treeWidgetLeft3 = QTreeWidgetTemplate( self, signals=True, textRaw=self.text3Edit, withLabel=False  )
        self.treeWidgetLeft3.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        
        # tree for template messages 
        signalsExpanded = QtHelper.str2bool(Settings.instance().readValue( key = 'TestRun/auto-expandcollapse-templates' ))
        signalsClicked = QtHelper.str2bool(Settings.instance().readValue( key = 'TestRun/auto-selection-templates' ))
        self.treeWidgetRight = QTreeWidgetTemplate( self, signalsExpanded=signalsExpanded, signalsAutoSelect=signalsClicked, 
                                                    signalsReadMore=True ) 
        self.treeWidgetRight.setStatusLabels()
        self.treeWidgetRight.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.treeWidgetRight.tree.setStyleSheet( """QTreeWidget { border: 1px solid %s;}""" % Settings.instance().readValue( key = 'TestRun/tree-template-expected-color' ) )
        
        # text | text
        self.vSplitter.addWidget( self.textEdit )
        self.vSplitter.addWidget( self.text2Edit )
        self.vSplitter.setStretchFactor(1, 0)

        # treeview | treeview
        self.vSplitter2.addWidget( self.treeWidgetLeft )
        self.vSplitter2.addWidget( self.treeWidgetRight )
        self.vSplitter2.setStretchFactor(1, 0)
        self.vSplitter2.hide()

        # treeview | hexa/ascii
        self.vSplitter3.addWidget( self.treeWidgetLeft2 )
        self.vSplitter3.addWidget( self.rightTab )
        self.vSplitter3.setStretchFactor(1, 0)
        self.vSplitter3.hide()

        # treeview | text
        self.vSplitter4.addWidget( self.treeWidgetLeft3 )
        self.vSplitter4.addWidget( self.text3Edit )
        self.vSplitter4.setStretchFactor(1, 0)
        self.vSplitter4.hide()

        self.textEdit.setEnabled(False)
        self.text2Edit.setEnabled(False)
        self.text3Edit.setEnabled(False)
        self.hexEdit.setEnabled(False)
        self.hexEdit2.setEnabled(False)
        self.rawEdit.setEnabled(False)
        self.imgEdit.setEnabled(False)
        self.xmlEdit.setEnabled(False)

        layout.addWidget(self.vSplitter)    
        layout.addWidget(self.vSplitter2)   
        layout.addWidget(self.vSplitter3)
        layout.addWidget(self.vSplitter4)
        layout.setContentsMargins(0,0,0,0)
        self.setLayout(layout)

    def copyKeyIteem(self):
        """
        Copy the key item to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft2.tree.currentItem()
        itemKey = currentItem.getTextKey()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemKey) 

    def copyKeyItemLeft(self):
        """
        Copy the key item left to the clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft.tree.currentItem()
        itemKey = currentItem.getTextKey()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemKey) 

    def copyKeyItemLeft3(self):
        """
        Copy the key item left to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft3.tree.currentItem()
        itemKey = currentItem.getTextKey()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemKey) 

    def copyKeyItemRight(self):
        """
        Copy the key item right to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetRight.tree.currentItem()
        itemKey = currentItem.getTextKey()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemKey) 

    def copyValueIteem(self):
        """
        Copy the value item to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft2.tree.currentItem()
        itemValue = currentItem.getTextValue()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemValue) 

    def copyValueItemLeft(self):
        """
        Copy the value item left to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft.tree.currentItem()
        itemValue = currentItem.getTextValue()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemValue) 

    def copyValueItemLeft3(self):
        """
        Copy the value left item to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetLeft3.tree.currentItem()
        itemValue = currentItem.getTextValue()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemValue) 

    def copyValueItemRight(self):
        """
        Copy the value right to clipboard
        """
        # retrieve the text to copy
        currentItem = self.treeWidgetRight.tree.currentItem()
        itemValue = currentItem.getTextValue()

        # set clipboard 
        clipboard = QApplication.clipboard() 
        clipboard.setText(itemValue) 

    def expandAllItems(self):
        """
        Expand all items
        """
        self.treeWidgetLeft2.tree.expandAll()
        # self.itemEventExpandedCollapsed(item=None)
    
    def collapseAllItems(self):
        """
        Collapse all items
        """
        self.treeWidgetLeft2.tree.collapseAll()
        # self.itemEventExpandedCollapsed(item=None)

    def expandAllItemsLeft3(self):
        """
        Expand all items left
        """
        self.treeWidgetLeft3.tree.expandAll()
    
    def collapseAllItemsLeft3(self):
        """
        Collapse all items left
        """
        self.treeWidgetLeft3.tree.collapseAll()

    def expandAllItemsLeft(self):
        """
        Expand all items left
        """
        self.treeWidgetLeft.tree.expandAll()
    
    def collapseAllItemsLeft(self):
        """
        Collapse all items left
        """
        self.treeWidgetLeft.tree.collapseAll()

    def expandAllItemsRight(self):
        """
        Expand all item right
        """
        self.treeWidgetRight.tree.expandAll()
    
    def collapseAllItemsRight(self):
        """
        Collpase all item right
        """
        self.treeWidgetRight.tree.collapseAll()

    def expandItem(self, itm):
        """
        Expand item
        """
        itm.setExpanded(True)
        if itm.childCount() > 0:
            for i in xrange( itm.childCount() ):
                itm.child(i).setExpanded(True)
                if itm.child(i).childCount() > 0:
                    self.expandItem(itm=itm.child(i))

    def expandSubtreeIteem(self):
        """
        Expand the subtree item
        """
        currentItem = self.treeWidgetLeft2.tree.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)
            # self.itemEventExpandedCollapsed(item=currentItem)

    def expandSubtreeItemLeft(self):
        """
        Expand subtree item left
        """
        currentItem = self.treeWidgetLeft.tree.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)

    def expandSubtreeItemLeft3(self):
        """
        Expand subtree item left
        """
        currentItem = self.treeWidgetLeft3.tree.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)

    def expandSubtreeItemRight(self):
        """
        Expand subtree item right
        """
        currentItem = self.treeWidgetRight.tree.currentItem()
        if currentItem is not None:
            self.expandItem(itm=currentItem)

    def onPopupMenuLeft(self, pos):
        """
        On popup menu left

        @param pos:
        @type pos:
        """
        item = self.treeWidgetLeft.tree.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.menu.addAction( self.expandSubtreeActionLeft )
            self.menu.addAction( self.expandAllActionLeft )
            self.menu.addAction( self.collapseAllActionLeft )
            self.menu.addSeparator()
            self.menu.addAction( self.copyKeyActionLeft )
            self.menu.addAction( self.copyValueActionLeft )
            self.menu.addSeparator()
            self.menu.addAction(self.displayValueLeftAction)
            self.menu.popup(self.treeWidgetLeft.tree.mapToGlobal(pos))

    def onPopupMenuLeft3(self, pos):
        """
        On popup menu left

        @param pos:
        @type pos:
        """
        item = self.treeWidgetLeft3.tree.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.menu.addAction( self.expandSubtreeActionLeft3 )
            self.menu.addAction( self.expandAllActionLeft3 )
            self.menu.addAction( self.collapseAllActionLeft3 )
            self.menu.addSeparator()
            self.menu.addAction( self.copyKeyActionLeft3 )
            self.menu.addAction( self.copyValueActionLeft3 )
            self.menu.addSeparator()
            self.menu.addAction(self.displayValueLeft3Action)
            self.menu.popup(self.treeWidgetLeft3.tree.mapToGlobal(pos))

    def onPopupMenuRight(self, pos):
        """
        On popup menu right

        @param pos:
        @type pos:
        """
        item = self.treeWidgetRight.tree.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.menu.addAction( self.expandSubtreeActionRight )
            self.menu.addAction( self.expandAllActionRight )
            self.menu.addAction( self.collapseAllActionRight )
            self.menu.addSeparator()
            self.menu.addAction( self.copyKeyActionRight )
            self.menu.addAction( self.copyValueActionRight )
            self.menu.popup(self.treeWidgetRight.tree.mapToGlobal(pos))

    def onPopupMenu(self, pos):
        """
        On popup menu

        @param pos:
        @type pos:
        """
        item = self.treeWidgetLeft2.tree.itemAt(pos)
        self.menu = QMenu()
        if item:
            self.menu.addAction( self.expandSubtreeAction )
            self.menu.addAction( self.expandAllAction )
            self.menu.addAction( self.collapseAllAction )
            self.menu.addSeparator()
            self.menu.addAction( self.copyKeyAction )
            self.menu.addAction( self.copyValueAction )
            self.menu.addSeparator()
            self.menu.addAction(self.displayValueLeft2Action)

            self.menu.popup(self.treeWidgetLeft2.tree.mapToGlobal(pos))

    # def selectAuto(self):
        # """
        # Select auto
        # """
        # if not len(self.treeIndexesSelected):
            # return 
            
        # self.treeWidgetLeft2.tree.setFocus()
        
        # i = self.treeIndexesSelected.pop()
        
        # itm = self.treeWidgetLeft2.tree.topLevelItem(i)
        # if itm is None:
            # return
            
        # if not len(self.treeIndexesSelected):
            # itm.setSelected(True)
        # else:
            # self.__selectAuto(itm)
            
    # def __selectAuto(self, itm):
        # """
        # Select auto
        # """
        # j = self.treeIndexesSelected.pop()
        
        # itmchild = itm.child(j)
        # if itmchild is None:
            # return
            
        # if not len(self.treeIndexesSelected):
            # itmchild.setSelected(True)
        # else:
            # self.__selectAuto(itmchild)
                    
    def display (self, data, dataType, shortName):
        """  
        Display event

        @param data:
        @type data: 

        @param dataType:
        @type dataType: 

        @param shortName: 
        @type shortName:
        """
        if dataType == TYPE_DATA_PAYLOAD_V1:

            if isinstance(data, list):
                # reset widget
                self.reset()
                self.vSplitter3.show()
                self.vSplitter4.hide()
                self.vSplitter2.hide()
                self.vSplitter.hide()

                # extract payload header
                payloadHeader = data[-1:][0] # last position of the list

                payloadName, payloadValue = payloadHeader
                if payloadName == TYPE_DATA_PAYLOAD_V1:
                    self.extractHeader(val=payloadValue)

                # read payload
                for kv in data:
                    self.loadTreeTemplate(kv, parent=self.treeWidgetLeft2.tree)
                
                # expand item ?
                if QtHelper.str2bool(Settings.instance().readValue( key = 'TestRun/auto-expandcollapse-events' )):
                    self.EventTreeMemory.restore()
                    # self.expandAuto()
                    # self.selectAuto()
                    
            else:
                pass

        elif dataType == TYPE_DATA_STEP:
            if isinstance(data, list):
                self.reset()
                self.vSplitter3.show()
                self.vSplitter4.hide()
                self.vSplitter2.hide()
                self.vSplitter.hide()
                
                # extract payload header
                payloadHeader = data[-1:][0] # last position of the list

                payloadName, payloadValue = payloadHeader
                if payloadName == TYPE_DATA_PAYLOAD_V1:
                    self.extractHeader(val=payloadValue)

                # read payload
                for kv in data:
                    self.loadTreeTemplate(kv, parent=self.treeWidgetLeft2.tree)

                itm = self.treeWidgetLeft2.tree.topLevelItem( 0 )
                if itm is not None:
                    itm.setExpanded(True)
            else:
                pass

        elif dataType == TYPE_DATA_MATCH:

            if isinstance(data, list):
                # reset widget
                self.reset()
                self.vSplitter2.show()
                self.vSplitter4.hide()
                self.vSplitter3.hide()
                self.vSplitter.hide()
                if 'expected template' in shortName.lower() :
                    self.treeWidgetLeft.setLabel('Template Expected')
                elif  'template match' in shortName.lower() :
                    self.treeWidgetLeft.setLabel('Template Received')
                elif 'template mismatch' in shortName.lower():
                    self.treeWidgetLeft.setLabel('Template Received')
                else:
                    self.treeWidgetLeft.frameLabel.setText('')
                
                # read payload
                for kv in data:
                    self.loadTreeTemplate(kv, parent=self.treeWidgetLeft.tree, template=True)
                    
                if QtHelper.str2bool(Settings.instance().readValue( key = 'TestRun/auto-expandcollapse-templates' )):
                    self.TemplateTreeMemory.restore()
                    
            else:
                self.reset()
                self.vSplitter.show()
                self.vSplitter2.hide()
                self.vSplitter3.hide()
                self.vSplitter4.hide()

        elif dataType == TYPE_DATA_MATCH_RECEIVED:

            if isinstance(data, list) or isinstance(data, tuple):
                # extract received and expecte templates
                received, expected = data
                
                # reset received template widget
                self.reset()
                self.vSplitter2.show()
                self.vSplitter4.hide()
                self.vSplitter3.hide()
                self.vSplitter.hide()
                if 'expected template' in shortName.lower() :
                    self.treeWidgetLeft.setLabel('Template Expected')
                elif  'template match' in shortName.lower() :
                    self.treeWidgetLeft.setLabel('Template Received')
                elif 'template mismatch' in shortName.lower():
                    self.treeWidgetLeft.setLabel('Template Received')
                else:
                    self.treeWidgetLeft.frameLabel.setText('')
                
                # read received template
                for kv in received:
                    self.loadTreeTemplate(kv, parent=self.treeWidgetLeft.tree,template=False)
                                                
                # reset expected template widget
                self.treeWidgetRight.clear()
                self.treeWidgetRight.show()
                self.treeWidgetRight.setLabel('Template Expected')

                # read received template
                for kv in expected:
                    self.loadTreeTemplate(kv, parent=self.treeWidgetRight.tree,template=True)
                    
                if QtHelper.str2bool(Settings.instance().readValue( key = 'TestRun/auto-expandcollapse-templates' )):
                    self.TemplateTreeMemory.restore()
            else:
                self.reset()
                self.vSplitter.show()
                self.vSplitter2.hide()
                self.vSplitter3.hide()
                self.vSplitter4.hide()

        elif dataType == TYPE_DATA_TIMER:
            # reset widget
            self.reset()
            self.vSplitter.show()
            self.vSplitter2.hide()
            self.vSplitter3.hide()
            self.vSplitter4.hide()

            self.textEdit.setPlainText( data )
            self.textEdit.setEnabled(True)

        else:
            if data is None:
                self.reset()
                self.vSplitter.show()
                self.vSplitter2.hide()
                self.vSplitter3.hide()
                self.vSplitter4.hide()
            else:
                self.reset()
                self.vSplitter.show()
                self.vSplitter2.hide()
                self.vSplitter3.hide()
                self.vSplitter4.hide()
                if dataType == 'raw':
                    self.textEdit.setPlainText( data )
                else:
                    self.textEdit.setHtml(html=data)
                self.textEdit.setEnabled(True)

    def loadTreeTemplate (self, keyval, parent, template=False):
        """
        Load the tree template

        Payload view version 1

        @param keyval: 
        @type keyval:

        @param parent: 
        @type parent:
        """
        if isinstance(keyval, list) or isinstance(keyval, tuple):
            key, val = keyval
            if key != TYPE_DATA_PAYLOAD_V1:
                valueRaw = None
                clr = 'bl'
                clrValue = None
                if template:
                    key, clr = self.getColor(txt=key)
                if isinstance(val, dict):
                    if '%%raw-layer%%' in val:
                        valueRaw = copy.deepcopy( val['%%raw-layer%%'] )

                keyItem = KeyItem( key = key, valueRaw=valueRaw, parent = parent, colorKey = clr, colorValue = clrValue, noLimit=False)
                self.loadTreeTemplate( val,keyItem,template )
       
        elif isinstance(keyval, dict):

            for h,v in keyval.items():  
                clr = 'b'
                clrValue = None
                
                # convert int and float values to integer, should not be happen
                if isinstance(v, int) or isinstance(v, float):
                    v = str(v)
                
                if not ( isinstance( v, tuple) or isinstance(v, list) ):
                    if template:
                        v, clrValue = self.getColor(txt=v)      
                if template:
                    h, clr = self.getColor(txt=h)

                if clr == "y" or clr == "r":
                    clrValue = "y" 

                if isinstance(parent, KeyItem):
                    if parent.color == "y":
                        clr = "y"
                        clrValue = "y"

                if isinstance(v, tuple) or isinstance(v, list):
                    if len(v) == 2:
                        sk, sv = v
                        if template:
                            sk, clrValue = self.getColor(txt=sk)
                        hdrItem = KeyItem( key = str(h), value = sk, parent = parent, colorKey = clr, colorValue = clrValue, noLimit=False )
                        self.loadTreeTemplate( sv,hdrItem,template )
                    else:
                        print('bad value: %s, tuple expected or list of 2 elements' % v)
                else:
                    # display all items except the internal key
                    if str(h) != '%%raw-layer%%':
                        hdrItem = KeyItem( key = str(h), value = v, parent = parent, colorKey = clr, colorValue = clrValue, noLimit=False )
        else:
            pass

    def getColor(self, txt):
        """
        Returns color
        """
        clr = 'b'

        # convert to str
        if isinstance(txt, int) or isinstance(txt, long): 
            txt = str(txt)

        # python3 support
        if sys.version_info >(3,) and isinstance(txt, bytes):
            txt = str(txt, 'utf8', errors="ignore")
            
        if isinstance(txt, str) or isinstance(txt, unicode) :
            if txt.startswith('$g'):
                clr = 'g'
                txt = txt[2:]
            if txt.startswith('$r'):
                clr = 'r'
                txt = txt[2:]
            if txt.startswith('$y'):
                clr = 'y'
                txt = txt[2:]
            if txt.startswith('$bl'):
                clr = 'bl'
                txt = txt[3:]
        else:
            clr = 'r'
            txt = str(txt) # issue 287
            self.parent.error( 'detailed view, unknown type: %s' % type(txt) )
        return txt, clr

    def extractHeader(self, val):
        """
        Extract header of the event

        @param val: 
        @type val:
        """
        # {'raw': '', 'len': 0, 'time': 1339864775.215465}
        sz = val['len']

        hx = base64.b64decode(val['raw'])
        t =  val['time']
        
        resume = ''
        if sz == 0:
            resume = 'Arrival Time: %s' % QtHelper.formatTimestamp(t, milliseconds=True)
        else:
            resume = 'Length: %s, Arrival Time: %s' % ( QtHelper.bytes2human(sz), QtHelper.formatTimestamp(t, milliseconds=True) )
        self.treeWidgetLeft2.setLabel(resume  )
        
        # update image view
        self.imgEdit.setImage(content=hx)
        
        if sys.version_info > (3,): # python3 support
            hx = str(hx, 'utf-8', errors='ignore')
            
        # fills raw view
        self.rawEdit.setEnabled(True)
        if sys.version_info > (3,):
            rawTxt = hx
        else:
            rawTxt = removeNonPrintableCharacter(datas=hx)
        self.rawEdit.setPlainText( rawTxt )
        self.htmlEdit.setEnabled(True)
        self.htmlEdit.setHtml( rawTxt )

        # fills xml view
        self.xmlEdit.setEnabled(True)
        xmlTxt = rawTxt.replace('><', '>\r\n<')
        self.xmlEdit.setText(xmlTxt)

        # fills hex view
        self.hexEdit.setEnabled(True)
        hexas = ["%02X" % (ord(ch),) for ch in str(hx) ]
        self.hexEdit.setPlainText( ' '.join(hexas) )

    def reset (self):
        """
        Reset widgets
        """
        self.textEdit.resetView()
        self.text2Edit.setPlainText( "" )
        self.text3Edit.setPlainText( "" )
        self.hexEdit.setPlainText( "" )
        self.rawEdit.resetView()
        self.htmlEdit.resetView()
        self.imgEdit.resetView()
        self.xmlEdit.setText("")

        self.treeWidgetLeft.clear()
        self.treeWidgetLeft2.clear()
        self.treeWidgetLeft3.clear()
        self.treeWidgetRight.clear()

        self.textEdit.setEnabled(False)
        self.text2Edit.setEnabled(False)
        self.text3Edit.setEnabled(False)
        self.hexEdit.setEnabled(False)
        self.rawEdit.setEnabled(False)
        self.imgEdit.setEnabled(False)
        self.xmlEdit.setEnabled(False)
        self.htmlEdit.setEnabled(False)
