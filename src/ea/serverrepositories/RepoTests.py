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

import os
import sys
try:
    import scandir
except ImportError:  # for python3 support
    scandir = os
import yaml
import json

from ea.serverengine import (ProjectsManager)
from ea.serverinterfaces import EventServerInterface as ESI
from ea.libs.FileModels import TestSuite as TestSuite
from ea.libs.FileModels import TestUnit as TestUnit
from ea.libs.FileModels import TestPlan as TestPlan
from ea.serverrepositories import RepoManager
from ea.libs import Settings, Logger

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str

try:
    xrange
except NameError:  # support python3
    xrange = range


TS_ENABLED = "2"
TS_DISABLED = "0"


class RepoTests(RepoManager.RepoManager, Logger.ClassLogger):
    """
    Tests repository class
    """

    def __init__(self, context):
        """
        Repository manager for tests files
        """
        RepoManager.RepoManager.__init__(self,
                                         pathRepo='%s%s' % (Settings.getDirExec(),
                                                            Settings.get('Paths', 'tests')),
                                         extensionsSupported=[RepoManager.TEST_SUITE_EXT,
                                                              RepoManager.TEST_PLAN_EXT,
                                                              RepoManager.TEST_CONFIG_EXT,
                                                              RepoManager.TEST_DATA_EXT,
                                                              RepoManager.TEST_UNIT_EXT,
                                                              RepoManager.PNG_EXT,
                                                              #RepoManager.TEST_YAML_EXT,
                                                              RepoManager.TEST_GLOBAL_EXT],
                                         context=context)

        self.context = context

    def getTree(self, b64=False, project=1):
        """
        Returns tree
        """
        return self.getListingFilesV2(path="%s/%s" % (self.testsPath, str(project)),
                                      project=project, supportSnapshot=True)

    def addtf2tg(self, data_):
        """
        Add remote testplan, testsuites or testunit in the testglobal
        internal function
        """
        ret = (self.context.CODE_OK, "")
        alltests = []
        # read each test files in data
        for ts in data_:
            # can be missing with yaml format, new in v22
            if "type" not in ts:
                ts["type"] = "remote"
            if "enable" not in ts:
                ts["enable"] = "2"
            # end of new
            
            # backward compatibility
            if 'alias' not in ts:
                ts['alias'] = ''

            # extract project info
            prjName = str(ts['file']).split(":", 1)[0]
            ts.update({'testproject': prjName})

            # extract test name
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                filenameTs, fileExt = tmp[1].rsplit(".", 1)
            else:
                filenameTs, fileExt = tmp[0].rsplit(".", 1)

            # extract test path
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                testPath = "/%s" % tmp[0]
            else:
                testPath = "/"
            ts.update({'testpath': testPath})

            if ts['type'] == "remote" and ts['enable'] == TS_DISABLED:
                ts.update({'path': filenameTs, 'depth': 1})
                alltests.append(ts)

            if ts['type'] == "remote" and ts['enable'] == TS_ENABLED:
                # extract the project name then the project id
                prjID = 0
                absPath = ''
                try:
                    prjName, absPath = ts['file'].split(':', 1)
                except Exception as e:
                    self.error("unable to extract project name: %s" % str(e))
                    ret = (
                        self.context.CODE_NOT_FOUND, "ID=%s %s" %
                        (ts['id'], ts['file']))
                    break
                else:
                    prjID = ProjectsManager.instance().getProjectID(name=prjName)

                    # prepare data model according to the test extension
                    if absPath.endswith(RepoManager.TEST_SUITE_EXT):
                        doc = TestSuite.DataModel()
                    elif absPath.endswith(RepoManager.TEST_UNIT_EXT):
                        doc = TestUnit.DataModel()
                    elif absPath.endswith(RepoManager.TEST_PLAN_EXT):
                        doc = TestPlan.DataModel()
                    
                    elif absPath.endswith(RepoManager.TEST_YAML_EXT):
                        pass
                    
                    else:
                        self.error("unknown test extension file: %s" % absPath)
                        ret = (
                            self.context.CODE_NOT_FOUND, "ID=%s %s" %
                            (ts['id'], ts['file']))
                        break

                    # new in v22
                    if absPath.endswith(RepoManager.TEST_YAML_EXT):
                        try:
                            # read the file
                            with open("%s/%s/%s" % (self.testsPath, prjID, absPath), "r") as f:
                                doc_yaml = f.read()
                            res = yaml.safe_load(doc_yaml)
                            
                            # add default props if missing
                            if "properties" not in res:
                                res["properties"] = {}
                                
                            # add default descriptions if missing
                            if "descriptions" not in res["properties"]:
                                res["properties"]["descriptions"] = {}
                                res["properties"]["descriptions"]["author"] = "undefined"
                                res["properties"]["descriptions"]["name"] = "undefined"
                                res["properties"]["descriptions"]["requirement"] = "undefined"
                                res["properties"]["descriptions"]["summary"] = "undefined"
                            
                            # add parameters if missing
                            if "parameters" not in res["properties"]:
                                res["properties"]["parameters"] = []
                                
                            # add default scope in main parameters
                            for p in res["properties"]["parameters"]:
                                if "scope" not in p:
                                    p["scope"] = "local"
                                if "value" not in p:
                                    p["value"] = ""
                                if "type" not in p:
                                    if p["value"] is None:
                                        p["type"] = "none"
                                        p["value"] = ""
                                    elif isinstance(p["value"], bool):
                                        p["type"] = "bool"
                                        p["value"] = "%s" % p["value"]
                                    elif isinstance(p["value"], int):
                                        p["type"] = "int"
                                        p["value"] = "%s" % p["value"]
                                    elif isinstance(p["value"], list) or isinstance(p["value"], dict):
                                        p["type"] = "json"
                                        p["value"] = json.dumps(p["value"])
                                    else:
                                        p["type"] = "text"
                                
                            testprops = {}
                            testprops["inputs-parameters"] = {}
                            testprops["inputs-parameters"]["parameter"] = res["properties"]["parameters"]
                            testprops["descriptions"] = {}
                            testprops["descriptions"]["description"] = []
         
                            for k,v in res["properties"]["descriptions"].items():
                                s = { 'key': k, 'value': v }
                                testprops["descriptions"]["description"].append(s)
                                                        
                            # decode file
                            if "testsuite" in res:
                                fileExt = "tsx"
                                doc = TestSuite.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["testsuite"]
                                doc.testexec = ""
                                ts["extension"] = "tsx"
                                
                            elif "python" in res:
                                fileExt = "tsx"
                                doc = TestSuite.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["python"]
                                doc.testexec = ""
                                ts["extension"] = "tsx"  
                                
                            elif "testunit" in res:
                                fileExt = "tux"
                                doc = TestUnit.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["testunit"]
                                ts["extension"] = "tux"
                            
                            elif "testplan" in res or "actions" in res:
                                fileExt = "tpx"
                                doc = TestPlan.DataModel()
                                doc.properties['properties'] = testprops

                                if "actions" in res:
                                    testfile = res["actions"]     
                                else:
                                    testfile = res["testplan"]    
                                testplan = {}
                                testplan['testplan'] = { 'testfile': [] }
                                i = 1
                                for tp in testfile:
                                    # add parameters if missing
                                    if "parameters" not in tp:
                                        tp["parameters"] = []
                                    # add default scope in main parameters
                                    for p in tp["parameters"]:
                                        if "scope" not in p:
                                            p["scope"] = "local"
                                        if "value" not in p:
                                            p["value"] = ""
                                        if "type" not in p:
                                            if p["value"] is None:
                                                p["type"] = "none"
                                                p["value"] = ""
                                            elif isinstance(p["value"], bool):
                                                p["type"] = "bool"
                                                p["value"] = "%s" % p["value"]
                                            elif isinstance(p["value"], int):
                                                p["type"] = "int"
                                                p["value"] = "%s" % p["value"]
                                            elif isinstance(p["value"], list) or isinstance(p["value"], dict):
                                                p["type"] = "json"
                                                p["value"] = json.dumps(p["value"])
                                            else:
                                                p["type"] = "text"
                                            
                                    if "id" not in tp:
                                        tp["id"] = "%s" % i
                                    if isinstance(tp["id"], int):
                                        tp["id"] = str(tp["id"])
                                    if "parent" not in tp:
                                        tp["parent"] = "0"
                                    if isinstance(tp["parent"], int):
                                        tp["parent"] = str(tp["parent"])
                                        
                                    if "parent-condition" not in tp:
                                        tp["parent-condition"] = "0"
                                    else:
                                        if tp["parent-condition"] == "success":
                                            tp["parent-condition"] = "0"
                                        else:
                                            tp["parent-condition"] = "1"
                                        tp["parent-condition"] = str(tp["parent-condition"])
                        
                                    if "description" in tp:
                                        tp["alias"] = tp["description"]
                        
                                    i+=1
                                        
                                    tf_descr = [ {"key": "author", "value": "undefined"},
                                                 {"key": "summary", "value": "undefined"}, 
                                                 {"key": "name", "value": "undefined"},
                                                 {"key": "requirement", "value": "undefined"}]
                                    tf_prop = {"properties": {"descriptions": { "description": tf_descr},
                                                              "inputs-parameters": {} }}
                                    tf_prop["properties"]["inputs-parameters"]["parameter"] = tp["parameters"]
                                    tp.update(tf_prop)
                                    testplan['testplan']['testfile'].append(tp)
                                
                                doc.testplan = testplan
                                
                            elif "testglobal" in res:
                                raise Exception("tg - bad yaml format")
                                
                            res = True
                        except Exception as e:
                            self.error("yaml error: %s" % e)
                            res = False
                    # end of new v22
                    
                    else:   
                        # load the data model
                        res = doc.load(
                            absPath="%s/%s/%s" %
                            (self.testsPath, prjID, absPath))
                    if not res:
                        ret = (self.context.CODE_NOT_FOUND, absPath)
                        break
                    else:
                        # update/add test parameters with the main parameters
                        # of the test global
                        self.__updatetsparams(currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                              newParam=ts['properties']['inputs-parameters']['parameter'])
                        ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']

                        if fileExt == RepoManager.TEST_SUITE_EXT:
                            ts.update({'test-definition': doc.testdef,
                                       'test-execution': doc.testexec,
                                       'path': filenameTs})
                            alltests.append(ts)
                        elif fileExt == RepoManager.TEST_UNIT_EXT:
                            ts.update({'test-definition': doc.testdef,
                                       'path': filenameTs})
                            alltests.append(ts)
                        elif fileExt == RepoManager.TEST_PLAN_EXT:
                            self.trace('Reading sub test plan')
                            sortedTests = doc.getSorted()
                            subret, suberr = self.addtf2tp(
                                data_=sortedTests, tpid=ts['id'])
                            ret = (subret, suberr)
                            if subret != self.context.CODE_OK:
                                del sortedTests
                                break
                            else:
                                alias_ts = ts['alias']
                                # fix issue encode, ugly fix
                                try:
                                    alias_ts = str(alias_ts)
                                except UnicodeEncodeError:
                                    pass
                                else:
                                    try:
                                        alias_ts = alias_ts.encode('utf8')
                                    except UnicodeDecodeError:
                                        alias_ts = alias_ts.decode('utf8')
                                # end of fix

                                # add testplan separator
                                alltests.extend([{'extension': 'tpx',
                                                  'separator': 'started',
                                                  'enable': "0",
                                                  'depth': 1,
                                                  'id': ts['id'],
                                                  'testname': filenameTs,
                                                  'parent': ts['parent'],
                                                  'alias': alias_ts,
                                                  'properties': ts['properties'],
                                                  "testpath": ts['testpath'],
                                                  "testproject": ts['testproject']}])

                                # update all subtest with parameters from
                                # testplan
                                for i in xrange(len(sortedTests)):
                                    cur_param = sortedTests[i]['properties']['inputs-parameters']['parameter']
                                    new_param = ts['properties']['inputs-parameters']['parameter']
                                    self.__updatetsparams(currentParam=cur_param,
                                                          newParam=new_param)
                                self.trace('Read sub test plan finished')

                                alltests.extend(sortedTests)
                                alltests.extend([{
                                    'extension': 'tpx',
                                    'separator': 'terminated',
                                    'enable': "0",
                                    'depth': 1,
                                    'id': ts['id'],
                                    'testname': filenameTs,
                                    'parent': ts['parent'],
                                    'alias': alias_ts}])
        return ret + (alltests,)

    def addtf2tp(self, data_, tpid=0):
        """
        Add remote testsuites or testunit in the testplan
        Internal function
        """
        ret = (self.context.CODE_OK, "")
        for ts in data_:
            
            # can be missing with yaml format, new in v22
            if "type" not in ts:
                ts["type"] = "remote"
            if "enable" not in ts:
                ts["enable"] = "2"
            # end of new
            
            # extract project info
            prjName = str(ts['file']).split(":", 1)[0]
            ts.update({'testproject': prjName})

            # extract test name
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                filenameTs, fileExt = tmp[1].rsplit(".", 1)
            else:
                filenameTs, fileExt = tmp[0].rsplit(".", 1)

            # extract test path
            tmp = str(ts['file']).split(":", 1)[1].rsplit("/", 1)
            if len(tmp) > 1:
                testPath = "/%s" % tmp[0]
            else:
                testPath = "/"
            ts.update({'testpath': testPath})

            if ts['type'] == "remote" and ts['enable'] == TS_DISABLED:
                ts.update({'path': filenameTs, 'tpid': tpid})
                # backward compatibility
                self.__fixAliasTp(ts=ts)

            elif ts['type'] == "remote" and ts['enable'] == TS_ENABLED:
                prjID = 0
                absPath = ''
                try:
                    prjName, absPath = ts['file'].split(':', 1)
                except Exception as e:
                    self.error("unable to extract project name: %s" % str(e))
                    ret = (
                        self.context.CODE_NOT_FOUND, "ID=%s %s" %
                        (ts['id'], ts['file']))
                    break
                else:
                    prjID = ProjectsManager.instance().getProjectID(name=prjName)
                    if absPath.endswith(RepoManager.TEST_SUITE_EXT):
                        doc = TestSuite.DataModel()
                    else:
                        doc = TestUnit.DataModel()
                        
                    if absPath.endswith(RepoManager.TEST_YAML_EXT):
                        try:
                            # read the file
                            with open("%s/%s/%s" % (self.testsPath, prjID, absPath), "r") as f:
                                doc_yaml = f.read()
                            res = yaml.safe_load(doc_yaml)
                            
                            # add default props if missing
                            if "properties" not in res:
                                res["properties"] = {}
                                
                            # add default descriptions if missing
                            if "descriptions" not in res["properties"]:
                                res["properties"]["descriptions"] = {}
                                
                            if "author" not in res["properties"]["descriptions"]:
                                res["properties"]["descriptions"]["author"] = "undefined"
                                
                            if "name" not in res["properties"]["descriptions"]:
                                res["properties"]["descriptions"]["name"] = "undefined"
                                
                            if "requirement" not in res["properties"]["descriptions"]:
                                res["properties"]["descriptions"]["requirement"] = "undefined"
                                
                            if "summary" not in res["properties"]["descriptions"]:
                                res["properties"]["descriptions"]["summary"] = "undefined"
                                
                            # add parameters if missing
                            if "parameters" not in res["properties"]:
                                res["properties"]["parameters"] = []    
                                
                            # add default scope in main parameters
                            for p in res["properties"]["parameters"]:
                                if "scope" not in p:
                                    p["scope"] = "local"
                                if "value" not in p:
                                    p["value"] = ""
                                if "type" not in p:
                                    if p["value"] is None:
                                        p["type"] = "none"
                                        p["value"] = ""
                                    elif isinstance(p["value"], bool):
                                        p["type"] = "bool"
                                        p["value"] = "%s" % p["value"]
                                    elif isinstance(p["value"], int):
                                        p["type"] = "int"
                                        p["value"] = "%s" % p["value"]
                                    elif isinstance(p["value"], list) or isinstance(p["value"], dict):
                                        p["type"] = "json"
                                        p["value"] = json.dumps(p["value"])
                                    else:
                                        p["type"] = "text"
                                
                            testprops = {}
                            testprops["inputs-parameters"] = {}
                            testprops["inputs-parameters"]["parameter"] = res["properties"]["parameters"]
                            testprops["descriptions"] = {}
                            testprops["descriptions"]["description"] = []

                            for k,v in res["properties"]["descriptions"].items():
                                s = { 'key': k, 'value': v }
                                testprops["descriptions"]["description"].append(s)
                                                        
                            # decode file
                            if "testsuite" in res:
                                fileExt = "tsx"
                                doc = TestSuite.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["testsuite"]
                                doc.testexec = ""
                                ts["extension"] = "tsx"
                            elif "python" in res:
                                fileExt = "tsx"
                                doc = TestSuite.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["python"]
                                doc.testexec = ""
                                ts["extension"] = "tsx"
                            else:
                                fileExt = "tux"
                                doc = TestUnit.DataModel()
                                doc.properties['properties'] = testprops
                                doc.testdef = res["testunit"]
                                ts["extension"] = "tux"
                            
                            res = True
                        except Exception as e:
                            self.error("yaml error: %s" % e)
                            res = False
                    
                    else:
                        res = doc.load(
                            absPath="%s/%s/%s" % (self.testsPath, prjID, absPath))
                            
                    if not res:
                        ret = (
                            self.context.CODE_NOT_FOUND, "ID=%s %s" %
                            (ts['id'], ts['file']))
                        break
                    else:

                        #
                        self.__updatetsparams(currentParam=doc.properties['properties']['inputs-parameters']['parameter'],
                                              newParam=ts['properties']['inputs-parameters']['parameter'])
                        ts['properties']['inputs-parameters'] = doc.properties['properties']['inputs-parameters']

                        if fileExt == RepoManager.TEST_SUITE_EXT:
                            ts.update({'test-definition': doc.testdef,
                                       'test-execution': doc.testexec,
                                       'path': filenameTs, 'tpid': tpid})
                        else:
                            ts.update({'test-definition': doc.testdef,
                                       'path': filenameTs, 'tpid': tpid})

                        # backward compatibility
                        self.__fixAliasTp(ts=ts)
            else:
                pass
        return ret

    def __fixAliasTp(self, ts):
        """
        """
        # backward compatibility
        if 'alias' not in ts:
            ts['alias'] = ''

        # fix issue encode, ugly fix
        try:
            ts['alias'] = str(ts['alias'])
        except UnicodeEncodeError:
            pass
        else:
            try:
                ts['alias'] = ts['alias'].encode('utf8')
            except UnicodeDecodeError:
                ts['alias'] = ts['alias'].decode('utf8')

    def __updatetsparams(self, currentParam, newParam):
        """
        Update current test parameters with main parameter
        Internal function
        """
        for i in xrange(len(currentParam)):
            for np in newParam:
                if np['name'] == currentParam[i]['name'] and currentParam[i]['type'] != "alias":
                    currentParam[i] = np
        # adding new param
        newparams = self.__getnewparams(currentParam, newParam)
        for np in newparams:
            currentParam.append(np)

    def __getnewparams(self, currentParam, newParam):
        """
        New param to add
        Internal function
        """
        toAdd = []
        for np in newParam:
            isNew = True
            for cp in currentParam:
                if np['name'] == cp['name']:
                    isNew = False
            if isNew:
                toAdd.append(np)
        return toAdd

    def findInstance(self, filePath, projectName, projectId):
        """
        Find a test instance according to the path of the file
        """
        self.trace("Find tests instance: %s" % filePath)

        if filePath.startswith("/"):
            filePath = filePath[1:]

        tests = []
        try:
            for path, _, files in os.walk(
                    "%s/%s" % (self.testsPath, projectId)):
                for name in files:
                    if name.endswith(RepoManager.TEST_PLAN_EXT) or name.endswith(
                            RepoManager.TEST_GLOBAL_EXT):
                        doc = TestPlan.DataModel()
                        res = doc.load(absPath=os.path.join(path, name))
                        if not res:
                            self.error(
                                'unable to read test plan: %s' %
                                os.path.join(
                                    path, name))
                        else:
                            testsfile = doc.testplan['testplan']['testfile']
                            t = {"instance": 0}
                            testFound = False
                            for i in xrange(len(testsfile)):
                                if testsfile[i]['type'] == 'remote':
                                    if "%s:%s" % (
                                            projectName, filePath) == testsfile[i]['file']:
                                        p = os.path.join(path, name)
                                        p = p.split(
                                            "%s/%s" %
                                            (self.testsPath, projectId))[1]
                                        t['test'] = p
                                        t['instance'] += 1
                                        testFound = True
                            if testFound:
                                tests.append(t)

        except Exception as e:
            self.error("unable to find test instance: %s" % e)
            return (self.context.CODE_ERROR, tests)
        return (self.context.CODE_OK, tests)

    def getFile(self, pathFile, binaryMode=True, project='', addLock=True, login='',
                forceOpen=False, readOnly=False, b64encode=True):
        """
        New in v17
        Return the file ask by the tester
        and check the file content for testplan or testglobal
        """
        ret = RepoManager.RepoManager.getFile(self, pathFile=pathFile,
                                              binaryMode=binaryMode,
                                              project=project,
                                              addLock=addLock,
                                              login=login,
                                              forceOpen=forceOpen,
                                              readOnly=readOnly,
                                              b64encode=b64encode)
        result, path_file, name_file, ext_file, project, _, locked, locked_by = ret
        if result != self.context.CODE_OK:
            return ret

        if ext_file in [RepoManager.TEST_PLAN_EXT,
                        RepoManager.TEST_GLOBAL_EXT]:
            self.trace("get specific file of type %s" % ext_file)
            # checking if all links are good
            doc = TestPlan.DataModel()
            absPath = "%s/%s/%s" % (self.testsPath, project, pathFile)
            if not doc.load(absPath=absPath):
                self.error(
                    'unable to read test plan: %s/%s/%s' %
                    (self.testsPath, project, pathFile))
                return ret
            else:
                testsfile = doc.testplan['testplan']['testfile']

                # get all projcts
                _, projectsList = ProjectsManager.instance().getProjectsFromDB()

                # read all tests file defined in the testplan or testglobal
                for i in xrange(len(testsfile)):
                    # update only remote file
                    if testsfile[i]['type'] == 'remote':
                        # mark as missing ?
                        prjName, testPath = testsfile[i]['file'].split(":", 1)
                        prjId = 0
                        for prj in projectsList:
                            if prj["name"] == prjName:
                                prjId = int(prj["id"])
                                break

                        if not os.path.exists(
                                "%s/%s/%s" % (self.testsPath, prjId, testPath)):
                            testsfile[i]["control"] = "missing"
                        else:
                            testsfile[i]["control"] = ""

                # finally save the change
                doc.write(absPath=absPath)
                return (result, path_file, name_file, ext_file,
                        project, doc.getRaw(), locked, locked_by)
            return ret
        else:
            return ret

    # dbr13 >>
    def getTestFileUsage(self, file_path, project_id, user_login):
        """
        Find test file usage in test plan or testglobal
        """
        project_name = ProjectsManager.instance().getProjectName(prjId=project_id)
        projects = ProjectsManager.instance().getProjects(user=user_login)

        usage_path_file = '%s:/%s' % (project_name, file_path)
        usage_path_file = os.path.normpath(usage_path_file)

        usage_path_file2 = '%s:%s' % (project_name, file_path)
        usage_path_file2 = os.path.normpath(usage_path_file2)

        extFile = file_path.rsplit('.')[-1]

        search_result = []

        for proj in projects:
            project_id = proj['project_id']
            tmp_proj_info = {}
            tmp_proj_info.update(proj)
            tmp_proj_info['content'] = []
            tmp_content = tmp_proj_info['content']
            _, _, listing, _ = self.getTree(project=project_id)
            tests_tree_update_locations = self.getTestsForUpdate(listing=listing,
                                                                 extFileName=extFile)
            files_paths = self.get_files_paths(
                tests_tree=tests_tree_update_locations)

            for file_path in files_paths:

                if file_path.endswith(RepoManager.TEST_PLAN_EXT):
                    doc = TestPlan.DataModel()
                elif file_path.endswith(RepoManager.TEST_GLOBAL_EXT):
                    doc = TestPlan.DataModel(isGlobal=True)
                else:
                    return "Bad file extension: %s" % file_path

                absPath = '%s%s%s' % (self.testsPath, project_id, file_path)
                doc.load(absPath=absPath)
                test_files_list = doc.testplan['testplan']['testfile']
                line_ids = []

                for test_file in test_files_list:
                    if usage_path_file == os.path.normpath(test_file['file']):
                        line_ids.append(test_file['id'])
                    if usage_path_file2 == os.path.normpath(test_file['file']):
                        line_ids.append(test_file['id'])

                tmp_content.append(
                    {'file_path': file_path, 'lines_id': line_ids}) if line_ids else None

            search_result.append(tmp_proj_info)
        return search_result

    # dbr13 >>
    def updateLinkedScriptPath(self, project, mainPath, oldFilename, extFilename,
                               newProject, newPath, newFilename, newExt, user_login,
                               file_referer_path='', file_referer_projectid=0):
        """
        Fix linked test in testplan or testglobal
        Pull request by dbr13 and updated by dmachard
        """
        # get current project name and accessible projects list for currnet
        # user
        project_name = ProjectsManager.instance().getProjectName(prjId=project)
        new_project_name = ProjectsManager.instance().getProjectName(prjId=newProject)

        projects = ProjectsManager.instance().getProjects(user=user_login)

        updated_files_list = []

        new_test_file_name = '%s:/%s/%s.%s' % (new_project_name,
                                               newPath,
                                               newFilename,
                                               newExt)
        old_test_file_name = '%s:/%s/%s.%s' % (project_name,
                                               mainPath,
                                               oldFilename,
                                               extFilename)

        self.trace(
            "Update link - test path to search: %s" %
            old_test_file_name)
        self.trace(
            "Update link - replace the old one by the new path: %s" %
            new_test_file_name)

        for proj_id in projects:
            project_id = proj_id['project_id']
            _, _, listing, _ = self.getTree(project=project_id)

            tests_tree_update_locations = self.getTestsForUpdate(listing=listing,
                                                                 extFileName=extFilename)

            if len(file_referer_path) and int(
                    proj_id['project_id']) == int(file_referer_projectid):
                files_paths = self.get_files_paths(tests_tree=tests_tree_update_locations,
                                                   exceptions=[file_referer_path])
            else:
                files_paths = self.get_files_paths(
                    tests_tree=tests_tree_update_locations)

            for file_path in files_paths:
                # init appropriate data model for current file path
                if file_path.endswith(RepoManager.TEST_PLAN_EXT):
                    doc = TestPlan.DataModel()
                    ext_file_name = RepoManager.TEST_PLAN_EXT
                elif file_path.endswith(RepoManager.TEST_GLOBAL_EXT):
                    doc = TestPlan.DataModel(isGlobal=True)
                    ext_file_name = RepoManager.TEST_GLOBAL_EXT
                else:
                    return "Bad file extension: %s" % file_path

                absPath = '%s%s%s' % (self.testsPath,
                                      project_id,
                                      file_path)
                doc.load(absPath=absPath)
                test_files_list = doc.testplan['testplan']['testfile']

                is_changed = False
                for test_file in test_files_list:
                    if os.path.normpath(old_test_file_name) == os.path.normpath(
                            test_file['file']):
                        test_file['file'] = new_test_file_name
                        test_file['extension'] = extFilename
                        is_changed = True

                if is_changed:
                    file_content = doc.getRaw()

                    f_path_list = file_path.split('/')
                    path_file = '/'.join(f_path_list[:-1])
                    name_file = f_path_list[-1][:-4]

                    path_file = os.path.normpath(path_file)

                    self.uploadFile(pathFile=path_file,
                                    nameFile=name_file,
                                    extFile=ext_file_name,
                                    contentFile=file_content,
                                    login=user_login,
                                    project=project_id,
                                    overwriteFile=True,
                                    createFolders=False,
                                    lockMode=False,
                                    binaryMode=True,
                                    closeAfter=False)

                    # notify all connected users of the change
                    data = ('test', ("changed", {"modified-by": user_login,
                                                 "path": file_path,
                                                 "project-id": project_id}))
                    ESI.instance().notifyByUserAndProject(body=data,
                                                          admin=True,
                                                          monitor=True,
                                                          tester=True,
                                                          projectId=int(project_id))

                    # append the file modified to the list
                    updated_files_list.append(file_path)

        return updated_files_list

    def getTestsForUpdate(self, listing, extFileName):
        """
        """
        tests_list = []

        extDict = {
            RepoManager.TEST_UNIT_EXT: [RepoManager.TEST_GLOBAL_EXT,
                                        RepoManager.TEST_PLAN_EXT],
            RepoManager.TEST_PLAN_EXT: [RepoManager.TEST_GLOBAL_EXT],
            RepoManager.TEST_SUITE_EXT: [RepoManager.TEST_GLOBAL_EXT,
                                         RepoManager.TEST_PLAN_EXT],
            'all': [RepoManager.TEST_GLOBAL_EXT,
                    RepoManager.TEST_PLAN_EXT,
                    RepoManager.TEST_SUITE_EXT,
                    RepoManager.TEST_UNIT_EXT,
                    ]
        }

        for test in listing:
            if test['type'] == 'file':
                ext_test = test['name'].split('.')[-1]
                req_exts = extDict[extFileName]
                if extFileName in extDict and ext_test in req_exts:
                    tests_list.append(test)
            else:
                if test['type'] == 'folder':
                    tests_list.append(test)
                    tests_list[-1]['content'] = (self.getTestsForUpdate(listing=test['content'],
                                                                        extFileName=extFileName))
        return tests_list

    def get_files_paths(self, tests_tree, file_path='/', exceptions=[]):
        """
        """
        list_path = []
        for test in tests_tree:
            f_path = file_path

            if test['type'] == 'file':
                # ignore specific files ?
                exception_detected = False
                for ex in exceptions:
                    if ex == '%s%s' % (f_path, test['name']):
                        exception_detected = True
                        break

                if exception_detected:
                    continue
                list_path.append('%s%s' % (f_path, test['name']))
            else:
                f_path += '%s/' % test['name']
                list_path += self.get_files_paths(test['content'],
                                                  file_path=f_path,
                                                  exceptions=exceptions)
        return list_path

    # dbr13 <<

RepoTestsMng = None


def instance():
    """
    Returns the singleton
    """
    return RepoTestsMng


def initialize(context):
    """
    Instance creation
    """
    global RepoTestsMng
    RepoTestsMng = RepoTests(context=context)


def finalize():
    """
    Destruction of the singleton
    """
    global RepoTestsMng
    if RepoTestsMng:
        RepoTestsMng = None
