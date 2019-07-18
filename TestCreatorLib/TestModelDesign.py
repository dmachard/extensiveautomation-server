#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# Copyright (c) 2010-2019 Denis Machard
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

# /!\ WARNING /!\
# Don't replace tab to space on python code generated for test
# the test is not compliant with python recommandation
# /!\ WARNING /!\

import sys

try:
    import TestModelCommon
except ImportError: # support python 3
    from . import TestModelCommon

from ServerRepositories import ( RepoManager, 
                                 RepoTests,
                                 RepoAdapters )
from ServerEngine import ( Common, ProjectsManager )


# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

def createTestDesign(   dataTest, 
                        userName, 
                        testName, 
                        trPath, 
                        logFilename, 
                        withoutProbes, 
                        defaultLibrary='', 
                        defaultAdapter='', 
                        userId=0,
                        projectId=0, 
                        parametersShared=[], 
                        stepByStep=False,
                        breakpoint=False, 
                        testId=0, 
                        runningAgents=[], 
                        runningProbes=[],
                        testLocation='', 
                        taskUuid='' ):
    """
    Creates and returns the test executable for design only

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    if dataTest["test-extension"] == "tgx":
        return createTestDesignForTg( dataTest, userName, testName, trPath, 
                                    logFilename, withoutProbes, defaultLibrary,
                                    defaultAdapter, userId, projectId, parametersShared, 
                                    stepByStep, breakpoint, testId,
                                    runningAgents, runningProbes, testLocation, taskUuid)
    elif dataTest["test-extension"] == "tpx":
        return createTestDesignForTp( dataTest, userName, testName, trPath, 
                                    logFilename, withoutProbes, defaultLibrary,
                                    defaultAdapter, userId, projectId, parametersShared, 
                                    stepByStep, breakpoint, testId,
                                    runningAgents, runningProbes, testLocation, taskUuid)
    elif dataTest["test-extension"] == "tux":
        return createTestDesignForTu( dataTest, userName, testName, trPath, 
                                    logFilename, withoutProbes, defaultLibrary, 
                                    defaultAdapter, userId, projectId, parametersShared, 
                                    stepByStep, breakpoint, testId,
                                    runningAgents, runningProbes, testLocation, taskUuid)
    else:
        return createTestDesignForTs( dataTest, userName, testName, trPath, logFilename, 
                                    withoutProbes, defaultLibrary, 
                                    defaultAdapter, userId, projectId, parametersShared, 
                                    stepByStep, breakpoint, testId,
                                    runningAgents, runningProbes, testLocation, taskUuid)

def createTestDesignForTg(dataTest, 
                          userName, 
                          testName, 
                          trPath, 
                          logFilename, 
                          withoutProbes, 
                          defaultLibrary='', 
                          defaultAdapter='', 
                          userId=0,
                          projectId=0, 
                          parametersShared=[], 
                          stepByStep=False, 
                          breakpoint=False, 
                          testId=0, 
                          runningAgents=[], 
                          runningProbes=[],
                          testLocation='', 
                          taskUuid=''  ):
    """
    """
    properties = dataTest['test-properties']
    parameters = properties['inputs-parameters']['parameter']
    descriptions = properties['descriptions']['description']

    testglobal = dataTest['test-execution']
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs(envTmp=True) )
    
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize()
ParametersHandler = TestProperties.instance()

scriptstart_time = time.time()

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, 
                user_ = user_, testname_ = test_name, id_ = test_id, 
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
    te.append( """	ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """	ParametersHandler.addParametersShared( parameters=%s)\n""" % parametersShared )
    te.append( """	ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """
	TestProperties.instance().initAtRunTime(cache=Cache())
	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
        
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)

	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")

    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )

    te.append("""
	try:
		from Var.SutAdapters import *
		import Var.SutAdapters as SutAdapters
		SutLibraries = SutAdapters
	except Exception as e:
		raise Exception('SUT adapters import error (more details)\\n\\n%s' % str(e))
	# try:
		# from Var.SutLibraries import *
		# import Var.SutLibraries as SutLibraries
	# except Exception as e:
		# raise Exception('SUT libraries import error (more details)\\n\\n%s' % str(e))    
""" )

    te.append( TestModelCommon.TEST_SUMMARY )

    if not len(testglobal):
        te.append("""
	pass
""")
    for ts in testglobal:
        isTs=True
        isTa=True
        
        if sys.version_info > (3,): # python3 support
            ts["alias"] = ts["alias"].decode("utf8")
            
        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
        if ts['enable'] == TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            te.append(Common.indent("""
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = TestModelCommon.loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = TestModelCommon.loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)

            if isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            te.append(Common.indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )

            te.append("\n")
            te.append("\n")
            te.append("\n")
            te.append("\n")

            te.append( Common.indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-definition'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("class TESTCASE(TestCase):", nbTab = ts['depth'] + 2 ))
                te.append("\n")
                te.append(Common.indent(ts['test-definition'], nbTab = ts['depth'] + 3 ))
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-execution'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            te.append(Common.indent("""
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

def createTestDesignForTp(dataTest, 
                          userName, 
                          testName, 
                          trPath, 
                          logFilename, 
                          withoutProbes, 
                          defaultLibrary='', 
                          defaultAdapter='', userId=0,
                          projectId=0, 
                          parametersShared=[], 
                          stepByStep=False, 
                          breakpoint=False, 
                          testId=0, 
                          runningAgents=[], 
                          runningProbes=[],
                          testLocation='', 
                          taskUuid='' ):
    """
    """
    properties = dataTest['test-properties']
    parameters = properties['inputs-parameters']['parameter']
    descriptions = properties['descriptions']['description']

    testplan = dataTest['test-execution']
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs(envTmp=True) )
    
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize()
ParametersHandler = TestProperties.instance()

scriptstart_time = time.time()

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13

return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, 
                user_ = user_, testname_ = test_name, id_ = test_id, 
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
    te.append( """	ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
    te.append( """	ParametersHandler.addParametersShared( parameters=%s)\n""" % parametersShared )
    te.append( """	ParametersHandler.addRunningAgents( agents=%s)\n""" % runningAgents )
    te.append( """
	TestProperties.instance().initAtRunTime(cache=Cache())
	def shared(project, name, subname=''):
		return ParametersHandler.shared(project=project, name=name, subname=subname)
	def input(name):
		return ParametersHandler.parameter(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def setInput(name, value):
		return ParametersHandler.setParameter(name=name, value=value, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def running(name):
		return ParametersHandler.running(name=name)
	def excel(data, worksheet, row=None, column=None):
		return ParametersHandler.excel(data=data, worksheet=worksheet, row=row, column=column)
        
	get = parameter = input # backward compatibility
	def inputs():
		return ParametersHandler.inputs(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
	def descriptions():
		return ParametersHandler.descriptions(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)

	def description(name):
		return ParametersHandler.description(name=name, tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId)
""")

    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )

    te.append("""
	try:
		from Var.SutAdapters import *
		import Var.SutAdapters as SutAdapters
		SutLibraries = SutAdapters
	except Exception as e:
		raise Exception('SUT adapters import error (more details)\\n\\n%s' % str(e))   
""" )
    te.append( TestModelCommon.TEST_SUMMARY )

    if not len(testplan):
        te.append("""
	pass
""")
    for ts in testplan:
        isTs=True
        isTa = False
        
        if sys.version_info > (3,): # python3 support
            ts["alias"] = ts["alias"].decode("utf8")

        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
        if ts['enable'] == TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            te.append(Common.indent("""
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = TestModelCommon.loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = TestModelCommon.loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)

            if isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=%s, testPath="%s", testProject="%s", nameAlias="%s")
if %s:""" % (ts['path'], ts['enable'], ts["testpath"], ts["testproject"], ts["alias"], ts['enable']) , nbTab = ts['depth'] + 1 ) )
            te.append(Common.indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )

            te.append("\n")
            te.append("\n")
            te.append("\n")
            te.append("\n")

            te.append( Common.indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            # te.append( Common.indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        # ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-definition'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("class TESTCASE(TestCase):", nbTab = ts['depth'] + 2 ))
                te.append("\n")
                te.append(Common.indent(ts['test-definition'], nbTab = ts['depth'] + 3 ))
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-execution'], nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            te.append(Common.indent("""
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

def createTestDesignForTs(dataTest, 
                          userName, 
                          testName, 
                          trPath, 
                          logFilename, 
                          withoutProbes, 
                          defaultLibrary='', 
                          defaultAdapter='', 
                          userId=0,
                          projectId=0, 
                          parametersShared=[], 
                          stepByStep=False, 
                          breakpoint=False, 
                          testId=0, 
                          runningAgents=[], 
                          runningProbes=[],
                          testLocation='', 
                          taskUuid=''  ):
    """
    """
    properties = dataTest['test-properties']
    parameters = properties['inputs-parameters']['parameter']
    descriptions = properties['descriptions']['description']

    srcTest = dataTest['test-definition']
    srcExec = dataTest['test-execution']

    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs(envTmp=True) )
    
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize(parameters=%s, descriptions=%s, parametersShared=%s, runningAgents=%s)""" % (parameters, descriptions, parametersShared, runningAgents) )

    te.append("""

scriptstart_time = time.time()
RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13
return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
	TestProperties.instance().initAtRunTime(cache=Cache())
	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility
	def description(name):
		return TestProperties.Descriptions().get(name=name)
""")

    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )

    te.append("""
	try:
		from Var.SutAdapters import *
		import Var.SutAdapters as SutAdapters
		SutLibraries = SutAdapters
	except Exception as e:
		raise Exception('SUT adapters import error (more details)\\n\\n%s' % str(e))   
""" )
    te.append( TestModelCommon.TEST_SUMMARY ) 
    te.append("""
	# !! test injection
""")
    te.append(Common.indent(srcTest))
    te.append("\n")
    te.append("""
	# !! test exec injection
""")
    te.append(Common.indent(srcExec))
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

def createTestDesignForTu(dataTest, 
                          userName, 
                          testName, 
                          trPath, 
                          logFilename, 
                          withoutProbes, 
                          defaultLibrary='', 
                          defaultAdapter='', 
                          userId=0,
                          projectId=0, 
                          parametersShared=[], 
                          stepByStep=False, 
                          breakpoint=False, 
                          testId=0, 
                          runningAgents=[], 
                          runningProbes=[],
                          testLocation='', 
                          taskUuid=''  ):
    """
    """
    properties = dataTest['test-properties']
    parameters = properties['inputs-parameters']['parameter']
    descriptions = properties['descriptions']['description']
    
    srcTest = dataTest['test-definition']
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs(envTmp=True) )
    
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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
    
    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

    te.append("""
TestProperties.initialize(parameters=%s, descriptions=%s, parametersShared=%s, runningAgents=%s)""" % (parameters, descriptions, parametersShared, runningAgents) )

    te.append("""

RETURN_CODE_OK = 0
RETURN_CODE_TE_ERROR = 13
scriptstart_time = time.time()
return_code = RETURN_CODE_OK

TDS.initialize(path = result_path)

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
	TestProperties.instance().initAtRunTime(cache=Cache())
	def shared(project, name, subname=''):
		return TestProperties.Parameters().shared(project=project, name=name, subname=subname)
	def input(name):
		return TestProperties.Parameters().input(name=name)
	def setInput(name, value):
		return TestProperties.Parameters().setInput(name=name, value=value)
	def running(name):
		return TestProperties.Parameters().running(name=name) 
	def inputs():
		return TestProperties.Parameters().inputs()
	def descriptions():
		return TestProperties.Parameters().descriptions()
	def excel(data, worksheet, row=None, column=None):
		return TestProperties.Parameters().excel(data=data, worksheet=worksheet, row=row, column=column)
	get = parameter = input # backward compatibility
	def description(name):
		return TestProperties.Descriptions().get(name=name)
""")

    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )

    te.append("""
	try:
		from Var.SutAdapters import *
		import Var.SutAdapters as SutAdapters
		SutLibraries = SutAdapters
	except Exception as e:
		raise Exception('SUT adapters import error (more details)\\n\\n%s' % str(e))   
""" )
    te.append( TestModelCommon.TEST_SUMMARY ) 
    te.append("""
	# !! test injection
	class TESTCASE(TestCase):
""")
    te.append(Common.indent(srcTest, nbTab=2))
    te.append("\n")
    te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
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

