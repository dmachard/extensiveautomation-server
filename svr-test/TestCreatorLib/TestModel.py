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

# /!\ WARNING /!\
# Don't replace tab to space on python code generated for test
# the test is not compliant with python recommandation
# /!\ WARNING /!\

import sys

try:
    import TestModelCommon
except ImportError: # support python 3
    from . import TestModelCommon

from ServerRepositories import ( RepoManager, RepoTests,
                                 RepoAdapters, RepoLibraries )
from ServerEngine import ( Common, ProjectsManager )
                          
# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

def createTestExecutable( dataTest, 
                          userName, 
                          testName, 
                          trPath, 
                          logFilename, 
                          withoutProbes, 
                          defaultLibrary='', 
                          defaultAdapter='', 
                          userId=0,
                          projectId=0, 
                          subTEs=1, 
                          parametersShared=[], 
                          stepByStep=False, 
                          breakpoint=False, 
                          testId=0, 
                          runningAgents=[], 
                          runningProbes=[],
                          channelId=False, 
                          testLocation='', 
                          taskUuid=''):
    """
    Creates and returns the test executable: testplan or testsuite

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    if dataTest["test-extension"] == "tgx":
        return createTestGlobal( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                runningAgents, runningProbes, channelId, testLocation, taskUuid)
    elif dataTest["test-extension"] == "tpx":
        return createTestPlan( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                runningAgents, runningProbes, channelId, testLocation, taskUuid)
    elif dataTest["test-extension"] == "tux":
        return createTestUnit( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                runningAgents, runningProbes, channelId, testLocation, taskUuid)
    elif dataTest["test-extension"] == "tax":
        return createTestAbstract( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary, 
                                defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                runningAgents, runningProbes, channelId, testLocation, taskUuid)
    else:
        return createTestSuite( dataTest, userName, testName, trPath, logFilename, withoutProbes, defaultLibrary,
                                defaultAdapter, userId, projectId, subTEs, parametersShared, stepByStep, breakpoint, testId,
                                runningAgents, runningProbes, channelId, testLocation, taskUuid)

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

def createTestGlobal ( dataTest, 
                       userName, 
                       testName, 
                       trPath, 
                       logFilename, 
                       withoutProbes, 
                       defaultLibrary='', 
                       defaultAdapter='', 
                       userId=0, 
                       projectId=0, 
                       subTEs=1, 
                       parametersShared=[], 
                       stepByStep=False, 
                       breakpoint=False, 
                       testId=0,
                       runningAgents=[], 
                       runningProbes=[], 
                       channelId=False, 
                       testLocation='', 
                       taskUuid=''):
    """
    Creates and returns a test global executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['test-properties']
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

    testglobal = dataTest['test-execution']
    
    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = TestModelCommon.loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)
    missingImagesOut = TestModelCommon.loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs() )
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

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

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
TestProperties.instance().initAtRunTime(cache=Cache())\n""" )
    te.append( """ParametersHandler.addParametersShared( parameters=%s )\n""" % parametersShared )
    te.append( """ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
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
    te.append( TestModelCommon.CODE_PROBES ) 
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
    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )
    te.append( TestModelCommon.TEST_SUMMARY )
    te.append( TestModelCommon.TEST_SUMMARY_TG ) 
    for ds in missingDataset:
        te.append("""
	TLX.instance().log_testglobal_warning(message = 'Dataset %s is missing in inputs parameters.', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)
    for ds in missingDatasetOut:
        te.append("""
	TLX.instance().log_testglobal_warning(message = 'Dataset %s is missing in outputs parameters.', component = 'TESTGLOBAL', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testglobal_internal(message = 'Loading modules...\\nExtra[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTGLOBAL', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

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
        
        
        if sys.version_info > (3,): # python3 support
            ts["alias"] = ts["alias"].decode("utf8")

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
                te.append( Common.indent("""
TLX.instance().setMainTpId(tpId='%s-0')
if not TLX.instance().allPassed(tsId = "%s-0"):
	TLX.instance().setMainTpResult(tpId='%s-0')
else:
    """ % (ts['id'], ts['parent'], ts['id']), nbTab = ts['depth'] ) )
                if ts['separator'] == 'terminated':
                    te.append( Common.indent("""
	testplanstop_time = time.time()
	testplanduration = testplanstop_time - testplanstart_time
	tsMgr.addSubTestPlanDuration(duration=testplanduration)
	tsMgr.newStopTpInTg(name="%s", nameAlias="%s")
	TLX.instance().log_testplan_separator_terminated(tid='%s', testname='%s', duration=testplanduration, alias='%s')
	""" % ( ts['testname'], ts['alias'], ts['id'], ts['testname'], ts['alias']), nbTab = ts['depth'] ) )
                else:
                    te.append( Common.indent("""
	ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s) 
	tsMgr.newStartTpInTg(name="%s", nameAlias="%s", summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath='%s', testProject='%s')
	testplanstart_time = time.time()
	TLX.instance().log_testplan_separator(tid='%s', testname='%s', alias='%s')
	""" % (  ts['properties']['descriptions']['description'], ts['testname'], ts['alias'], 
             ts["testpath"], ts["testproject"], 
             ts['id'], ts['testname'], ts['alias']), nbTab = ts['depth'] ) )
        
        if ts['enable'] != TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            parentId = "%s-0" % ts['parent']
            if 'tpid' in ts: parentId = "%s-0-%s" % (ts['tpid'], ts['parent'])
            if isTp:
                pass
            elif isTpFromTg:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=0, isTpFromTg=True, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")""" % (ts['path'], ts['alias'], ts["testpath"], ts["testproject"]) , nbTab = ts['depth'] ) )
            elif isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            elif isTa:
                te.append(Common.indent("""
tsMgr.newTa(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )

        if ts['enable'] == TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(Common.indent("""
	testsuitestart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            elif isTa:
                te.append(Common.indent("""
	testabstractstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            else:
                te.append(Common.indent("""
	testunitstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = TestModelCommon.loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = TestModelCommon.loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = TestModelCommon.loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = TestModelCommon.loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            parentId = "%s-0" % ts['parent']
            if 'tpid' in ts:
                parentId = "%s-0-%s" % (ts['tpid'], ts['parent'])
                
            # new in v17
            notCond = ""
            if ts['parent-condition'] == "1": 
                notCond = "not"
            # end of new
            
            if isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(Common.indent("""
tsMgr.newTa(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, parentId, notCond) , nbTab = ts['depth'] + 1 ) )
            
            tstId = "%s-0" % ts['id']
            if 'tpid' in ts:
                tstId = "%s-0-%s" % (ts['tpid'], ts['id'])
            te.append(Common.indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], tstId ), nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testsuite_started(tid='%s', alias='%s')
TLX.instance().log_testsuite_info(message = 'BEGIN', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            elif isTa:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testabstract_started(tid='%s', alias='%s')
TLX.instance().log_testabstract_info(message = 'BEGIN', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'],ts['alias']), nbTab = ts['depth']  + 2 ) )
            else:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testunit_started(tid='%s', alias='%s')
TLX.instance().log_testunit_info(message = 'BEGIN', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'],ts['alias']), nbTab = ts['depth']  + 2 ) )

            for dsTs in missingDatasetTs:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for dsTs in missingDatasetTsOut:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            for imgTs in missingImagesTs:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for imgTs in missingImagesTsOut:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            te.append( Common.indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """tsMgr.addSummary(summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( Common.indent( """tsMgr.addInputs(dataInputs=ParametersHandler.data(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutInputs=ParametersHandler.sut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( Common.indent( """tsMgr.addOutputs(dataOutputs=ParametersHandler.dataOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutOutputs=ParametersHandler.sutOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            if isTs:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-execution'], nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            if isTs:
                te.append(Common.indent("""
TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testsuitestop_time = time.time()
testsuiteduration = testsuitestop_time - testsuitestart_time
TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testsuiteduration)""", nbTab = ts['depth'] + 2 ) )
            elif isTa:
                te.append(Common.indent("""
TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testabstractstop_time = time.time()
testabstractduration = testabstractstop_time - testabstractstart_time
TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testabstractduration)""", nbTab = ts['depth'] + 2 ) )
            else:
                te.append(Common.indent("""
TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testunitstop_time = time.time()
testunitduration = testunitstop_time - testunitstart_time
TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testunitduration)""", nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append(Common.indent("""
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
                te.append(Common.indent("""
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
                te.append(Common.indent("""
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

def createTestPlan ( dataTest, 
                     userName, 
                     testName, 
                     trPath, 
                     logFilename, 
                     withoutProbes, 
                     defaultLibrary='',
                     defaultAdapter='', 
                     userId=0, 
                     projectId=0, 
                     subTEs=1, 
                     parametersShared=[], 
                     stepByStep=False,
                     breakpoint=False, 
                     testId=0, 
                     runningAgents=[], 
                     runningProbes=[], 
                     channelId=False, 
                     testLocation='', 
                     taskUuid='' ):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['test-properties']
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

    testplan = dataTest['test-execution']
    
    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = TestModelCommon.loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)
    missingImagesOut = TestModelCommon.loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs() )
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

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

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
TestProperties.instance().initAtRunTime(cache=Cache())
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
    te.append( TestModelCommon.INPUT_CUSTOM )
    te.append( TestModelCommon.INPUT_CACHE )
    
    te.append( """
ParametersHandler.addParametersShared( parameters=%s )\n""" % parametersShared )
    te.append( """ParametersHandler.addParameters( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parameters )
    te.append( """ParametersHandler.addParametersOut( parametersId=TLX.instance().mainScriptId, parameters=%s)\n""" % parametersOut )
    te.append( """ParametersHandler.addAgents( agentsId=TLX.instance().mainScriptId, agents=%s)\n""" % agents )
    te.append( """ParametersHandler.addDescriptions( descriptionsId=TLX.instance().mainScriptId, descriptions=%s)\n""" % descriptions )
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
    te.append( TestModelCommon.CODE_PROBES ) 
    te.append( """	__PROBES__ = %s""" % probes )

    te.append( TestModelCommon.TEST_SUMMARY )
    te.append( TestModelCommon.TEST_SUMMARY_TP ) 
    for ds in missingDataset:
        te.append("""
	TLX.instance().log_testplan_warning(message = 'Dataset %s is missing in inputs parameters.', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)
    for ds in missingDatasetOut:
        te.append("""
	TLX.instance().log_testplan_warning(message = 'Dataset %s is missing in outputs parameters.', component = 'TESTPLAN', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % ds)

    te.append( """
	TLX.instance().log_testplan_internal(message = 'Loading modules...\\nExtra[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTPLAN', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

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
        
        if sys.version_info > (3,): # python3 support
            ts["alias"] = ts["alias"].decode("utf8")

        if 'extension' in ts:
            if ts['extension'] == RepoManager.TEST_UNIT_EXT:
                isTs=False
            if ts['extension'] == RepoManager.TEST_ABSTRACT_EXT:
                isTs=False
                isTa=True
                
        if ts['enable'] != TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth']  ) )
            elif isTa:
                te.append(Common.indent("""
tsMgr.newTa(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=0, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ))""" % (ts['path'], ts['alias']) , nbTab = ts['depth'] ) )

        if ts['enable'] == TestModelCommon.TS_ENABLED:
            ts['depth'] = 1 # bypass depath
            if isTs:
                te.append(Common.indent("""
	testsuitestart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            elif isTa:
                te.append(Common.indent("""
	testabstractstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            else:
                te.append(Common.indent("""
	testunitstart_time = time.time()
	try:
""", nbTab = ts['depth'] -1 ))
            # prepare datasets
            missingDatasetTs = TestModelCommon.loadDataset(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingDatasetTsOut = TestModelCommon.loadDataset(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)

            # prepare images
            missingImagesTs = TestModelCommon.loadImages(parameters=ts['properties']['inputs-parameters']['parameter'], user=userName)
            missingImagesTsOut = TestModelCommon.loadImages(parameters=ts['properties']['outputs-parameters']['parameter'], user=userName)
            
            # new in v17
            notCond = ""
            if ts['parent-condition'] == "1": 
                notCond = "not"
            # end of new
            
            if isTs:
                te.append(Common.indent("""
tsMgr.newTs(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            elif isTa:
                te.append(Common.indent("""
tsMgr.newTa(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            else:
                te.append(Common.indent("""
tsMgr.newTu(name="%s", isEnabled=%s, nameAlias="%s", startedAt=time.strftime( "%%d/%%m/%%Y %%H:%%M:%%S", time.localtime(time.time()) ), testPath="%s", testProject="%s")
if %s TLX.instance().allPassed(tsId = "%s", notCond="%s"):""" % (ts['path'], ts['enable'], ts['alias'], ts["testpath"], ts["testproject"], notCond, ts['parent'], notCond) , nbTab = ts['depth'] + 1 ) )
            te.append(Common.indent("""

TLX.instance().setUniqueId("%s", tsId = "%s")
	""" % ( ts['path'], ts['id'] ), nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testsuite_started(tid='%s', alias='%s')
TLX.instance().log_testsuite_info(message = 'BEGIN', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            elif isTa:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testabstract_started(tid='%s', alias='%s')
TLX.instance().log_testabstract_info(message = 'BEGIN', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )
            else:
                te.append( Common.indent("""
tsMgr.isTestStarted()
TLX.instance().log_testunit_started(tid='%s', alias='%s')
TLX.instance().log_testunit_info(message = 'BEGIN', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=False, flagBegin=True)
# !! test injection
	""" % (ts['id'], ts['alias']), nbTab = ts['depth']  + 2 ) )

            for dsTs in missingDatasetTs:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for dsTs in missingDatasetTsOut:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Dataset %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % dsTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            for imgTs in missingImagesTs:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in inputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )	
            te.append("\n")
            for imgTs in missingImagesTsOut:
                if isTs:
                    te.append( Common.indent("""
TLX.instance().log_testsuite_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                elif isTa:
                    te.append( Common.indent("""
TLX.instance().log_testabstract_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
                else:
                    te.append( Common.indent("""
TLX.instance().log_testunit_warning(message = 'Image %s is missing in outputs parameters', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % imgTs, nbTab = ts['depth'] + 2 ) )
            te.append("\n")

            te.append( Common.indent( """ParametersHandler.addParameters(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['inputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addParametersOut(parametersId=TLX.instance().scriptId, parameters = %s)""" %
                        ts['properties']['outputs-parameters']['parameter'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addDescriptions(descriptionsId=TLX.instance().scriptId, descriptions = %s)""" %
                        ts['properties']['descriptions']['description'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """ParametersHandler.addAgents(agentsId=TLX.instance().scriptId, agents = %s)""" %
                        ts['properties']['agents']['agent'], nbTab = ts['depth'] + 2 ))
            te.append("\n")
            te.append( Common.indent( """tsMgr.addSummary(summary=ParametersHandler.description(name="summary", tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( Common.indent( """tsMgr.addInputs(dataInputs=ParametersHandler.data(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutInputs=ParametersHandler.sut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            te.append( Common.indent( """tsMgr.addOutputs(dataOutputs=ParametersHandler.dataOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId), sutOutputs=ParametersHandler.sutOut(tpId=TLX.instance().mainScriptId, tsId=TLX.instance().scriptId))""" , nbTab = ts['depth'] + 2 ) )
            te.append("\n")
            if isTs:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("from SubTE%s import *" % i , nbTab = ts['depth'] + 2 ))
            te.append("\n")
            if isTs:
                te.append(Common.indent(ts['test-execution'], nbTab = ts['depth'] + 2 ))
            elif isTa:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            else:
                te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name')).execute()", nbTab = ts['depth'] + 2 ))
            if isTs:
                te.append(Common.indent("""
TLX.instance().log_testsuite_info(message = 'END', component = 'TESTSUITE', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testsuitestop_time = time.time()
testsuiteduration = testsuitestop_time - testsuitestart_time
TLX.instance().log_testsuite_stopped(result=tsMgr.getVerdictTs(), duration=testsuiteduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testsuiteduration)""", nbTab = ts['depth'] + 2 ) )
            elif isTa:
                te.append(Common.indent("""
TLX.instance().log_testabstract_info(message = 'END', component = 'TESTABSTRACT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testabstractstop_time = time.time()
testabstractduration = testabstractstop_time - testabstractstart_time
TLX.instance().log_testabstract_stopped(result=tsMgr.getVerdictTs(), duration=testabstractduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testabstractduration)""", nbTab = ts['depth'] + 2 ) )
            else:
                te.append(Common.indent("""
TLX.instance().log_testunit_info(message = 'END', component = 'TESTUNIT', fromlevel=LEVEL_TE, tolevel=LEVEL_USER, flagEnd=True, flagBegin=False)
testunitstop_time = time.time()
testunitduration = testunitstop_time - testunitstart_time
TLX.instance().log_testunit_stopped(result=tsMgr.getVerdictTs(), duration=testunitduration, nbTc=tsMgr.getNbTc(), prjId=projectid_)
tsMgr.addTestDuration(duration=testunitduration)""", nbTab = ts['depth'] + 2 ) )
            if isTs:
                te.append(Common.indent("""
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
                te.append(Common.indent("""
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
                te.append(Common.indent("""
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
		return_message = "ERR_TE_600: %s" % e

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

def createTestSuite (	dataTest, 
                        userName, 
                        testName, 
                        trPath, 
                        logFilename, 
                        withoutProbes, 
                        defaultLibrary='',
                        defaultAdapter='', 
                        userId=0, 
                        projectId=0, 
                        subTEs=1, 
                        parametersShared=[], 
                        stepByStep=False,
                        breakpoint=False, 
                        testId=0, 
                        runningAgents=[], 
                        runningProbes=[], 
                        channelId=False, 
                        testLocation='', 
                        taskUuid='' ):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['test-properties']
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

    srcTest = dataTest['test-definition']
    srcExec = dataTest['test-execution']

    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = TestModelCommon.loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)
    missingImagesOut = TestModelCommon.loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs() )
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

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

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
    te.append( TestModelCommon.CODE_PROBES ) 
    te.append("""	__PROBES__ = %s""" % probes )
    te.append("""	
	TestProperties.instance().initAtRunTime(cache=Cache())
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
    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )
    te.append(""" 
	TestProperties.instance().initAtRunTime(cache=Cache())
""")
    te.append( TestModelCommon.TEST_SUMMARY ) 
    te.append( TestModelCommon.TEST_SUMMARY_TS ) 
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
	TLX.instance().log_testsuite_internal(message = 'Loading modules...\\nExtra[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTSUITE', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

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
    te.append(Common.indent(srcExec))
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

def createTestUnit (	dataTest, 
                        userName, 
                        testName, 
                        trPath, 
                        logFilename, 
                        withoutProbes, 
                        defaultLibrary='',
                        defaultAdapter='', 
                        userId=0, 
                        projectId=0, 
                        subTEs=1, 
                        parametersShared=[],
                        stepByStep=False, 
                        breakpoint=False, 
                        testId=0, 
                        runningAgents=[], 
                        runningProbes=[], 
                        channelId=False, 
                        testLocation='', 
                        taskUuid=''):
    """
    Creates and returns a test suite executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['test-properties']
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
  
    srcTest = dataTest['test-definition']
    
    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = TestModelCommon.loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)
    missingImagesOut = TestModelCommon.loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs() )
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

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

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
    te.append( TestModelCommon.CODE_PROBES ) 
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
    te.append( Common.indent(TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )
    te.append(""" 
	TestProperties.instance().initAtRunTime(cache=Cache())
""")
    te.append( TestModelCommon.TEST_SUMMARY ) 
    te.append( TestModelCommon.TEST_SUMMARY_TA ) 
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
	TLX.instance().log_testunit_internal(message = 'Loading modules...\\nExtra[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTUNIT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

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
    te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
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

def createTestAbstract (	dataTest, 
                            userName, 
                            testName, 
                            trPath, 
                            logFilename, 
                            withoutProbes, 
                            defaultLibrary='',
                            defaultAdapter='', 
                            userId=0, 
                            projectId=0, 
                            subTEs=1, 
                            parametersShared=[], 
                            stepByStep=False, 
                            breakpoint=False, 
                            testId=0, 
                            runningAgents=[], 
                            runningProbes=[], 
                            channelId=False, 
                            testLocation='', 
                            taskUuid=''):
    """
    Creates and returns a test abstract executable 

    @param dataTest:
    @type dataTest:

    @return:
    @rtype: string
    """
    properties = dataTest['test-properties']
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

    srcTest = dataTest['test-definition']
    
    projectName = ProjectsManager.instance().getProjectName(prjId=projectId)
    
    # prepare datasets
    missingDataset = TestModelCommon.loadDataset(parameters=parameters, user=userName)
    missingDatasetOut = TestModelCommon.loadDataset(parameters=parametersOut, inputs=False, user=userName)

    # prepare images
    missingImages = TestModelCommon.loadImages(parameters=parameters, user=userName)
    missingImagesOut = TestModelCommon.loadImages(parameters=parametersOut, user=userName)

    # te construction
    te = []
    # import python libraries
    te.append( TestModelCommon.IMPORT_PY_LIBS )

    # import static arguments
    te.append( TestModelCommon.getStaticArgs() )
    
    te.append( """taskuuid_ = '%s'\n""" % taskUuid )
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

    te.append(TestModelCommon.IMPORT_INTRO)
    
    # import test executor libraries
    te.append(TestModelCommon.IMPORT_TE_LIBS)

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

TLX.initialize(task_uuid=taskuuid_, path = result_path, name = log_filename, user_ = user_, testname_ = test_name, id_ = test_id,
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
    te.append( TestModelCommon.CODE_PROBES ) 
    te.append("""	__PROBES__ = %s""" % probes )
    te.append("""	
	TestProperties.instance().initAtRunTime(cache=Cache())
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
    te.append( Common.indent(code=TestModelCommon.INPUT_CUSTOM) )
    te.append( Common.indent(TestModelCommon.INPUT_CACHE) )
    te.append(""" 
	TestProperties.instance().initAtRunTime(cache=Cache())
""")
    te.append( TestModelCommon.TEST_SUMMARY ) 
    te.append( TestModelCommon.TEST_SUMMARY_TA ) 
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
	TLX.instance().log_testabstract_internal(message = 'Loading modules...\\nExtra[Adapters=%s, Libraries=%s]\\nGeneric[Adapters=%s, Libraries=%s]', component = 'TESTABSTRACT', bold=False, italic=True, fromlevel=LEVEL_TE, tolevel=LEVEL_USER)
""" % (SutAdapters, SutLibraries, SutAdaptersGeneric, SutLibrariesGeneric) ) 
    
    te.append("""
	TestLibrary.setVersionGeneric('%s') 
	TestAdapter.setVersionGeneric('%s')   
""" %(SutLibrariesGeneric, SutAdaptersGeneric))

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
    te.append(Common.indent("TESTCASE(suffix=None, testName='%s' % description('name') ).execute()"  ))
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