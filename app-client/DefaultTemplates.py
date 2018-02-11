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
Templates files
"""

from Libs import QtHelper, Logger

import zlib
import sys

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
    
class Templates(Logger.ClassLogger):
    """
    Handle templates files
    """
    def __init__(self):
        """
        Constructor
        """
        self.tplTuFile = '%s/Files/testunit_def.tpl' % QtHelper.dirExec()
        self.tplDefFile = '%s/Files/testsuite_def.tpl' % QtHelper.dirExec()
        self.tplExecFile = '%s/Files/testsuite_exec.tpl' % QtHelper.dirExec()
        self.tplAdpFile = '%s/Files/adapter.tpl' % QtHelper.dirExec()
        self.tplLibFile = '%s/Files/library.tpl' % QtHelper.dirExec()
        # auto
        self.tplTuFileAuto = '%s/Files/testunit_def_auto.tpl' % QtHelper.dirExec()
        self.tplDefFileAuto = '%s/Files/testsuite_def_auto.tpl' % QtHelper.dirExec()
        self.tplExecFileAuto = '%s/Files/testsuite_exec_auto.tpl' % QtHelper.dirExec()

    def getTestUnitDefinition(self):
        """
        Return test unit definition
        """
        return self.openDefautTemplate(filename=self.tplTuFile)

    def getTestDefinition(self):
        """
        Return test definition
        """
        return self.openDefautTemplate(filename=self.tplDefFile)

    def getTestExecution(self):
        """
        Return test execution
        """
        return self.openDefautTemplate(filename=self.tplExecFile)

    def getTestUnitDefinitionAuto(self):
        """
        Return test unit definition for automatic test
        """
        return self.openDefautTemplate(filename=self.tplTuFileAuto)

    def getTestDefinitionAuto(self):
        """
        Return test definition for automatic test
        """
        return self.openDefautTemplate(filename=self.tplDefFileAuto)

    def getTestExecutionAuto(self):
        """
        Return test execution for automatic test
        """
        return self.openDefautTemplate(filename=self.tplExecFileAuto)

    def getAdapter(self):
        """
        Return adapter template
        """
        return self.openDefautTemplate(filename=self.tplAdpFile)

    def getLibrary(self):
        """
        Return library template
        """
        return self.openDefautTemplate(filename=self.tplLibFile)

    def setTestUnitDefinition(self, data):
        """
        Save test unit definition
        """
        return self.saveDefautTemplate(filename=self.tplTuFile, data=data)

    def setTestDefinition(self, data):
        """
        Save test definition
        """
        return self.saveDefautTemplate(filename=self.tplDefFile, data=data)

    def setTestExecution(self, data):
        """
        Save test execution
        """
        return self.saveDefautTemplate(filename=self.tplExecFile, data=data)

    def setTestUnitDefinitionAuto(self, data):
        """
        Save test unit definition for automatic test 
        """
        return self.saveDefautTemplate(filename=self.tplTuFileAuto, data=data)

    def setTestDefinitionAuto(self, data):
        """
        Save test definition for automatic test 
        """
        return self.saveDefautTemplate(filename=self.tplDefFileAuto, data=data)

    def setTestExecutionAuto(self, data):
        """
        Save test exeuction for automatic test
        """
        return self.saveDefautTemplate(filename=self.tplExecFileAuto, data=data)

    def setAdapter(self, data):
        """
        Save adapter template
        """
        return self.saveDefautTemplate(filename=self.tplAdpFile, data=data)

    def setLibrary(self, data):
        """
        Save library template
        """
        return self.saveDefautTemplate(filename=self.tplLibFile, data=data)

    def openDefautTemplate(self, filename):
        """
        Open default template
        """
        ret = ''
        try:
            f = open(filename, 'rb')
            read_data = f.read()
            f.close()
        except Exception as e:
            self.error( "unable to read default template: %s" % e)
            return ret
        try:
            ret = zlib.decompress(read_data) # return data as bytes
        except Exception as e:
            self.error("unable to decompress default template: %s" % str(e))
            return ret
        
        if sys.version_info > (3,): # python3 support
            # convert bytes to str
            return str(ret, 'utf8')
        else:
            return ret.decode("utf8")

    def saveDefautTemplate(self, filename, data):
        """
        Save default template
        """
        try:
            # open the file as binary
            f = open(filename, 'wb')

            # compress data with zip
            if sys.version_info > (3,): # python3 support
                # convert data to bytes 
                compressTpl = zlib.compress(bytes(data, 'utf8'))
            else:
                compressTpl = zlib.compress(data)
            
            # write data and close it
            f.write(compressTpl)
            f.close()
            return True
        except Exception as e:
            self.error( "unable to write default template: %s" % e)
            return False
        return True
