#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -------------------------------------------------------------------

import sys
import os

try:
    import cPickle
except ImportError:  # support python 3
    import pickle as cPickle


STORAGE_MODE_FILE = "FILE"
STORAGE_MODE_MEM = "MEM"


class TestDataStorage:
    """
    Test data storage
    """

    def __init__(self, path, storageMode=STORAGE_MODE_MEM):
        """
        Constructor for the test data storage
        """
        self.__filename = 'storage.dat'
        self.__path = path
        self.__storageMode = storageMode
        self.__storageData = {}

    def save_data(self, data):
        """
        Save data on the storage
        """
        validData = False
        if isinstance(data, str):
            validData = True
        if isinstance(data, list):
            validData = True
        if isinstance(data, dict):
            validData = True
        if isinstance(data, tuple):
            validData = True

        if self.__storageMode == STORAGE_MODE_MEM:
            if validData:
                self.__storageData = data

        storagePath = '%s/%s' % (self.__path, self.__filename)
        storagePath = os.path.normpath(storagePath)
        try:
            if validData:
                fd = open(storagePath, 'wb')
                fd.write(cPickle.dumps(data))
                fd.close()
        except Exception as e:
            self.error("[save_data] %s" % str(e))

    def load_data(self):
        """
        Load data from the storage
        """
        if self.__storageMode == STORAGE_MODE_MEM:
            return self.__storageData

        storagePath = '%s/%s' % (self.__path, self.__filename)
        storagePath = os.path.normpath(storagePath)

        # check if the storage.dat file exists ?
        if not os.path.exists(storagePath):
            return {}

        # read the file and unpickle the content
        try:
            fd = open(storagePath, "r")
            data = fd.read()
            fd.close()
            return cPickle.loads(data)
        except Exception as e:
            self.error("[load_data] %s" % str(e))
            return None

    def reset_data(self):
        """
        Reset data from the storage
        """
        if self.__storageMode == STORAGE_MODE_MEM:
            del self.__storageData
            self.__storageData = {}
            return True

        storagePath = '%s/%s' % (self.__path, self.__filename)
        storagePath = os.path.normpath(storagePath)

        # check if the file exists?
        if not os.path.exists(storagePath):
            return {}

        # Empty the file storage.dat
        try:
            fd = open(storagePath, "wb")
            fd.write("")
            fd.close()
            return True
        except Exception as e:
            self.error("[reset_data] %s" % str(e))
            return False

    def error(self, err):
        """
        Log error
        """
        sys.stderr.write("[%s] %s\n" % (self.__class__.__name__, err))


TDS = None


def instance():
    """
    """
    if TDS:
        return TDS


def initialize(path):
    """
    """
    global TDS
    TDS = TestDataStorage(path=path)


def finalize():
    """
    """
    global TDS
    if TDS:
        TDS = None
