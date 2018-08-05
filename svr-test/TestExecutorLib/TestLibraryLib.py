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


import wrapt

@wrapt.decorator
def doc_public(wrapped, instance, args, kwargs):
    """
    New in v17
    public decorator for documentation
    """
    return wrapped(*args, **kwargs)
    
__DESCRIPTION__ = """The library provides some important functionalities to create library."""

try:
    import TestSettings
    import TestAdapterLib
except ImportError: # python3 support
    from . import TestSettings
    from . import TestAdapterLib
    
import re

__version_libs = ''
__version_generic_libs = ''

def getDefaultVersion():
    """
    Return default version

    @return: default version
    @rtype: string
    """
    return getVersion()

def getGenericVersion():
    """
    Return generic version

    @return: generic version
    @rtype: string
    """
    return getVersionGeneric()

def setVersionGeneric(ver):
    """
    Set version
    """
    global __version_generic_libs
    __version_generic_libs = ver
    
def setVersion(ver):
    """
    Set version
    """
    pkg = __import__("SutLibraries")
    pkg = __import__("SutLibraries.%s" % ver)
    global __version_libs
    __version_libs = ver

def getVersion():
    """
    Return version
    """
    global __version_libs
    return __version_libs

def getVersionGeneric():
    """
    Return version
    """
    global __version_generic_libs
    return __version_generic_libs
    
__deprecated_library = False

def setDeprecated():
    """
    Set as deprecated
    """
    global __deprecated_library
    __deprecated_library = True

def isDeprecated():
    """
    Is deprecated
    """
    global __deprecated_library
    return __deprecated_library


def caller():
    """
    Function to find out which function is the caller of the current function. 

    @return: caller function name
    @rtype: string
    """
    return  inspect.getouterframes(inspect.currentframe())[1][1:4]

class Version(object):
    """
    """
    @doc_public
    def getDefault(self):
        """
        Return default version

        @return: default version
        @rtype: string
        """
        return getVersion()
        
    @doc_public
    def getGeneric(self):
        """
        Return generic version

        @return: generic version
        @rtype: string
        """
        return getVersionGeneric()

class LibraryException(Exception):
    """
    """
    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg
    def __str__(self):
        """
        """
        # sut adapters path normalized, remove double // or more
        sut = re.sub("/{2,}", "/", getMainPath())
        
        f = self.orig[0].split(sut)[1]
        ret = "Library.%s > %s" % (self.orig[2],self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret

class ValueException(Exception):
    """
    """
    def __init__(self, orig, msg):
        """
        """
        self.orig = orig
        self.msg = msg
    def __str__(self):
        """
        """
        # sut adapters path normalized, remove double // or more
        sut = re.sub("/{2,}", "/", getMainPath())
        
        f = self.orig[0].split(sut)[1]
        ret = "Library.%s > %s" % (self.orig[2],self.msg)
        ret += '\nFile: %s' % f
        ret += '\nLine error: %s' % self.orig[1]
        return ret
        
LEVEL_LIBRARY = 'LIBRARY'
LEVEL_USER = 'USER'

class Library(TestAdapterLib.Adapter):
    """
    Library
    """
    @doc_public
    def __init__(self, parent, name, realname=None, debug=False, showEvts=True, 
                 showSentEvts=True, showRecvEvts=True, shared=False):
        """
        All libraries must inherent from this class

        @param parent: the parent testcase
        @type parent: testcase

        @param name: library name
        @type name: string

        @param debug: True to activate debug mode, default value=False
        @type debug: boolean
        
        @param shared: True to activate shared mode, default value=False
        @type shared: boolean
        """
        TestAdapterLib.Adapter.__init__(self, parent=parent, name=name, realname=realname, debug=debug, showEvts=showEvts,
                                            showSentEvts=showSentEvts, showRecvEvts=showRecvEvts, shared=shared)
        self.realname__ = realname
        self.__testcase = parent

    def getFromLevel(self):
        """
        Return the from level
        """
        if self.realname__ is None:
            self.realname__ = "%s #%s" % (LEVEL_LIBRARY, self.__adp_id__)
        return self.realname__.upper()
    @doc_public
    def testcase(self):
        """
        Accessor to the testcase
        """
        return self.__testcase
    @doc_public    
    def info (self, txt, bold = False, italic=False, multiline=False, raw=False):
        """
        Display an info message

        @param txt: info message
        @type txt: string

        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """ 
        TestAdapterLib.Adapter.info(self, txt=txt, bold=bold, italic=italic, 
                                    multiline=multiline, raw=raw)
    @doc_public
    def error (self, txt, bold = False, italic=False, multiline=False, raw=False):
        """
        Display an error message

        @param txt: error message
        @type txt: string
        
        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """ 
        TestAdapterLib.Adapter.error(self, txt=txt, bold = bold, italic=italic, 
                                     multiline=multiline, raw=raw)

    def trace (self, txt, bold = False, italic=False, multiline=False, raw=False):
        """
        Trace message
        Nothing is displayed if txt=None
        
        @param txt: trace message
        @type txt: string

        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """ 
        TestAdapterLib.Adapter.trace(self, txt=txt, bold = bold, italic=italic, 
                                     multiline=multiline, raw=raw)
    @doc_public
    def warning (self, txt, bold = False, italic=False, multiline=False, raw=False):
        """
        Display an debug message

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold
        @type bold: boolean

        @param italic: text is rendered as italic
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """ 
        TestAdapterLib.Adapter.warning(self, txt=txt, bold = bold, italic=italic, 
                                       multiline=multiline, raw=raw)
    @doc_public
    def debug(self, txt, raw=True):
        """
        Display an debug message

        @param txt: debug message
        @type txt: string
        """
        TestAdapterLib.Adapter.debug(self, txt=txt, raw=raw )
    @doc_public    
    def onReset (self):
        """
        On reset, called automatically by framework
        Function to overwrite
        """
        pass