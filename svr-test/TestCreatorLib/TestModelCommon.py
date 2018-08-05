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

import base64
import sys

from Libs import Settings
import Libs.FileModels.TestData as TestData

from ServerRepositories import ( RepoTests )
from ServerEngine import ( ProjectsManager )

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str
        
TS_ENABLED				= "2"
TS_DISABLED				= "0"

IMPORT_PY_LIBS = """#!/usr/bin/python -O
# -*- coding: utf-8 -*-
import sys
import time
import re

"""

IMPORT_INTRO = """
task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )

if sys.version_info > (3,):
	sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a+', 1) 
else:
	sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
"""

IMPORT_TE_LIBS = """
try:
	from Libs import Scheduler
except ImportError as e:
	pass
import TestExecutorLib.TestLoggerXml as TLX
import TestExecutorLib.TestDataStorage as TDS
import TestExecutorLib.TestClientInterface as TCI

from TestExecutorLib.TestExecutorLib import *
import TestExecutorLib.TestPropertiesLib as TestProperties
import TestExecutorLib.TestOperatorsLib as TestOperators
import TestExecutorLib.TestValidatorsLib as TestValidators
import TestExecutorLib.TestExecutorLib as TestExecutorLib
import TestExecutorLib.TestTemplatesLib as TestTemplates
import TestExecutorLib.TestAdapterLib as TestAdapter
import TestExecutorLib.TestManipulatorsLib as TestManipulators
import TestExecutorLib.TestReportingLib as TestReporting

SutAdapter = TestAdapter
import TestExecutorLib.TestLibraryLib as TestLibrary
SutLibrary = TestLibrary

import TestInteropLib as TestInteroperability
"""

CODE_PROBES = """
	__PROBES_ACTIVE__ = []
	__PROBES_RUNNING__ = []
	__PROBES_STARTED__ = []

	def get_active_probes__():
		for pr in  __PROBES__:
			if pr['active'] == 'True':
				__PROBES_ACTIVE__.append(pr)

	def prepare_probes__(component='TESTSUITE'):
		for pr in __PROBES_ACTIVE__:
			if pr['active'] == 'True':
				ret = TCI.instance().cmd( data = {'cmd': CMD_GET_PROBE, 'name': pr['name'], 'task-id': task_id})
				if ret is None:
					raise Exception('Server Error> prepare probes: no response')
				elif ret['body']['cmd']!= CMD_GET_PROBE:
					raise Exception('[prepare_probes__] cmd error')
				if ret['body']['res']:
					__PROBES_RUNNING__.append(pr)
					if component=='TESTSUITE':
						TLX.instance().log_testsuite_trace(message = "probe %s: alive" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTUNIT':
						TLX.instance().log_testunit_trace(message = "probe %s: alive" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTABSTRACT':
						TLX.instance().log_testabstract_trace(message = "probe %s: alive" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTPLAN':
						TLX.instance().log_testplan_trace(message = "probe %s: alive" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					else:
						TLX.instance().log_testglobal_trace(message = "probe %s: alive" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				else:
					if component=='TESTSUITE':
						TLX.instance().log_testsuite_warning(message = "probe %s: unknown" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTUNIT':
						TLX.instance().log_testunit_warning(message = "probe %s: unknown" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTABSTRACT':
						TLX.instance().log_testabstract_warning(message = "probe %s: unknown" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					elif component=='TESTPLAN':
						TLX.instance().log_testplan_warning(message = "probe %s: unknown" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
					else:
						TLX.instance().log_testglobal_warning(message = "probe %s: unknown" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	
	def start_probe__(component='TESTSUITE'):
		for pr in __PROBES_RUNNING__:
			if component=='TESTSUITE':
				TLX.instance().log_testsuite_trace(message = "probe %s: starting..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
			elif component=='TESTUNIT':
				TLX.instance().log_testunit_trace(message = "probe %s: starting..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
			elif component=='TESTABSTRACT':
				TLX.instance().log_testabstract_trace(message = "probe %s: starting..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
			elif component=='TESTPLAN':
				TLX.instance().log_testplan_trace(message = "probe %s: starting..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
			else:
				TLX.instance().log_testglobal_trace(message = "probe %s: starting..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

			ret = TCI.instance().cmd( data = {'cmd': CMD_START_PROBE, 'name': pr['name'], 'replay-id': replay_id, 'args': pr['args'], 'result-path': test_result_path, 'task-id': task_id } )
			if ret is None:
				raise Exception('Server Error>start probe: no response')
			elif ret['body']['cmd']!= CMD_START_PROBE:
				raise Exception('[start_probe__] system error: cmd')

			elif ret['body']['res']['callid'] is None:
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_error( message = "unable to start probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_error( message = "unable to start probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_error( message = "unable to start probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_error( message = "unable to start probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				else:
					TLX.instance().log_testglobal_error( message = "unable to start probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

			elif ret['body']['res']['callid'] == -1 :
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_error( message = "unable to start probe: %s, arguments missing" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_error( message = "unable to start probe: %s, arguments missing" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_error( message = "unable to start probe: %s, arguments missing" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_error( message = "unable to start probe: %s, arguments missing" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				else:
					TLX.instance().log_testglobal_error( message = "unable to start probe: %s, arguments missing" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

			elif ret['body']['res']['callid'] == -10:
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_error( message = "system error, unable to start: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_error( message = "system error, unable to start: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_error( message = "system error, unable to start: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_error( message = "system error, unable to start: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				else:
					TLX.instance().log_testglobal_error( message = "system error, unable to start: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

			else:
				__PROBES_STARTED__.append( (pr, ret['body']['res']['callid']) )
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_trace( message = "probe %s: started" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
					TLX.instance().log_testsuite_trace( message = "probe %s: running..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_trace( message = "probe %s: started" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
					TLX.instance().log_testunit_trace( message = "probe %s: running..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_trace( message = "probe %s: started" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
					TLX.instance().log_testabstract_trace( message = "probe %s: running..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_trace( message = "probe %s: started" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
					TLX.instance().log_testplan_trace( message = "probe %s: running..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
				else:
					TLX.instance().log_testglobal_trace( message = "probe %s: started" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )
					TLX.instance().log_testglobal_trace( message = "probe %s: running..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

	def stop_probe__(component='TESTSUITE'):
		for pr, callid in __PROBES_STARTED__:
			if component=='TESTSUITE':
				TLX.instance().log_testsuite_trace(message = "probe %s: stopping..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			elif component=='TESTUNIT':
				TLX.instance().log_testunit_trace(message = "probe %s: stopping..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			elif component=='TESTABSTRACT':
				TLX.instance().log_testabstract_trace(message = "probe %s: stopping..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			elif component=='TESTPLAN':
				TLX.instance().log_testplan_trace(message = "probe %s: stopping..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			else:
				TLX.instance().log_testglobal_trace(message = "probe %s: stopping..." % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

			ret = TCI.instance().cmd( data = {'cmd': CMD_STOP_PROBE, 'name': pr['name'], 'callid': callid, 'replay-id': replay_id, 'result-path': test_result_path, 'task-id': task_id })
			if ret is None:
				raise Exception('Server Error> stop probe: no response')
			if ret['body']['cmd']!= CMD_STOP_PROBE:
				raise Exception('[stop_probe__] system error: cmd')

			elif ret['body']['res']['callid'] is None:
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_error( message = "unable to stop the probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_error( message = "unable to stop the probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_error( message = "unable to stop the probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_error( message = "unable to stop the probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				else:
					TLX.instance().log_testglobal_error( message = "unable to stop the probe: %s" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			else:
				if component=='TESTSUITE':
					TLX.instance().log_testsuite_trace(message = "probe %s: stopped" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTUNIT':
					TLX.instance().log_testunit_trace(message = "probe %s: stopped" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTABSTRACT':
					TLX.instance().log_testabstract_trace(message = "probe %s: stopped" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				elif component=='TESTPLAN':
					TLX.instance().log_testplan_trace(message = "probe %s: stopped" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
				else:
					TLX.instance().log_testglobal_trace(message = "probe %s: stopped" % pr['name'], component = component, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

"""

TEST_SUMMARY = """

	inputs_str = []
	for i in inputs():
		if i['type'] in ['snapshot-image', 'local-file', 'local-image', 'dataset' ]:
			inputs_str.append( '\\t* %s (%s) = ...binary...' % (i['name'], i['type']) )
		else:
			try:
				val_tmp = str(i['value'])
			except Exception:
				val_tmp = i['value'].encode('utf8')
			inputs_str.append( '\\t* %s (%s) = %s' % ( str(i['name']), str(i['type']), val_tmp ))

	outputs_str = []
	for o in outputs():
		if o['type'] in ['snapshot-image', 'local-file', 'local-image', 'dataset' ]:
			outputs_str.append( '\\t* %s (%s) = ...binary...' % (o['name'], o['type']) )
		else:
			try:
				val_tmp = str(o['value'])
			except Exception:
				val_tmp = o['value'].encode('utf8')
			outputs_str.append( '\\t* %s (%s) = %s' % (str(o['name']), str(o['type']), val_tmp))

	agents_str = []
	for a in agents():
		try:
			val_tmp = str(a['value'])
		except Exception:
			val_tmp = a['value'].encode('utf8')
		agents_str.append( '\\t* %s (%s) = %s' % (str(a['name']), str(a['type']), val_tmp))

	ts_summary = [ 'Description' ]
	ts_summary.append( '\\tAuthor: \\t%s' % description('author') )
	ts_summary.append( '\\tCreation: \\t%s' % description('creation date') )
	ts_summary.append( '\\tRun at: \\t%s' % time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(scriptstart_time) ) )
	ts_summary.append( '\\tPurpose: \\t%s' % description('summary') )
	ts_summary.append( '\\tSUT Adapters: \\t%s' % description('adapters') )
	ts_summary.append( '\\tSUT Libraries: \\t%s' % description('libraries') )
	ts_summary.append( '\\tInputs: \\t\\n%s' % '\\n'.join(inputs_str) )
	ts_summary.append( '\\tOutputs: \\t\\n%s' % '\\n'.join(outputs_str) )
	ts_summary.append( '\\tAgents: \\t\\n%s' % '\\n'.join(agents_str) )
    
	sum_dict = []
	sum_dict.append( ('run at', time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(scriptstart_time) )) )
	sum_dict.append( ('run by', user_) )
	sum_dict.append( ( 'test name', test_name) )
	sum_dict.append( ( 'test path', test_location) )
	sum_dict.append( ( 'project name', projectname_) )
	sum_dict.append( ('adapters', description('adapters')) )
	sum_dict.append( ('libraries',  description('libraries')) )
	tsMgr.setDescription(sum_dict)
"""

TEST_SUMMARY_TG = """
	TLX.instance().log_testglobal_internal(message = '\\n'.join(ts_summary), component = 'TESTGLOBAL', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TP = """
	TLX.instance().log_testplan_internal(message = '\\n'.join(ts_summary), component = 'TESTPLAN', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TS = """
	TLX.instance().log_testsuite_internal(message = '\\n'.join(ts_summary), component = 'TESTSUITE', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TU = """
	TLX.instance().log_testunit_internal(message = '\\n'.join(ts_summary), component = 'TESTUNIT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
"""

TEST_SUMMARY_TA = """
	TLX.instance().log_testabstract_internal(message = '\\n'.join(ts_summary), component = 'TESTABSTRACT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
"""

INPUT_CACHE = """
def cache(key):
    return Cache().get(name=key)
TestProperties.cache = cache
"""

INPUT_CUSTOM = """
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
        trPath = '%s%s' % ( Settings.getDirExec(), 
                            Settings.get( 'Paths', 'testsresults-tmp' ) )
    else:
        trPath = '%s%s' % ( Settings.getDirExec(), 
                            Settings.get( 'Paths', 'testsresults' ) )
    return trPath

def getStaticArgs(envTmp=False):
    """
    """
    te_args = """root = '%s'
tests_result_path = '%s'
controller_ip = '%s'
controller_port = %s
""" % ( 
            Settings.getDirExec(), 
            getTestsPath(envTmp=envTmp),
            Settings.get( 'Bind', 'ip-tsi' ),
            Settings.get( 'Bind', 'port-tsi' )
        )
    return te_args
    
def loadImages(parameters, user=''):
    """
    """
    missingImages = [ ]
    for pr in parameters:
        if pr['type'] == 'remote-image':
            if pr['value'].startswith('undefined:/'):
                dataEncoded = pr['value'].split('undefined:/')[1]
                if dataEncoded:
                    pr['value'] =  base64.b64decode(dataEncoded)
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('local-tests:/'):
                dataEncoded = pr['value'].split('local-tests:/')[1]
                if dataEncoded:
                    pr['value'] =  base64.b64decode(dataEncoded)
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('remote-tests('):
                try:
                    fileName = pr['value'].split('):/', 1)[1]
                    projectName = pr['value'].split('remote-tests(', 1)[1].split('):/', 1)[0]
                except Exception as e:
                    missingImages.append( pr['value'] )
                    pr['value'] = ''
                else:
                    projectId = 0
                    allPrjs = ProjectsManager.instance().getProjects(user=user, b64=False)
                    for p in allPrjs:
                        if p['name'] == projectName:
                            projectId = p['project_id']
                            break

                    absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, projectId, fileName) 
                    try:
                        f = open(absPath, 'rb')
                        pr['value'] = f.read()
                        f.close()
                    except Exception as e:
                        missingImages.append( ''.join( [fileName] ) )
            else:
                pass
    return missingImages

def loadDataset(parameters, inputs=True, user=''):
    """
    """
    missingDataset = [ ]
    for pr in parameters:
        if pr['type'] == 'dataset':
            if pr['value'].startswith('undefined:/'):
                dataEncoded = pr['value'].split('undefined:/')[1]
                if dataEncoded:
                    dataDecoded =  base64.b64decode(dataEncoded)
                    doc = TestData.DataModel()
                    res = doc.load(rawData=dataDecoded)
                    if not res: pr['value'] = ''
                    else: 
                        if inputs:
                            parametersBis = doc.properties['properties']['inputs-parameters']['parameter']
                        else:
                            parametersBis = doc.properties['properties']['outputs-parameters']['parameter']
                        for p in parametersBis:
                            doc.testdata = doc.testdata.replace('__%s__' % p['name'], p['value'])
                        pr['value'] = unicode(doc.testdata).encode('utf-8')
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('local-tests:/'):
                dataEncoded = pr['value'].split('local-tests:/')[1]
                if dataEncoded:
                    dataDecoded =  base64.b64decode(dataEncoded)
                    doc = TestData.DataModel()
                    res = doc.load(rawData=dataDecoded)
                    if not res: pr['value'] = ''
                    else: 
                        if inputs:
                            parametersBis = doc.properties['properties']['inputs-parameters']['parameter']
                        else:
                            parametersBis = doc.properties['properties']['outputs-parameters']['parameter']
                        for p in parametersBis:
                            doc.testdata = doc.testdata.replace('__%s__' % p['name'], p['value'])
                        pr['value'] = unicode(doc.testdata).encode('utf-8')
                else:
                    pr['value'] = ''
            elif pr['value'].startswith('remote-tests('):
                try:
                    fileName = pr['value'].split('):/', 1)[1]
                    projectName = pr['value'].split('remote-tests(', 1)[1].split('):/', 1)[0]
                except Exception as e:
                    missingDataset.append( pr['value'] )
                    pr['value'] = ''
                else:
                    projectId = 0
                    allPrjs = ProjectsManager.instance().getProjects(user=user, b64=False)
                    for p in allPrjs:
                        if p['name'] == projectName:
                            projectId = p['project_id']
                            break
                    doc = TestData.DataModel()
                    res = doc.load( absPath = "%s/%s/%s" % (RepoTests.instance().testsPath, projectId, fileName) )
                    if not res:		
                        missingDataset.append( ''.join( [fileName] ) )
                        pr['value'] = ''
                    else:
                        if inputs:
                            parametersBis = doc.properties['properties']['inputs-parameters']['parameter']
                        else:
                            parametersBis = doc.properties['properties']['outputs-parameters']['parameter']
                        for p in parametersBis:
                            doc.testdata = doc.testdata.replace('__%s__' % p['name'], p['value'])
                        pr['value'] = unicode(doc.testdata).encode('utf-8')
            else:
                pass
    return missingDataset