#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2020 Denis Machard
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

import base64
import sys
import os

from ea.libs import Settings
from ea.libs.FileModels import TestData as TestData
from ea.serverrepositories import (RepoTests)
from ea.serverengine import (ProjectsManager)

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

TS_ENABLED = "2"
TS_DISABLED = "0"

IMPORT_PY_LIBS = """#!/usr/bin/python -O
# -*- coding: utf-8 -*-
import sys
import time
import re

try:
    xrange
except NameError: # support python3
    xrange = range

"""

IMPORT_INTRO = """
task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root)

if sys.version_info > (3,):
    sys.stdout = sys.stderr = open('%s/test.log' % result_path,'a+', 1)
else:
    sys.stdout = sys.stderr = open('%s/test.log' % result_path,'a', 0)
"""

IMPORT_TE_LIBS = """

from ea.libs import Scheduler
from ea.testexecutorlib import TestLoggerXml as TLX
from ea.testexecutorlib import TestDataStorage as TDS
from ea.testexecutorlib import TestClientInterface as TCI

from ea.testexecutorlib import *
from ea.testexecutorlib import TestPropertiesLib as TestProperties
from ea.testexecutorlib import TestOperatorsLib as TestOperators
from ea.testexecutorlib import TestValidatorsLib as TestValidators
from ea.testexecutorlib import TestExecutorLib as TestExecutorLib
from ea.testexecutorlib import TestTemplatesLib as TestTemplates
from ea.testexecutorlib import TestAdapterLib as TestAdapter
from ea.testexecutorlib import TestReportingLib as TestReporting
from ea.testexecutorlib import TestLibraryLib as TestLibrary

from ea.testexecutorlib.TestExecutorLib import *

SutAdapter = TestAdapter
SutLibrary = TestLibrary
"""

TEST_SUMMARY = """

    inputs_str = []
    for i in inputs():
        if i['type'] in ['snapshot-image', 'local-file', 'local-image', 'dataset' ]:
            inputs_str.append('\\t* %s (%s) = ...binary...' % (i['name'], i['type']))
        else:
            try:
                val_tmp = str(i['value'])
            except Exception:
                val_tmp = i['value'].encode('utf8')
            inputs_str.append('\\t* %s (%s) = %s' % (str(i['name']), str(i['type']), val_tmp))

    ts_summary = ['Description']
    ts_summary.append('\\tAuthor: \\t%s' % description('author'))
    ts_summary.append('\\tRun at: \\t%s' % time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(scriptstart_time)))
    ts_summary.append('\\tPurpose: \\t%s' % description('summary'))
    ts_summary.append('\\tInputs: \\t\\n%s' % '\\n'.join(inputs_str))

    sum_dict = []
    sum_dict.append(('run at', time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(scriptstart_time))))
    sum_dict.append(('run by', user_))
    sum_dict.append(('test name', test_name))
    sum_dict.append(('test path', test_location))
    sum_dict.append(('project name', projectname_))
    tsMgr.setDescription(sum_dict)
"""

TEST_SUMMARY_TG = """
    TLX.instance().log_testglobal_internal(message='\\n'.join(ts_summary),
                                           component='TESTGLOBAL',
                                           bold=False,
                                           italic=True,
                                           fromlevel=LEVEL_TE,
                                           tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TP = """
    TLX.instance().log_testplan_internal(message='\\n'.join(ts_summary),
                                         component='TESTPLAN',
                                         bold=False,
                                         italic=True,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TS = """
    TLX.instance().log_testsuite_internal(message='\\n'.join(ts_summary),
                                          component='TESTSUITE',
                                          bold=False,
                                          italic=True,
                                          fromlevel=LEVEL_TE,
                                          tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TU = """
    TLX.instance().log_testunit_internal(message='\\n'.join(ts_summary),
                                         component='TESTUNIT',
                                         bold=False,
                                         italic=True,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER)
"""

INPUT_CACHE = """
def cache(key):
    return Cache().get(name=key)
TestProperties.cache = cache
"""

INPUT_CUSTOM = r"""
def custom_text(line):
    cache = re.findall("\[!CACHE:[\w-]+(?:\:[\w-]+)*\:\]", line)
    new_line = line

    for c in cache:
        cache_args = c.split(":")[1:-1]
        v = Cache().get(name=cache_args[0])
        cache_args = cache_args[1:]
        while len(cache_args):
            if isinstance(v, dict):
                v = v.get(cache_args[0])
            cache_args = cache_args[1:]
        new_line = new_line.replace(c, "%s" % v, 1)

    inputs = re.findall("\[!INPUT:[\w-]+(?:\:[\w-]+)*\:\]", new_line)
    for c in inputs:
        input_args = c.split(":")[1:-1]
        v = input(input_args[0])
        i = 1
        while i<len(input_args):
            if isinstance(v, dict):
                v = v[input_args[i]]
            i=i+1
        new_line = new_line.replace(c, "%s" % v, 1)

    captures = re.findall("\[!CAPTURE:[\w-]+(?:\:.*?)??\:\]", new_line)
    for c in captures:
        sub = c[2:-2]
        captures_args = sub.split(":", 2)[1:]
        if len(captures_args) == 2:
            new_line = new_line.replace(c, "(?P<%s>%s)" % (captures_args[0], captures_args[1]), 1)
        else:
            new_line = new_line.replace(c, "(?P<%s>.*)" % captures_args[0], 1)
    return new_line
def custom_json(line):
    line = re.sub(r"#.*", "", line)
    cache = re.findall("\[!CACHE:[\w-]+(?:\:[\w-]+)*\:\]", line)
    new_line = line

    for c in cache:
        cache_args = c.split(":")[1:-1]
        v = Cache().get(name=cache_args[0])
        cache_args = cache_args[1:]
        while len(cache_args):
            if isinstance(v, dict):
                v = v.get(cache_args[0])
            cache_args = cache_args[1:]
        new_line = new_line.replace(c, "%s" % v, 1)

    inputs = re.findall("\[!INPUT:[\w-]+(?:\:[\w-]+)*\:\]", new_line)
    for c in inputs:
        input_args = c.split(":")[1:-1]
        v = input(input_args[0])
        i = 1
        while isinstance(v, dict):
            v = v[input_args[i]]
            i=i+1
        new_line = new_line.replace(c, "%s" % v, 1)
    new_line = re.sub(r"None", "null", new_line)
    return new_line
TestProperties.custom_text = custom_text
TestProperties.custom_json = custom_json
"""


def getTestsPath(envTmp=False):
    """
    Get the path of all tests result

    @return:
    @rtype: string
    """
    if envTmp:
        trPath = '%s%s' % (Settings.getDirExec(),
                           Settings.get('Paths', 'testsresults-tmp'))
    else:
        trPath = '%s%s' % (Settings.getDirExec(),
                           Settings.get('Paths', 'testsresults'))

    # normalize the path and return it
    return os.path.normpath(trPath)


def indent(code, nbTab=1):
    """
    Add tabulation for each lines

    @param nbTab:
    @type nbTab: int

    @return:
    @rtype: string
    """
    tab = '    '
    indentChar = tab * nbTab
    ret = []
    for line in code.splitlines():
        ret.append("%s%s" % (indentChar, line))
    return '\n'.join(ret)


def getStaticArgs(envTmp=False):
    """
    """
    te_args = """root = r'%s/../'
tests_result_path = r'%s'
controller_ip = '%s'
controller_port = %s
""" % (
        os.path.normpath(Settings.getDirExec()),
        os.path.normpath(getTestsPath(envTmp=envTmp)),
        Settings.get('Bind', 'ip-tsi'),
        Settings.get('Bind', 'port-tsi')
    )
    return te_args


def loadImages(parameters, user=''):
    """
    """
    missingImages = []
    for pr in parameters:
        if pr['type'] == 'remote-image':
            if pr['value'].startswith('undefined:/'):
                dataEncoded = pr['value'].split('undefined:/')[1]
                if dataEncoded:
                    pr['value'] = base64.b64decode(dataEncoded)
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('remote-tests('):
                try:
                    fileName = pr['value'].split('):/', 1)[1]
                    projectName = pr['value'].split(
                        'remote-tests(', 1)[1].split('):/', 1)[0]
                except Exception:
                    missingImages.append(pr['value'])
                    pr['value'] = ''
                else:
                    projectId = 0
                    allPrjs = ProjectsManager.instance().getProjects(user=user)
                    for p in allPrjs:
                        if p['name'] == projectName:
                            projectId = p['project_id']
                            break

                    absPath = "%s/%s/%s" % (RepoTests.instance().testsPath,
                                            projectId,
                                            fileName)
                    try:
                        f = open(absPath, 'rb')
                        pr['value'] = f.read()
                        f.close()
                    except Exception:
                        missingImages.append(''.join([fileName]))
            else:
                pass
    return missingImages


def loadDataset(parameters, inputs=True, user=''):
    """
    """
    missingDataset = []
    for pr in parameters:
        if pr['type'] == 'dataset':
            if pr['value'].startswith('undefined:/'):
                dataEncoded = pr['value'].split('undefined:/')[1]
                if dataEncoded:
                    dataDecoded = base64.b64decode(dataEncoded)
                    doc = TestData.DataModel()
                    res = doc.load(rawData=dataDecoded)
                    if not res:
                        pr['value'] = ''
                    else:
                        if inputs:
                            parametersBis = doc.properties['properties']['inputs-parameters']['parameter']
                        for p in parametersBis:
                            doc.testdata = doc.testdata.replace(
                                '__%s__' % p['name'], p['value'])
                        pr['value'] = unicode(doc.testdata).encode('utf-8')
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('remote-tests('):
                try:
                    fileName = pr['value'].split('):/', 1)[1]
                    projectName = pr['value'].split(
                        'remote-tests(', 1)[1].split('):/', 1)[0]
                except Exception:
                    missingDataset.append(pr['value'])
                    pr['value'] = ''
                else:
                    projectId = 0
                    allPrjs = ProjectsManager.instance().getProjects(user=user)
                    for p in allPrjs:
                        if p['name'] == projectName:
                            projectId = p['project_id']
                            break
                    doc = TestData.DataModel()
                    res = doc.load(absPath="%s/%s/%s" % (RepoTests.instance().testsPath,
                                                         projectId,
                                                         fileName)
                                   )
                    if not res:
                        missingDataset.append(''.join([fileName]))
                        pr['value'] = ''
                    else:
                        if inputs:
                            parametersBis = doc.properties['properties']['inputs-parameters']['parameter']
                        for p in parametersBis:
                            doc.testdata = doc.testdata.replace(
                                '__%s__' % p['name'], p['value'])
                        pr['value'] = unicode(doc.testdata).encode('utf-8')
            else:
                pass
    return missingDataset
