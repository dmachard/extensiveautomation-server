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

from ea.libs import Settings
import pickle
import sys

import DocInspect

sys.path.insert(0, '../../../')


# initialize settings module to read the settings.ini file
Settings.initialize(path="./")

cache_pathfile = "%s/%s/documentations.dat" % (Settings.getDirExec(),
                                               Settings.get('Paths', 'var'))


def extractTestExecutor(lib):
    """
    """
    pkg_te = __import__("ea.testexecutorlib", fromlist=[lib])
    descr_pkg = getattr(pkg_te, '__DESCRIPTION__')

    lib_obj = getattr(pkg_te, lib)
    lib_descr = getattr(lib_obj, '__DESCRIPTION__')
    classes = getattr(lib_obj, '__HELPER__')

    pkg_desc = DocInspect.describePackage(pkg_te,
                                          modules=[(lib, classes, lib_descr)],
                                          descr=descr_pkg)
    return pkg_desc


def generate_helps():
    """
    Return help for the test executor library
    """
    try:
        pkgDesc = extractTestExecutor(lib="TestExecutorLib")
        pkgDesc['name'] = 'TestLibrary'
        pkgDesc['modules'][0]['name'] = 'TestExecutor'
    except Exception as e:
        raise Exception("TE_EXE: %s" % e)

    try:
        pkgDesc2 = extractTestExecutor(lib="TestOperatorsLib")
        pkgDesc2['modules'][0]['name'] = 'TestOperators'
        pkgDesc['modules'].append(pkgDesc2['modules'][0])
    except Exception as e:
        raise Exception("TE_OPE: %s" % e)

    try:
        pkgDesc4 = extractTestExecutor(lib="TestValidatorsLib")
        pkgDesc4['modules'][0]['name'] = 'TestValidators'
        pkgDesc['modules'].append(pkgDesc4['modules'][0])
    except Exception as e:
        raise Exception("TE_VAL: %s" % e)

    try:
        pkgDesc5 = extractTestExecutor(lib="TestTemplatesLib")
        pkgDesc5['modules'][0]['name'] = 'TestTemplates'
        pkgDesc['modules'].append(pkgDesc5['modules'][0])
    except Exception as e:
        raise Exception("TE_TPL: %s" % e)

    try:
        pkgDesc7 = extractTestExecutor(lib="TestReportingLib")
        pkgDesc7['modules'][0]['name'] = 'TestReporting'
        pkgDesc['modules'].append(pkgDesc7['modules'][0])
    except Exception as e:
        raise Exception("TE_REP: %s" % e)

    try:
        pkgDesc9 = extractTestExecutor(lib="TestAdapterLib")
        pkgDesc9['modules'][0]['name'] = 'SutAdapter'
        pkgDesc['modules'].append(pkgDesc9['modules'][0])
    except Exception as e:
        raise Exception("TE_ADP: %s" % e)

    return [pkgDesc]


def save_helps(data, file):
    """
    Save data to the cache file
    The cache file is sent to users to construct the documentation
    """
    fd = open(file, 'wb')
    fd.write(pickle.dumps(data))
    fd.close()


if __name__ == "__main__":
    return_code = 0

    # read the docs from source code
    ret = []
    try:
        ret.extend(generate_helps())
    except Exception as e:
        sys.stderr.write('Test Library: %s\n' % str(e))
        return_code = 1

    # save the docs to file
    try:
        save_helps(data=ret, file=cache_pathfile)
    except Exception as e:
        sys.stderr.write('error to helps: %s\n' % str(e))
        return_code = 1

    # finalize the script
    Settings.finalize()
    sys.exit(return_code)
