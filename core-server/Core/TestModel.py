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

# /!\ WARNING /!\
# Don't replace tab to space on python code generated for test
# the test is not compliant with python recommandation
# /!\ WARNING /!\

import os
import base64

from Libs import Settings
import Libs.FileModels.TestData as TestData

try:
    import RepoManager
    import RepoTests
    import RepoAdapters
    import RepoLibraries
    import ProjectsManager
    import Common 
except ImportError: # support python 3
    from . import RepoManager
    from . import RepoTests
    from . import RepoAdapters
    from . import RepoLibraries
    from . import ProjectsManager
    from . import Common 
    
TS_ENABLED				= "2"
TS_DISABLED				= "0"

indent = Common.indent

def getTestsPath(envTmp=False):
    """
    Get the path of all tests result

    @return:
    @rtype: string
    """
    if envTmp:
        trPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults-tmp' ) )
    else:
        trPath = '%s%s' % ( Settings.getDirExec(), Settings.get( 'Paths', 'testsresults' ) )
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

IMPORT_PY_LIBS = """#!/usr/bin/python -O
# -*- coding: utf-8 -*-
import sys
import time
import re

"""

IMPORT_TE_LIBS = """
try:
	from Libs import Scheduler
except ImportError, e:
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
	def custom(line):
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

		inputs = re.findall("\[!INPUT:[\w-]+\:\]", new_line)
		for c in inputs:
			inputs_args = c.split(":")[1:-1]
			v = input(inputs_args[0])
			new_line = new_line.replace(c, "%s" % v, 1)
            
		captures = re.findall("\[!CAPTURE:[\w-]+(?:\:.*?)?\:\]", new_line)
		for c in captures:
			sub = c[2:-2]
			captures_args = sub.split(":", 2)[1:]
			if len(captures_args) == 2:
				new_line = new_line.replace(c, "(?P<%s>%s)" % (captures_args[0], captures_args[1]), 1)
			else:
				new_line = new_line.replace(c, "(?P<%s>.*)" % captures_args[0], 1)
		return new_line
	TestProperties.custom = custom
"""

def getLocalAdapters ( path ):
    """
    Get all adapters available in path directory
    Deprecated

    @param path:
    @type path:

    @return:
    @rtype: list
    """
    adapters = os.listdir(path)
    ret = []

    for adp in adapters:
        if adp.endswith('.py'): # remove extension py
            modul = adp[:-3]
            ret.append(modul)
        else:
            if os.path.isdir( "%s/%s/" % (path,adp) ):
                ret.append(adp) # directory
    return ret

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

def createTestDesign(   dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                        projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                         testLocation='' ):
    """
    Creates and returns the test executable for design only

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    if 'testglobal' in dataTest:
        return createTestDesignForTg( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary,
                                        defaultAdapter, userId, projectId, parametersShared, stepByStep, breakpoint, testId,
                                            runningAgents, runningProbes, testLocation)
    else:
        if 'testplan' in dataTest:
            return createTestDesignForTp( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary,
                                            defaultAdapter, userId, projectId, parametersShared, stepByStep, breakpoint, testId,
                                                runningAgents, runningProbes, testLocation)
        else:
            if 'testunit' in dataTest:
                return createTestDesignForTu( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                                defaultAdapter, userId, projectId, parametersShared, stepByStep, breakpoint, testId,
                                                    runningAgents, runningProbes, testLocation)
            elif 'testabstract' in dataTest:
                return createTestDesignForTa( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                                defaultAdapter, userId, projectId, parametersShared, stepByStep, breakpoint, testId,
                                                    runningAgents, runningProbes, testLocation)
            else:
                return createTestDesignForTs( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                                defaultAdapter, userId, projectId, parametersShared, stepByStep, breakpoint, testId,
                                                    runningAgents, runningProbes, testLocation)

def createTestDesignForTg(dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            testLocation='' ):
    """
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    testglobal = dataTest['testglobal']

    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs(envTmp=True) )

    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
ParametersHandler = TestProperties.TestPlanParameters()
scriptstart_time = time.time()

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_=userid_)

TestExecutorLib.dontExecute()
tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTp(name=test_name)
tsMgr.setMainDescriptions(descriptions=%s)

try:
""" % descriptions)
    te.append( """	ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """	ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """	ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """	ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """	ParametersHandler.addParametersShared( parameters=%s)\n""" % parametersShared )
    te.append( """	ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """	ParametersHandler.addRunningProbes( probes=%s)\n""" % runningProbes )
    te.append( """	__PROBES__ = %s""" % probes )
    te.append( """

	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def output(name):
		return ParametersHandler.parameterOut(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setOutput(name, value):
		return ParametersHandler.setParameterOut(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agent(name):
		return ParametersHandler.agent(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
        
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def outputs():
		return ParametersHandler.outputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agents():
		return ParametersHandler.agents(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)

	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")

    te.append(INPUT_CUSTOM)
    te.append(INPUT_CACHE)
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )
    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    te.append( TEST_SUMMARY )

    if not len(testglobal):
        te.append("""
	pass
""")
    for ts in testglobal:
        isTs=True
        isTa=True
        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
            if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                isTs=False
                isTa=True
        if ts['enable'] == TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            te.append(indent("""
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            if isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            te.append(indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )

            te.append("\n")
            te.append("\n")
            te.append("\n")
            te.append("\n")

            te.append( indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("class TESTCASE(TestCase):", nbTab = ts['depth'] + 2 ))
                te.append("\n")
                te.append(indent(ts['src'], nbTab = ts['depth'] + 3 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src2'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            te.append(indent("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )
		return_code = RETURN_CODE_TE_ERROR""", nbTab = ts['depth'] - 1) )
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	return_code = RETURN_CODE_TE_ERROR

TLX.instance().setMainId()

tsMgr.saveDesigns()
tsMgr.saveDesignsXml()

TLX.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestDesignForTp(dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            testLocation='' ):
    """
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    testplan = dataTest['testplan']

    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs(envTmp=True) )

    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
ParametersHandler = TestProperties.TestPlanParameters()
scriptstart_time = time.time()

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_=userid_)

TestExecutorLib.dontExecute()
tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTp(name=test_name)

tsMgr.setMainDescriptions(descriptions=%s)

try:
""" % descriptions)
    te.append( """	ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """	ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """	ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """	ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """	ParametersHandler.addParametersShared( parameters=%s)\n""" % parametersShared )
    te.append( """	ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """	ParametersHandler.addRunningProbes( probes=%s)\n""" % runningProbes )
    te.append( """	__PROBES__ = %s""" % probes )
    te.append( """

	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def output(name):
		return ParametersHandler.parameterOut(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setOutput(name, value):
		return ParametersHandler.setParameterOut(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agent(name):
		return ParametersHandler.agent(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
        
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def outputs():
		return ParametersHandler.outputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agents():
		return ParametersHandler.agents(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)

	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")

    te.append(INPUT_CUSTOM)
    te.append(INPUT_CACHE)

    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )
    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    te.append( TEST_SUMMARY )

    if not len(testplan):
        te.append("""
	pass
""")
    for ts in testplan:
        isTs=True
        isTa = False
        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
            if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                isTs=False
                isTa=True
        if ts['enable'] == TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            te.append(indent("""
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            if isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            te.append(indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )

            te.append("\n")
            te.append("\n")
            te.append("\n")
            te.append("\n")

            te.append( indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("class TESTCASE(TestCase):", nbTab = ts['depth'] + 2 ))
                te.append("\n")
                te.append(indent(ts['src'], nbTab = ts['depth'] + 3 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src2'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            te.append(indent("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )
		return_code = RETURN_CODE_TE_ERROR""", nbTab = ts['depth'] - 1) )
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	return_code = RETURN_CODE_TE_ERROR

TLX.instance().setMainId()

tsMgr.saveDesigns()
tsMgr.saveDesignsXml()

TLX.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestDesignForTs(dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            testLocation='' ):
    """
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']
    if 'src-exec' in dataTest:
        srcExec = dataTest['src-exec']

    if 'testunit' in dataTest:
        srcTest = "class TESTCASE_01(TestCase):\t%s"% indent(srcTest)
        srcExec = "TESTCASE_01(suffix=None, testName='%s' % description('name')).execute()"

    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs(envTmp=True) )

    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

scriptstart_time = time.time()
RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13
return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_)

TestExecutorLib.dontExecute()
tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTs(name=test_name, isEnabled=True, testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

try:
""")
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility
	def description(name):
		return TestProperties.Descriptions().get(name=name)
""")

    te.append(INPUT_CUSTOM)
    te.append(INPUT_CACHE)

    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )
    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    te.append( TEST_SUMMARY ) 
    te.append("""
	# !! test injection
""")
    te.append(indent(srcTest))
    te.append("\n")
    te.append("""
	# !! test exec injection
""")
    te.append(indent(srcExec))
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	return_code = RETURN_CODE_TE_ERROR

tsMgr.saveDesigns()
tsMgr.saveDesignsXml()

TLX.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')


def createTestDesignForTu(dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            testLocation='' ):
    """
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']

    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs(envTmp=True) )

    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13
scriptstart_time = time.time()
return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_)

TestExecutorLib.dontExecute()
tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTu(name=test_name, isEnabled=True, testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

try:
""")
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility
	def description(name):
		return TestProperties.Descriptions().get(name=name)
""")

    te.append(INPUT_CUSTOM)
    te.append(INPUT_CACHE)

    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )
    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    te.append( TEST_SUMMARY ) 
    te.append("""
	# !! test injection
	class TESTCASE(TestCase):
""")
    te.append(indent(srcTest, nbTab=2))
    te.append("\n")
    te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	return_code = RETURN_CODE_TE_ERROR

tsMgr.saveDesigns()
tsMgr.saveDesignsXml()

TLX.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestDesignForTa(dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            testLocation='' ):
    """
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']

    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs(envTmp=True) )

    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]
result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13
scriptstart_time = time.time()
return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_)

TestExecutorLib.dontExecute()
tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTa(name=test_name, isEnabled=True, testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

try:
""")
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility
	def description(name):
		return TestProperties.Descriptions().get(name=name)
	
""")

    te.append(INPUT_CUSTOM)
    te.append(INPUT_CACHE)

    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )
    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    te.append( TEST_SUMMARY ) 
    te.append("""
	# !! test injection
	class TESTCASE(TestCase):
""")
    te.append(indent(srcTest, nbTab=2))
    te.append("\n")
    te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	return_code = RETURN_CODE_TE_ERROR

tsMgr.saveDesigns()
tsMgr.saveDesignsXml()

TLX.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestExecutable( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', defaultAdapter='', userId=0,
                            projectId=0, subTEs=1, parametersShared=[], stepByStep=False, breakpoint=False, testId=0, runningAgents=[], runningProbes=[],
                            channelId=False, testLocation=''):
    """
    Creates and returns the test executable: testplan or testsuite

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    if 'testglobal' in dataTest:
        return createTestGlobal( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                    defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                        runningAgents, runningProbes, channelId, testLocation)
    else:
        if 'testplan' in dataTest:
            return createTestPlan( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                    defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                        runningAgents, runningProbes, channelId, testLocation)
        else:
            if 'testunit' in dataTest:
                return createTestUnit( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                        defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                            runningAgents, runningProbes, channelId, testLocation)
            elif 'testabstract' in dataTest:
                return createTestAbstract( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                        defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                            runningAgents, runningProbes, channelId, testLocation)
            else:
                return createTestSuite( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary,
                                        defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                            runningAgents, runningProbes, channelId, testLocation)

# -------- Events test global -----------

# > log_script_started
#	> log_testglobal_started
#	> log_testglobal_info
#	> ( log_testglobal_trace )
#	> ( log_testglobal_warning )
#	> ( log_testglobal_error )
#		> log_testsuite_started
#			> log_testsuite_info
#			> ( log_testsuite_error )
#				> log_testcase_started
#					> log_testcase_info
#					> ( log_testcase_error )
#					> log_testcase_info
#				> log_testcase_stopped
#				....
#			> log_testsuite_info
#		> log_testsuite_stopped
#		...
#	> (log_testglobal_error)
#	> log_testglobal_info
#	> log_testglobal_stopped
# > log_script_stopped

# -------- Events test plan -----------

# > log_script_started
#	> log_testplan_started
#	> log_testplan_info
#	> ( log_testplan_trace )
#	> ( log_testplan_warning )
#	> ( log_testplan_error )
#		> log_testsuite_started
#			> log_testsuite_info
#			> ( log_testsuite_error )
#				> log_testcase_started
#					> log_testcase_info
#					> ( log_testcase_error )
#					> log_testcase_info
#				> log_testcase_stopped
#				....
#			> log_testsuite_info
#		> log_testsuite_stopped
#		...
#	> (log_testplan_error)
#	> log_testplan_info
#	> log_testplan_stopped
# > log_script_stopped

# -------- Events test suite / testcase -----------

# > log_script_started
#	> log_testsuite_started
#		> log_testsuite_info
#		> ( log_testsuite_trace )
#		> ( log_testsuite_warning )
#		> ( log_testsuite_error )
#			> log_testcase_started
#				> log_testcase_info
#				> ( log_testcase_error )
#				> log_testcase_info
#			> log_testcase_stopped
#			....
#		> ( log_testsuite_error )
#		> log_testsuite_info
#	> log_testsuite_stopped
# > log_script_stopped

def createTestGlobal ( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='', 
                        defaultAdapter='', userId=0, projectId=0, subTEs=1, parametersShared=[], stepByStep=False, breakpoint=False, testId=0,
                        runningAgents=[], runningProbes=[], channelId=False, testLocation=''):
    """
    Creates and returns a test global executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    testglobal = dataTest['testglobal']

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs() )

    te.append( """channelid_ = %s\n""" % channelId )
    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestAdapter.setMainPath(sutPath=root)

Scheduler.initialize()
TestProperties.initialize()
ParametersHandler = TestProperties.instance()

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

class Cleanup(Exception): pass

CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK
return_message = None


TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_=userid_, channelid_=channelid_)

def initialize_te():
	TCI.initialize( address =  (controller_ip, int(controller_port) ), name = "%s.%s" %(log_filename, task_id) )

def finalize_te (return_code):
	TCI.finalize()

initialize_te()

tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
tsMgr.setTestGlobal()
""")
    te.append("""tsMgr.setNbTests(nb=%s)""" % len(testglobal))
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append( """
ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """ParametersHandler.addParametersShared( parameters=%s )\n""" % parametersShared )
    te.append( """ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """ParametersHandler.addRunningProbes( probes=%s)\n""" % runningProbes )
    te.append("""
tsMgr.newTp(name=test_name, dataInputs=ParametersHandler.getDataFromMain(parametersId=TLX.instance().mainScriptId), sutInputs=ParametersHandler.getSutFromMain(parametersId=TLX.instance().mainScriptId), summary=ParametersHandler.getDescrFromMain(name="summary", tpId=TLX.instance().mainScriptId), startedAt=time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(time.time()) ), dataOutputs=ParametersHandler.getDataOutFromMain(parametersId=TLX.instance().mainScriptId), sutOutputs=ParametersHandler.getSutOutFromMain(parametersId=TLX.instance().mainScriptId))
""")
    te.append("""
tsMgr.setMainDescriptions(descriptions=%s)
""" % descriptions)
    te.append("""
adpsMgr = TestExecutorLib.getAdpsMgr()
adpsMgrALL = TestExecutorLib.getAdpsMgrALL()

scriptstart_time = time.time()
TLX.instance().log_script_started()
testglobalstart_time = time.time()
TLX.instance().log_testglobal_started()
TLX.instance().log_testglobal_info(message = 'BEGIN', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)

try:
""")
    te.append( CODE_PROBES ) 
    te.append( """	__PROBES__ = %s""" % probes )
    te.append( """

	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def output(name):
		return ParametersHandler.parameterOut(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setOutput(name, value):
		return ParametersHandler.setParameterOut(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agent(name):
		return ParametersHandler.agent(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
 
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def outputs():
		return ParametersHandler.outputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agents():
		return ParametersHandler.agents(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
        
	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")
    te.append( TEST_SUMMARY )
    te.append( TEST_SUMMARY_TG ) 
    for ds in missingDataset:
        te.append("""
	TLX.instance().log_testglobal_warning(message = 'Dataset %s is missing in inputs parameters.', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)
    for ds in missingDatasetOut:
        te.append("""
	TLX.instance().log_testglobal_warning(message = 'Dataset %s is missing in outputs parameters.', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testglobal_internal(message = 'Loading modules...\\nDefault[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTGLOBAL', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if not withoutProbes:
        te.append("""
	get_active_probes__()
	prepare_probes__(component='TESTGLOBAL')
	start_probe__(component='TESTGLOBAL')
""")
    else:
        te.append("""
	TLX.instance().log_testglobal_warning(message = "Probes are not activated with this run.", component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""")
    if not len(testglobal):
        te.append("""
	pass
""")
    i = 0
    for ts in testglobal:

        # prevent error with old testfile, this key is new only since the version 17
        if "parent-condition" not in ts: ts['parent-condition'] = "0"
        
        isTs=True
        isTa=False
        isTpFromTg=False
        isTp=False
        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
            if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                isTs=False
                isTa=True
            if ts['extension'] == RepoManager.TEST_PLAN_EXT:
                isTpFromTg = True
            if ts['extension'] == RepoManager.TEST_PLAN_EXT and "separator" in ts:
                isTp = True
                te.append( indent("""
TLX.instance().setMainTpId(tpId='%s-0')
if not TLX.instance().allPassed(tsId = "%s-0"):
	TLX.instance().setMainTpResult(tpId='%s-0')
else:
    """ % (ts['id'], ts['parent'], ts['id']), nbTab = ts['depth'] ) )
                if ts['separator'] == 'terminated':
                    te.append( indent("""
	testplanstop_time = time.time()
	testplanduration = testplanstop_time - testplanstart_time
	tsMgr.addSubTestPlanDuration(duration=testplanduration)
	tsMgr.newStopTpInTg(name="%s", nameAlias="%s")
	TLX.instance().log_testplan_separator_terminated(tid='%s', testname='%s', duration=testplanduration, alias='%s')
	""" % ( ts['testname'], ts['alias'], ts['id'], ts['testname'], ts['alias']), nbTab = ts['depth'] ) )
                else:
                    te.append( indent("""
	ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s) 
	tsMgr.newStartTpInTg(name="%s", nameAlias="%s", summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath='%s', testProject='%s')
	testplanstart_time = time.time()
	TLX.instance().log_testplan_separator(tid='%s', testname='%s', alias='%s')
	""" % (  ts['properties']['descriptions']['description'], ts['testname'], ts['alias'], 
             ts["testpath"], ts["testproject"], 
             ts['id'], ts['testname'], ts['alias']), nbTab = ts['depth'] ) )
        
        if ts['enable'] != TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            parentId = "%s-0" % ts['parent']
            if 'tpid' in ts: parentId = "%s-0-%s" % (ts['tpid'], ts['parent'])
            if isTp:
                pass
            elif isTpFromTg:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=0, isTpFromTg=True, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")""" % (ts['path'], ts['alias'], ts["testpath"], ts["testproject"]) , nbTab = ts['depth'] ) )
            elif isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )

        if ts['enable'] == TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(indent("""
	testsuitestart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            elif isTa:
                te.append(indent("""
	testabstractstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            else:
                te.append(indent("""
	testunitstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            parentId = "%s-0" % ts['parent']
            if 'tpid' in ts:
                parentId = "%s-0-%s" % (ts['tpid'], ts['parent'])
                
            # new in v17
            notCond = ""
            if ts['parent-condition'] == "1": 
                notCond = "not"
            # end of new
            
            if isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            
            tstId = "%s-0" % ts['id']
            if 'tpid' in ts:
                tstId = "%s-0-%s" % (ts['tpid'], ts['id'])
            te.append(indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], tstId ), nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testsuite_started(tid='%s', alias='%s')
TLX.instance().log_testsuite_info(message = 'BEGIN', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            elif isTa:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testabstract_started(tid='%s', alias='%s')
TLX.instance().log_testabstract_info(message = 'BEGIN', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'],ts['alias']), nbTab = ts['depth']  + 2 ) )
            else:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testunit_started(tid='%s', alias='%s')
TLX.instance().log_testunit_info(message = 'BEGIN', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'],ts['alias']), nbTab = ts['depth']  + 2 ) )

            for dsTs in missingDatasetTs:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for dsTs in missingDatasetTsOut:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            for imgTs in missingImagesTs:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for imgTs in missingImagesTsOut:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            te.append( indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """tsMgr.addSummary(summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( indent( """tsMgr.addInputs(dataInputs=ParametersHandler.data(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutInputs=ParametersHandler.sut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( indent( """tsMgr.addOutputs(dataOutputs=ParametersHandler.dataOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutOutputs=ParametersHandler.sutOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            if isTs:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src2'], nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            if isTs:
                te.append(indent("""
TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testsuitestop_time = time.time()
testsuiteduration = testsuitestop_time - testsuitestart_time
TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testsuiteduration)""", nbTab = ts['depth'] + 2 ) )
            elif isTa:
                te.append(indent("""
TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testabstractstop_time = time.time()
testabstractduration = testabstractstop_time - testabstractstart_time
TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testabstractduration)""", nbTab = ts['depth'] + 2 ) )
            else:
                te.append(indent("""
TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testunitstop_time = time.time()
testunitduration = testunitstop_time - testunitstart_time
TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testunitduration)""", nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
			TLX.instance().error(return_message)
			TLX.instance().log_testsuite_error(return_message, component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)

		testsuitestop_time = time.time()
		testsuiteduration = testsuitestop_time - testsuitestart_time
		TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testsuiteduration)
        
		if isinstance(e, ForceStopException): raise ForceStopException(e)""", nbTab = ts['depth'] -1 ) )
            elif isTa:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
			TLX.instance().error(return_message)
			TLX.instance().log_testabstract_error(return_message, component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)

		testabstractstop_time = time.time()
		testabstractduration = testabstractstop_time - testabstractstart_time
		TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testabstractduration)
        
		if isinstance(e, ForceStopException): raise ForceStopException(e)""", nbTab = ts['depth'] - 1) )
            else:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
			TLX.instance().error(return_message)
			TLX.instance().log_testunit_error(return_message, component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)

		testunitstop_time = time.time()
		testunitduration = testunitstop_time - testunitstart_time
		TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testunitduration)
        
		if isinstance(e, ForceStopException): raise ForceStopException(e)""", nbTab = ts['depth'] - 1) )
            i += 1
    te.append("""
except Exception as e:
	if isinstance(e, ForceStopException) and tsMgr.isTestPlanInTestGlobal():
		testplanstop_time = time.time()
		testplanduration = testplanstop_time - testplanstart_time
		tsMgr.addSubTestPlanDuration(duration=testplanduration)
		tsMgr.newStopTpInTg(name="aborted by force")
        
	TLX.instance().setMainId()
    
	if not isinstance(e, ForceStopException):
		return_code = RETURN_CODE_TE_ERROR
		return_message = "ERR_TE_500: %s" % str( e )
        
		TLX.instance().error(return_message)
		TLX.instance().log_testglobal_error(return_message, component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

tcMgr.endingAll()

TLX.instance().setMainId()

try:
""" )
    if not withoutProbes:
        te.append("""
	stop_probe__(component='TESTGLOBAL')
""")
    else:
        te.append("""
	pass
""")
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	TLX.instance().log_testglobal_error( message = str(e), component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

for adpId, adp in adpsMgr.getAdps().items():
	try:
		adp.onReset()
	except Exception as e:
		TLX.instance().log_testglobal_error( "shared adapter: %s" % str(e), 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	adp.stop()
	adp.join()

TLX.instance().log_testglobal_info(message = 'END', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testglobalstop_time = time.time()
testglobalduration = testglobalstop_time - testglobalstart_time
TLX.instance().log_testglobal_stopped(result=tsMgr.computeResults(), duration=testglobalduration, nbTs=tsMgr.getNbTs(), nbTu=tsMgr.getNbTu(), nbTc=tsMgr.getNbTc(), prjId=projectid_ )
tsMgr.addTestPlanDuration(duration=testglobalduration)

scriptstop_time = time.time()
scriptduration = scriptstop_time - scriptstart_time
TLX.instance().log_script_stopped(duration=scriptduration, finalverdict=tsMgr.computeResults(), prjId=projectid_)
tsMgr.addScriptDuration(duration=scriptduration)

tsMgr.saveToCsv()
tsMgr.saveBasicReports(stoppedAt=scriptstop_time)
tsMgr.saveReports(stoppedAt=scriptstop_time)
tsMgr.saveDesigns()

tsMgr.saveDesignsXml()
tsMgr.saveReportsXml()
tsMgr.saveVerdictToXml()

# reset all adapters and libraries, just to be sure!
for adpId, adp in adpsMgrALL.getAdps().items():
    try:
        adp.onReset()
        adp.stop()
        adp.join()
    except Exception as e:
        pass

try:
	finalize_te(return_code)
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )

TLX.finalize()
Scheduler.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestPlan ( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='',
                        defaultAdapter='', userId=0, projectId=0, subTEs=1, parametersShared=[], stepByStep=False,
                        breakpoint=False, testId=0, runningAgents=[], runningProbes=[], channelId=False, testLocation='' ):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    testplan = dataTest['testplan']

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs() )

    te.append( """channelid_ = %s\n""" % channelId )
    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1]
test_id = sys.argv[2]
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestAdapter.setMainPath(sutPath=root)

Scheduler.initialize()
TestProperties.initialize()
ParametersHandler = TestProperties.instance()

class Cleanup(Exception): pass

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK
return_message = None


TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_=userid_, channelid_=channelid_)

def initialize_te():
	TCI.initialize( address =  (controller_ip, int(controller_port) ), name = "%s.%s" %(log_filename, task_id) )

def finalize_te (return_code):
	TCI.finalize()

initialize_te()

tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""tsMgr.setNbTests(nb=%s)"""% len(testplan) )
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep,breakpoint,testId))
    te.append( """
ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """ParametersHandler.addParametersShared( parameters=%s )\n""" % parametersShared )
    te.append( """ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """ParametersHandler.addRunningProbes( probes=%s)\n""" % runningProbes )
    te.append("""
tsMgr.newTp(name=test_name, dataInputs=ParametersHandler.getDataFromMain(parametersId=TLX.instance().mainScriptId), sutInputs=ParametersHandler.getSutFromMain(parametersId=TLX.instance().mainScriptId), summary=ParametersHandler.getDescrFromMain(name="summary", tpId=TLX.instance().mainScriptId), startedAt=time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(time.time()) ), dataOutputs=ParametersHandler.getDataOutFromMain(parametersId=TLX.instance().mainScriptId), sutOutputs=ParametersHandler.getSutOutFromMain(parametersId=TLX.instance().mainScriptId))
""")
    te.append("""
tsMgr.setMainDescriptions(descriptions=%s)
""" % descriptions)
    te.append("""
adpsMgr = TestExecutorLib.getAdpsMgr()
adpsMgrALL = TestExecutorLib.getAdpsMgrALL()

scriptstart_time = time.time()
TLX.instance().log_script_started()
testplanstart_time = time.time()
TLX.instance().log_testplan_started()
TLX.instance().log_testplan_info(message = 'BEGIN', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)

try:
""")
    te.append( CODE_PROBES ) 
    te.append( """	__PROBES__ = %s""" % probes )
    te.append( """

	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def output(name):
		return ParametersHandler.parameterOut(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setOutput(name, value):
		return ParametersHandler.setParameterOut(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agent(name):
		return ParametersHandler.agent(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
 
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def outputs():
		return ParametersHandler.outputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def agents():
		return ParametersHandler.agents(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
        
	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")

    te.append( TEST_SUMMARY )
    te.append( TEST_SUMMARY_TP ) 
    for ds in missingDataset:
        te.append("""
	TLX.instance().log_testplan_warning(message = 'Dataset %s is missing in inputs parameters.', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)
    for ds in missingDatasetOut:
        te.append("""
	TLX.instance().log_testplan_warning(message = 'Dataset %s is missing in outputs parameters.', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testplan_internal(message = 'Loading modules...\\nDefault[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTPLAN', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if not withoutProbes:
        te.append("""
	get_active_probes__()
	prepare_probes__(component='TESTPLAN')
	start_probe__(component='TESTPLAN')
""")
    else:
        te.append("""
	TLX.instance().log_testplan_warning(message = "Probes are not activated with this run.", component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""")

    if not len(testplan):
        te.append("""
	pass
""")
    i = 0
    for ts in testplan:
        isTs=True
        isTa=False
        
        # prevent error with old testfile, this key is new only since the version 17
        if "parent-condition" not in ts: ts['parent-condition'] = "0"
        
        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
            if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                isTs=False
                isTa=True
                
        if ts['enable'] != TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth']  ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )

        if ts['enable'] == TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(indent("""
	testsuitestart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            elif isTa:
                te.append(indent("""
	testabstractstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            else:
                te.append(indent("""
	testunitstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)
            
            # new in v17
            notCond = ""
            if ts['parent-condition'] == "1": 
                notCond = "not"
            # end of new
            
            if isTs:
                te.append(indent("""
tsMgr.newTs(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(indent("""
tsMgr.newTa(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(indent("""
tsMgr.newTu(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            te.append(indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testsuite_started(tid='%s', alias='%s')
TLX.instance().log_testsuite_info(message = 'BEGIN', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            elif isTa:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testabstract_started(tid='%s', alias='%s')
TLX.instance().log_testabstract_info(message = 'BEGIN', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            else:
                te.append( indent("""
tsMgr.isTestStarted()
TLX.instance().log_testunit_started(tid='%s', alias='%s')
TLX.instance().log_testunit_info(message = 'BEGIN', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )

            for dsTs in missingDatasetTs:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for dsTs in missingDatasetTsOut:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            for imgTs in missingImagesTs:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for imgTs in missingImagesTsOut:
                if isTs:
                    te.append( indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            te.append( indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( indent( """tsMgr.addSummary(summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( indent( """tsMgr.addInputs(dataInputs=ParametersHandler.data(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutInputs=ParametersHandler.sut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( indent( """tsMgr.addOutputs(dataOutputs=ParametersHandler.dataOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutOutputs=ParametersHandler.sutOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            if isTs:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(indent(ts['src2'], nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            else:
                te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            if isTs:
                te.append(indent("""
TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testsuitestop_time = time.time()
testsuiteduration = testsuitestop_time - testsuitestart_time
TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testsuiteduration)""", nbTab = ts['depth'] + 2 ) )
            elif isTa:
                te.append(indent("""
TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testabstractstop_time = time.time()
testabstractduration = testabstractstop_time - testabstractstart_time
TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testabstractduration)""", nbTab = ts['depth'] + 2 ) )
            else:
                te.append(indent("""
TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testunitstop_time = time.time()
testunitduration = testunitstop_time - testunitstart_time
TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testunitduration)""", nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
        
			TLX.instance().error(return_message)
			TLX.instance().log_testsuite_error(return_message, component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
		testsuitestop_time = time.time()
		testsuiteduration = testsuitestop_time - testsuitestart_time
		TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testsuiteduration)
        
		if isinstance(e, ForceStopException): raise ForceTerminateTestException(e)""", nbTab = ts['depth'] -1 ) )
            elif isTa:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
        
			TLX.instance().error(return_message)
			TLX.instance().log_testabstract_error(return_message, component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
		testabstractstop_time = time.time()
		testabstractduration = testabstractstop_time - testabstractstart_time
		TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testabstractduration)
        
		if isinstance(e, ForceStopException): raise ForceTerminateTestException(e)""", nbTab = ts['depth'] - 1) )
            else:
                te.append(indent("""
	except Exception as e:
		if not isinstance(e, ForceStopException):
			return_message = "ERR_TE_000: %s" % str( e )
			return_code = RETURN_CODE_TE_ERROR
            
			TLX.instance().error(return_message)
			TLX.instance().log_testunit_error(return_message, component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
			TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
		testunitstop_time = time.time()
		testunitduration = testunitstop_time - testunitstart_time
		TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
		tsMgr.addTestDuration(duration=testunitduration)
        
		if isinstance(e, ForceStopException): raise ForceTerminateTestException(e)""", nbTab = ts['depth'] - 1) )
            i += 1
    te.append("""
except Exception as e:
	TLX.instance().setMainId()
    
	if not isinstance(e, ForceTerminateTestException):
		return_code = RETURN_CODE_TE_ERROR
		return_message = "ERR_TE_500 2: %s" % type( e )

		TLX.instance().error(return_message)
		TLX.instance().log_testplan_error(message=return_message, component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

tcMgr.endingAll()

TLX.instance().setMainId()

try:
""")
    if not withoutProbes:
        te.append("""
	stop_probe__(component='TESTPLAN')
""")
    else:
        te.append("""
	pass
""")
    te.append("""
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	TLX.instance().log_testplan_error( message = str(e), component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

for adpId, adp in adpsMgr.getAdps().items():
	try:
		adp.onReset()
	except Exception as e:
		TLX.instance().log_testplan_error( "shared adapter: %s" % str(e), 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	adp.stop()
	adp.join()
    
TLX.instance().log_testplan_info(message = 'END', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testplanstop_time = time.time()
testplanduration = testplanstop_time - testplanstart_time
TLX.instance().log_testplan_stopped(result=tsMgr.computeResults(), duration=testplanduration, nbTs=tsMgr.getNbTs(), nbTu=tsMgr.getNbTu(), nbTc=tsMgr.getNbTc(), prjId=projectid_ )
tsMgr.addTestPlanDuration(duration=testplanduration)

scriptstop_time = time.time()
scriptduration = scriptstop_time - scriptstart_time
TLX.instance().log_script_stopped(duration=scriptduration, finalverdict=tsMgr.computeResults(), prjId=projectid_)
tsMgr.addScriptDuration(duration=scriptduration)

tsMgr.saveToCsv()
tsMgr.saveBasicReports(stoppedAt=scriptstop_time)
tsMgr.saveReports(stoppedAt=scriptstop_time)
tsMgr.saveDesigns()

tsMgr.saveDesignsXml()
tsMgr.saveReportsXml()
tsMgr.saveVerdictToXml()

# reset all adapters and libraries, just to be sure!
for adpId, adp in adpsMgrALL.getAdps().items():
    try:
        adp.onReset()
        adp.stop()
        adp.join()
    except Exception as e:
        pass

try:
	finalize_te(return_code)
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )

TLX.finalize()
Scheduler.finalize()
sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestSuite (	dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='',
                            defaultAdapter='', userId=0, projectId=0, subTEs=1, parametersShared=[], stepByStep=False,
                            breakpoint=False, testId=0, runningAgents=[], runningProbes=[], channelId=False, testLocation='' ):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']
    if 'src-exec' in dataTest:
        srcExec = dataTest['src-exec']

    if 'testunit' in dataTest:
        srcTest = "class TESTCASE_01(TestCase):\t%s"% indent(srcTest)
        srcExec = "TESTCASE_01(suffix=None, testName='%s' % description('name')).execute()"

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs() )

    te.append( """channelid_ = %s\n""" % channelId )
    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestAdapter.setMainPath(sutPath=root)
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, 
                        parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

Scheduler.initialize()
class Cleanup(Exception): pass

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK
return_message = None

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_, channelid_=channelid_)

def initialize_te():
	TCI.initialize( address =  (controller_ip, int(controller_port) ), name = "%s.%s" %(log_filename, task_id) )

def finalize_te (return_code):
	TCI.finalize()

initialize_te()

tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""")
    te.append("""tsMgr.setNbTests(nb=1)""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTs(name=test_name, isEnabled=True, dataInputs=TestProperties.Parameters().data(), 
                sutInputs=TestProperties.Parameters().sut(), summary=TestProperties.Descriptions().get(name="summary"), 
                startedAt=time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(time.time()) ), 
                dataOutputs=TestProperties.Parameters().dataOut(), 
                sutOutputs=TestProperties.Parameters().sutOut(), testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

adpsMgr = TestExecutorLib.getAdpsMgr()
adpsMgrALL = TestExecutorLib.getAdpsMgrALL()

scriptstart_time = time.time()
TLX.instance().log_script_started()
testsuitestart_time = time.time()
tsMgr.isTestStarted()
TLX.instance().log_testsuite_started()
TLX.instance().log_testsuite_info(message = 'BEGIN', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
try:
""")
    te.append( CODE_PROBES ) 
    te.append("""	__PROBES__ = %s""" % probes )
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility

	def description(name):
		return TestProperties.Descriptions().get(name=name)
	
""")
    te.append( TEST_SUMMARY ) 
    te.append( TEST_SUMMARY_TS ) 
    for ds in missingDataset:
        te.append("""	TLX.instance().log_testsuite_warning(message = 'Dataset missing %s on inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingDatasetOut:
        te.append("""	TLX.instance().log_testsuite_warning(message = 'Dataset missing %s on outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImages:
        te.append("""	TLX.instance().log_testsuite_warning(message = 'Image missing %s on inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImagesOut:
        te.append("""	TLX.instance().log_testsuite_warning(message = 'Image missing %s on outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testsuite_internal(message = 'Loading modules...\\nDefault[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTSUITE', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if not withoutProbes:
        te.append("""
	# first step get active network probe 
	get_active_probes__()
	prepare_probes__()
	start_probe__()

""")
    else:
        te.append("""
	TLX.instance().log_testsuite_warning(message = "Probes are not activated with this run.", component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""")
    te.append("""
	# !! test injection
""")
    nbSubTe = int(subTEs) -1
    te.append( """
	from SubTE%s import *
""" %  str(nbSubTe) )
    te.append("\n")
    te.append("""
	# !! test exec injection
""")
    te.append(indent(srcExec))
    te.append("""
except Exception as e:
    if not isinstance(e, ForceStopException):
        return_message = "ERR_TE_500: %s" % str( e )
        return_code = RETURN_CODE_TE_ERROR
        
        TLX.instance().error(return_message)
        TLX.instance().log_testsuite_error(return_message, component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

tcMgr.endingAll()

try:
""")
    if not withoutProbes:
        te.append("""
	stop_probe__()
""")
    else:
        te.append("""
	pass
""")
    te.append("""	
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	TLX.instance().log_testsuite_error( message = str(e), component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

for adpId, adp in adpsMgr.getAdps().items():
	try:
		adp.onReset()
	except Exception as e:
		TLX.instance().log_testsuite_error( "shared adapter: %s" % str(e), 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	adp.stop()
	adp.join()

TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testsuitestop_time = time.time()
testsuiteduration = testsuitestop_time - testsuitestart_time
TLX.instance().log_testsuite_stopped( result=tsMgr.computeResults(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_  )
tsMgr.addTestDuration(duration=testsuiteduration)

scriptstop_time = time.time()
scriptduration = scriptstop_time - scriptstart_time
TLX.instance().log_script_stopped(duration=scriptduration, finalverdict=tsMgr.computeResults(), prjId=projectid_)
tsMgr.addScriptDuration(duration=scriptduration)

tsMgr.saveToCsv()
tsMgr.saveBasicReports(stoppedAt=scriptstop_time)
tsMgr.saveReports(stoppedAt=scriptstop_time)
tsMgr.saveDesigns()

tsMgr.saveDesignsXml()
tsMgr.saveReportsXml()
tsMgr.saveVerdictToXml()

# reset all adapters and libraries, just to be sure!
for adpId, adp in adpsMgrALL.getAdps().items():
    try:
        adp.onReset()
        adp.stop()
        adp.join()
    except Exception as e:
        pass

try:
	finalize_te(return_code)
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )

TLX.finalize()
Scheduler.finalize()

sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')


def createTestUnit (	dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='',
                        defaultAdapter='', userId=0, projectId=0, subTEs=1, parametersShared=[], stepByStep=False, 
                        breakpoint=False, testId=0, runningAgents=[], runningProbes=[], channelId=False, testLocation=''):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs() )
    te.append( """channelid_ = %s\n""" % channelId )
    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestAdapter.setMainPath(sutPath=root)
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

Scheduler.initialize()
class Cleanup(Exception): pass

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK
return_message = None

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_, channelid_=channelid_)

def initialize_te():
	TCI.initialize( address =  (controller_ip, int(controller_port) ), name = "%s.%s" %(log_filename, task_id) )

def finalize_te (return_code):
	TCI.finalize()

initialize_te()

tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""" )
    te.append("""tsMgr.setNbTests(nb=1)""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTu(name=test_name, isEnabled=True, dataInputs=TestProperties.Parameters().data(), 
                sutInputs=TestProperties.Parameters().sut(), summary=TestProperties.Descriptions().get(name="summary"), 
                startedAt=time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(time.time()) ), 
                dataOutputs=TestProperties.Parameters().dataOut(), 
                sutOutputs=TestProperties.Parameters().sutOut(), testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

adpsMgr = TestExecutorLib.getAdpsMgr()
adpsMgrALL = TestExecutorLib.getAdpsMgrALL()

scriptstart_time = time.time()
TLX.instance().log_script_started()
testunitstart_time = time.time()
tsMgr.isTestStarted()
TLX.instance().log_testunit_started()
TLX.instance().log_testunit_info(message = 'BEGIN', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
try:
""")
    te.append( CODE_PROBES ) 
    te.append("""	__PROBES__ = %s""" % probes )
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility

	def description(name):
		return TestProperties.Descriptions().get(name=name)

""")
    te.append( TEST_SUMMARY ) 
    te.append( TEST_SUMMARY_TU ) 
    for ds in missingDataset:
        te.append("""	TLX.instance().log_testunit_warning(message = 'Dataset missing %s on inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingDatasetOut:
        te.append("""	TLX.instance().log_testunit_warning(message = 'Dataset missing %s on outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImages:
        te.append("""	TLX.instance().log_testunit_warning(message = 'Image missing %s on inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImagesOut:
        te.append("""	TLX.instance().log_testunit_warning(message = 'Image missing %s on outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testunit_internal(message = 'Loading modules...\\nDefault[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTUNIT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if not withoutProbes:
        te.append("""
	# first step get active network probe 
	get_active_probes__()
	prepare_probes__()
	start_probe__()

""")
    else:
        te.append("""
	TLX.instance().log_testunit_warning(message = "Probes are not activated with this run.", component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""")
    nbSubTe = int(subTEs) - 1
    te.append("""
	from SubTE%s import *
""" % str(nbSubTe) )

    te.append("\n")
    te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
    te.append("""
except Exception as e:
    if not isinstance(e, ForceStopException):
        return_message = "ERR_TE_500: %s" % str( e )
        return_code = RETURN_CODE_TE_ERROR
        
        TLX.instance().error(return_message)
        TLX.instance().log_testunit_error(return_message, component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

try:
""")
    if not withoutProbes:
        te.append("""
	stop_probe__()
""")
    else:
        te.append("""
	pass
""")
    te.append("""	
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	TLX.instance().log_testunit_error( message = str(e), component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

for adpId, adp in adpsMgr.getAdps().items():
	try:
		adp.onReset()
	except Exception as e:
		TLX.instance().log_testunit_error( "shared adapter: %s" % str(e), 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	adp.stop()
	adp.join()

TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testunitstop_time = time.time()
testunitduration = testunitstop_time - testunitstart_time
TLX.instance().log_testunit_stopped( result=tsMgr.computeResults(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_  )
tsMgr.addTestDuration(duration=testunitduration)

scriptstop_time = time.time()
scriptduration = scriptstop_time - scriptstart_time
TLX.instance().log_script_stopped(duration=scriptduration, finalverdict=tsMgr.computeResults(), prjId=projectid_)
tsMgr.addScriptDuration(duration=scriptduration)

tsMgr.saveToCsv()
tsMgr.saveBasicReports(stoppedAt=scriptstop_time)
tsMgr.saveReports(stoppedAt=scriptstop_time)
tsMgr.saveDesigns()

tsMgr.saveDesignsXml()
tsMgr.saveReportsXml()
tsMgr.saveVerdictToXml()

# reset all adapters and libraries, just to be sure!
for adpId, adp in adpsMgrALL.getAdps().items():
    try:
        adp.onReset()
        adp.stop()
        adp.join()
    except Exception as e:
        pass

try:
	finalize_te(return_code)
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )

TLX.finalize()
Scheduler.finalize()

sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')

def createTestAbstract (	dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary='',
                        defaultAdapter='', userId=0, projectId=0, subTEs=1, parametersShared=[], stepByStep=False, 
                        breakpoint=False, testId=0, runningAgents=[], runningProbes=[], channelId=False, testLocation=''):
    """
    Creates and returns a test abstract executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['properties']
    parameters = properties['inputs-parameters']['parameter']
    parametersOut = properties['outputs-parameters']['parameter']
    agents = properties['agents']['agent']
    descriptions = properties['descriptions']['description']
    probes = properties['probes']['probe']

    SutLibraries = defaultLibrary
    SutAdapters = defaultAdapter
    for d in descriptions:
        if d['key'] == 'libraries':
            SutLibraries = d['value']
        if d['key'] == 'adapters':
            SutAdapters = d['value']

    if not len(SutLibraries):
        SutLibraries = RepoLibraries.instance().getDefault()
    if not len(SutAdapters):
        SutAdapters = RepoAdapters.instance().getDefault()
        
    SutLibrariesGeneric = RepoLibraries.instance().getGeneric()
    SutAdaptersGeneric = RepoAdapters.instance().getGeneric()
    
    if 'src-test' in dataTest:
        srcTest = dataTest['src-test']

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = loadImages(parameters=parameters, user=userName)
    missingImagesOut = loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( IMPORT_PY_LIBS )

    # import static arguments
    te.append( getStaticArgs() )

    te.append( """channelid_ = %s\n""" % channelId )
    te.append( """user_ = '%s'\n""" % userName )
    te.append( """userid_ = '%s'\n""" % userId )
    te.append( """projectid_ = '%s'\n""" % projectId )
    te.append( """projectname_ = '%s'\n""" % projectName )
    te.append( """test_name = '%s'\n""" % testName )
    te.append( """test_location = '%s'\n""" % testLocation )
    te.append( """test_result_path = '%s'\n""" % trPath )
    te.append( """log_filename = '%s'\n""" % logFilename )
    te.append( """tests_path = '%s/%s/'\n""" % (RepoTests.instance().testsPath,projectId) )
    te.append( """adapters_path = '%s/'\n""" % (RepoAdapters.instance().testsPath) )
    te.append( """libraries_path = '%s/'\n""" % (RepoLibraries.instance().testsPath) )
    te.append("""

task_id = sys.argv[1] # task server id
test_id = sys.argv[2] # tab id of the test result in the gui
replay_id = sys.argv[3]

result_path = '%s/%s' % (tests_result_path, test_result_path)
sys.path.insert(0, root )
sys.stdout = sys.stderr = open( '%s/test.out' % result_path ,'a', 0) 

import TestExecutorLib.TestRepositoriesLib as TestRepositories
TestRepositories.setTestsPath(path=tests_path)
TestRepositories.setAdpsPath(path=adapters_path)
TestRepositories.setLibsPath(path=libraries_path)
""")

    # import test executor libraries
    te.append(IMPORT_TE_LIBS)

    te.append("""
TestAdapter.setMainPath(sutPath=root)
TestProperties.initialize(parameters=%s, descriptions=%s, parametersOut=%s, agents=%s, parametersShared=%s, runningAgents=%s, runningProbes=%s)""" % (parameters, descriptions, parametersOut, agents, parametersShared, runningAgents, runningProbes) )

    te.append("""

Scheduler.initialize()
class Cleanup(Exception): pass

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

CMD_GET_PROBE = 1
CMD_START_PROBE = 2
CMD_STOP_PROBE = 3

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK
return_message = None

TDS.initialize(path = result_path)

TLX.initialize(path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
	replay_id_ = replay_id, task_id_ = task_id, userid_ = userid_, channelid_=channelid_)

def initialize_te():
	TCI.initialize( address =  (controller_ip, int(controller_port) ), name = "%s.%s" %(log_filename, task_id) )

def finalize_te (return_code):
	TCI.finalize()

initialize_te()

tsMgr = TestExecutorLib.getTsMgr()
tcMgr = TestExecutorLib.getTcMgr()
""" )
    te.append("""tsMgr.setNbTests(nb=1)""")
    te.append("""
tsMgr.initialize(path=result_path, testname=test_name, replayId=replay_id, userId=userid_, projectId=projectid_, 
                stepByStep=%s, breakpoint=%s, testId=%s, relativePath=test_result_path, 
                testpath=test_location, userName=user_, projectName=projectname_)""" % (stepByStep, breakpoint, testId) )
    te.append("""
tsMgr.newTa(name=test_name, isEnabled=True, dataInputs=TestProperties.Parameters().data(), sutInputs=TestProperties.Parameters().sut(),
            summary=TestProperties.Descriptions().get(name="summary"), 
            startedAt=time.strftime( "%d/%m/%Y %H:%M:%S", time.localtime(time.time()) ), 
            dataOutputs=TestProperties.Parameters().dataOut(), 
            sutOutputs=TestProperties.Parameters().sutOut(), testPath=test_location, testProject=projectname_)

tsMgr.setMainDescriptions(descriptions=TestProperties.Parameters().descriptions())

adpsMgr = TestExecutorLib.getAdpsMgr()
adpsMgrALL = TestExecutorLib.getAdpsMgrALL()

scriptstart_time = time.time()
TLX.instance().log_script_started()
testabstractstart_time = time.time()
tsMgr.isTestStarted()
TLX.instance().log_testabstract_started()
TLX.instance().log_testabstract_info(message = 'BEGIN', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
try:
""")
    te.append( CODE_PROBES ) 
    te.append("""	__PROBES__ = %s""" % probes )
    te.append("""	

	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def output(name):
		return TestProperties.Parameters().output(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def setOutput(name, value):
		return TestProperties.Parameters().setOutput(name=name, value=value)
	def agent(name):
		return TestProperties.Parameters().agent(name=name)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def outputs():
		return TestProperties.Parameters().outputs()
	def agents():
		return TestProperties.Parameters().agents()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility

	def description(name):
		return TestProperties.Descriptions().get(name=name)
	
""")
    te.append( TEST_SUMMARY ) 
    te.append( TEST_SUMMARY_TA ) 
    for ds in missingDataset:
        te.append("""	TLX.instance().log_testabstract_warning(message = 'Dataset missing %s on inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingDatasetOut:
        te.append("""	TLX.instance().log_testabstract_warning(message = 'Dataset missing %s on outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImages:
        te.append("""	TLX.instance().log_testabstract_warning(message = 'Image missing %s on inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    for ds in missingImagesOut:
        te.append("""	TLX.instance().log_testabstract_warning(message = 'Image missing %s on outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testabstract_internal(message = 'Loading modules...\\nDefault[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTABSTRACT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

    if SutLibrariesGeneric:
        te.append("""

	# !! generic local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibrariesGeneric""" % SutLibrariesGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
        te.append("""
		raise Exception('Generic SUT libraries %s is not applicable'""" % SutLibrariesGeneric )
        te.append(""")
""")

    if SutAdaptersGeneric:
        te.append("""
	# !! generic local adapters injection
	try:
		from SutAdapters import %s as SutAdaptersGeneric""" % SutAdaptersGeneric )
        te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
        te.append("""
		raise Exception('Generic SUT adapter %s is not applicable'""" % SutAdaptersGeneric )
        te.append(""")	
""")

    te.append("""

	# !! local libraries adapters injection
	try:
		from SutLibraries import %s as SutLibraries""" % SutLibraries )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")
    te.append("""
		raise Exception('SUT libraries %s is not applicable'""" % SutLibraries )
    te.append(""")
""")
    te.append("""
	# !! local adapters injection
	try:
		from SutAdapters import %s as SutAdapters""" % SutAdapters )
    te.append("""
	except Exception as e:
		sys.stderr.write( '%s\\n' % str(e) )""")	
    te.append("""
		raise Exception('SUT adapter %s is not applicable'""" % SutAdapters )
    te.append(""")	
""")
    te.append("""
	if TestAdapter.isDeprecated():
		raise Exception('SUT adapter %s is deprecated')
""" % SutAdapters )
    te.append("""
	if TestLibrary.isDeprecated():
		raise Exception('SUT library %s is deprecated')  
""" % SutLibraries )

    if SutLibrariesGeneric:
        te.append("""
	try:
		SutLibraries.Generic = SutLibrariesGeneric
	except Exception as e:
		pass
""" )

    if SutAdaptersGeneric:
        te.append("""
	try:
		SutAdapters.Generic = SutAdaptersGeneric
	except Exception as e:
		pass
""" )

    if not withoutProbes:
        te.append("""
	# first step get active network probe 
	get_active_probes__()
	prepare_probes__()
	start_probe__()

""")
    else:
        te.append("""
	TLX.instance().log_testabstract_warning(message = "Probes are not activated with this run.", component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""")
    nbSubTe = int(subTEs) - 1
    te.append("""
	from SubTE%s import *
""" % str(nbSubTe) )

    te.append("\n")
    te.append(indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
    te.append("""
except Exception as e:
    if not isinstance(e, ForceStopException) :
        return_message = "ERR_TE_500: %s" % str( e )
        return_code = RETURN_CODE_TE_ERROR
        
        TLX.instance().error(return_message)
        TLX.instance().log_testabstract_error(return_message, component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)

try:
""")
    if not withoutProbes:
        te.append("""
	stop_probe__()
""")
    else:
        te.append("""
	pass
""")
    te.append("""	
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )
	TLX.instance().log_testabstract_error( message = str(e), component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER )

for adpId, adp in adpsMgr.getAdps().items():
	try:
		adp.onReset()
	except Exception as e:
		TLX.instance().log_testabstract_error( "shared adapter: %s" % str(e), 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
	adp.stop()
	adp.join()

TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testabstractstop_time = time.time()
testabstractduration = testabstractstop_time - testabstractstart_time
TLX.instance().log_testabstract_stopped( result=tsMgr.computeResults(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_  )
tsMgr.addTestDuration(duration=testabstractduration)

scriptstop_time = time.time()
scriptduration = scriptstop_time - scriptstart_time
TLX.instance().log_script_stopped(duration=scriptduration, finalverdict=tsMgr.computeResults(), prjId=projectid_)
tsMgr.addScriptDuration(duration=scriptduration)

tsMgr.saveToCsv()
tsMgr.saveBasicReports(stoppedAt=scriptstop_time)
tsMgr.saveReports(stoppedAt=scriptstop_time)
tsMgr.saveDesigns()

tsMgr.saveDesignsXml()
tsMgr.saveReportsXml()
tsMgr.saveVerdictToXml()

# reset all adapters and libraries, just to be sure!
for adpId, adp in adpsMgrALL.getAdps().items():
    try:
        adp.onReset()
        adp.stop()
        adp.join()
    except Exception as e:
        pass

try:
	finalize_te(return_code)
except Exception as e:
	sys.stderr.write( '%s\\n' % str(e) )

TLX.finalize()
Scheduler.finalize()

sys.exit(return_code)
""")
    return unicode(''.join(te)).encode('utf-8')