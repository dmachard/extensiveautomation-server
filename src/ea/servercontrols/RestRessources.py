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

from pycnic.core import Handler
from pycnic.errors import HTTP_401, HTTP_400, HTTP_500, HTTP_403, HTTP_404

import wrapt
import platform
import os
import yaml
import json
import pathlib

from ea.libs import Settings
from ea.serverengine import (Context,
                             ProjectsManager,
                             TaskManager,
                             AgentsManager,
                             UsersManager,
                             HelperManager)
from ea.serverrepositories import (RepoAdapters,
                                   RepoTests,
                                   RepoArchives)

from ea.libs.FileModels import TestSuite as TestSuite
from ea.libs.FileModels import TestUnit as TestUnit
from ea.libs.FileModels import TestPlan as TestPlan


def _get_user(request):
    """
    Lookup a user session or return None if one doesn't exist
    """
    sess_id = request.cookies.get("session_id")
    if sess_id is None:
        # new in v17, checking authorization header
        authorization = request.get_header(name="Authorization", default=None)
        if authorization is not None:
            userP = Context.instance().apiBasicAuthorization(authorization=authorization)
            if userP is None:
                raise HTTP_401("Invalid credentials")
            else:
                return userP
        else:
            raise HTTP_401("Authorization header not detected")
        # end of new
    else:
        if sess_id in Context.instance().getSessions():
            return Context.instance().getSessions()[sess_id]
        else:
            raise HTTP_401("Invalid session")

def _check_project_permissions(user_login, project_id):
    """
    Look up project
    """
    try:
        project_id = int(project_id)
    except BaseException:
        raise HTTP_400(
            "Invalid workspace id (Id=%s) provided in request, int expected" %
            str(project_id))

    # get the project id according to the name and checking permissions
    project_authorized = ProjectsManager.instance().checkProjectsAuthorization(user=user_login,
                                                                               projectId=project_id)
    if not project_authorized:
        raise HTTP_403('Permission denied to this workspace')

def fix_encoding_uri_param(p):
    try:
        p = p.encode("latin1").decode()
    except UnicodeError:
        pass
    return p
    
class EmptyValue(Exception):
    pass

class HandlerCORS(Handler):
    def options(self, *args):
        return {}
        
class FilesHandler(HandlerCORS):
    """/v1/files"""
    def get(self, file_path):
        """get files"""
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.args.get("workspace", 1)
            file_path = fix_encoding_uri_param(file_path)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Invalid request provided (%s ?)" % e)

        _check_project_permissions(
            user_login=user_profile['login'],
            project_id=projectId)

        # avoid directory traversal
        file_path = os.path.normpath("/" + file_path)

        success, _, _, _, _, content, _, _= RepoTests.instance().getFile(pathFile=file_path,
                                                                         binaryMode=True,
                                                                         project=projectId,
                                                                         addLock=False,
                                                                         b64encode=True)
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to download file")

        return {"cmd": self.request.path, "file-content": content}
    def delete(self, file_path):
        """delete file"""
        user_profile = _get_user(request=self.request)

        if user_profile['monitor']:
            raise HTTP_403("Access refused")
            
        try:
            projectId = self.request.args.get("workspace", 1)
            file_path = fix_encoding_uri_param(file_path)
        except Exception as e:
            raise HTTP_400("Invalid request provided (%s ?)" % e)
            
        # avoid directory traversal
        filePath = os.path.normpath("/" + file_path)
        
        success = RepoTests.instance().delFile(pathFile=filePath,
                                               project=projectId,
                                               supportSnapshot=False)
        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to delete file")
            
        return {"cmd": self.request.path,
                "message": "success"}                
    def post(self, file_path):
        """upload file"""
        user_profile = _get_user(request=self.request)

        if user_profile['monitor']:
            raise HTTP_403("Access refused")

        try:
            projectId = self.request.args.get("workspace", 1)
            file_path = fix_encoding_uri_param(file_path)
            
            fileContent = self.request.data.get("file-content")
            if fileContent is None:
                raise EmptyValue("Please specify a file content")
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Invalid request provided (%s ?)" % e)

        _check_project_permissions(
            user_login=user_profile['login'],
            project_id=projectId)

        try:
            filePath = os.path.normpath(file_path)
            p  = pathlib.Path(filePath)
            
            fileExt = p.suffix[1:]
            fileName = p.stem
            filePath = filePath.rsplit("%s%s" %(p.stem, p.suffix))[0]
        except Exception as e:
            raise HTTP_403('Invalid file name: %s' % e)
            
        success, _, _, _, _, _, _, _, _ = RepoTests.instance().uploadFile(pathFile=filePath,
                                                                        nameFile=fileName,
                                                                        extFile=fileExt,
                                                                        contentFile=fileContent,
                                                                        login=user_profile['login'],
                                                                        project=projectId,
                                                                        overwriteFile=True,
                                                                        createFolders=True,
                                                                        lockMode=False,
                                                                        binaryMode=True)

        if success != Context.instance().CODE_OK:
            raise HTTP_500("Unable to upload file")
            
        return {"cmd": self.request.path,
                "message": "success"}
                
class ExecutionsHandler(HandlerCORS):
    """/v1/executions"""
    def get(self):
        """get executions"""
        user_profile = _get_user(request=self.request)

        try:
            projectId = self.request.args.get("workspace", 1)

            testId = self.request.args.get("id")
            if testId is None:
                raise HTTP_400("Please specify execution id")

            _log_index = self.request.args.get("log_index", 0)
            
            projectId = int(projectId)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Bad request provided (%s ?)" % e)

        _check_project_permissions(user_login=user_profile['login'],
                                   project_id=projectId)

        founded, testPath = RepoArchives.instance().findTrInCache(projectId=projectId,
                                                                  testId=testId)
        if founded == Context.instance().CODE_NOT_FOUND:
            raise HTTP_404('Test result not found')

        state = RepoArchives.instance().getTrState(trPath=testPath)
        verdict = RepoArchives.instance().getTrEndResult(trPath=testPath)
        logs, logs_index = RepoArchives.instance().getTrLogs(trPath=testPath,
                                                         log_index=_log_index)
        return {"cmd": self.request.path,
                'execution-id': testId,
                'status': state,
                'verdict': verdict,
                'logs': logs,
                'logs-index': logs_index}
                
class JobsHandler(HandlerCORS):
    """/v1/jobs"""
    def post(self):
        """create job"""
        user_profile = _get_user(request=self.request)

        projectId = self.request.args.get("workspace", 1)
        
        try:
            yamlFile = self.request.data.get("yaml-file")
            if yamlFile is None:
                raise EmptyValue("Please specify a yaml file")
            
            yamlContent = self.request.data.get("yaml-content", "") 

            scheduleId = self.request.data.get("schedule-id", 0)
            _scheduleAt = self.request.data.get("schedule-at")
            _scheduleRepeat = self.request.data.get("schedule-repeat", 0)
            _debugEnabled = self.request.data.get("debug-enabled")
            _fromTime = self.request.data.get("from-time")
            _toTime = self.request.data.get("to-time")

            _testInputs = self.request.data.get("file-parameters")

            projectId = int(projectId)
            scheduleId = int(scheduleId)
        except EmptyValue as e:
            raise HTTP_400("%s" % e)
        except Exception as e:
            raise HTTP_400("Invalid request provided (%s ?)" % e)

        # checking input
        if _testInputs is not None:
            if not isinstance(_testInputs, list):
                raise HTTP_400(
                    "Invalid parameters provided in request, list expected")
            for inp in _testInputs:
                if not isinstance(inp, dict):
                    raise HTTP_400(
                        "Invalid parameters provided in request, list of dict expected")
                if not ("name" in inp and "type" in inp and "value" in inp):
                    raise HTTP_400(
                        "Invalid parameters provided in request")

        # run a test not save; change the project id to the default
        if projectId == 0:
            projectId = ProjectsManager.instance().getDefaultProjectForUser(
                user=user_profile['login'])

        _check_project_permissions(
            user_login=user_profile['login'],
            project_id=projectId)

        try:
            if yamlFile.startswith("//"):
                yamlFile = yamlFile[1:]
            yamlFile = os.path.normpath(yamlFile)
            p  = pathlib.Path(yamlFile)
            
            fileExtension = p.suffix[1:]
            fileName = p.stem
            filePath = yamlFile.rsplit("%s%s" %(p.stem, p.suffix))[0]
        except Exception as e:
            raise HTTP_403('Invalid yaml file: %s' % e)
        
        if len(yamlContent):
            try:
                res = yaml.safe_load(yamlContent)
            except Exception as e:
                raise HTTP_403('Invalid yaml content: %s' % e)
        
        else:
            try:
                file_path = "%s/%s/%s/%s.%s" % (RepoTests.instance().testsPath,
                                                projectId,
                                                filePath,
                                                fileName,
                                                fileExtension)
                # read the file
                with open(file_path, "r") as f:
                    doc_yaml = f.read()
                    
                res = yaml.safe_load(doc_yaml)
            except Exception as e:
                raise HTTP_403('Invalid yaml file: %s' % e)   

        try:
            # just for backward compatibility
            if "testplan" in res:
                testextension = "tpx"
                testfile = res["testplan"]
            elif "testglobal" in res:
                testextension = "tgx"
                testfile = res["testglobal"]
            elif "testsuite" in res:
                testextension = "tsx"
            elif "testunit" in res:
                testextension = "tux"
            # end of backward compatibility
                
            elif "python" in res:
                testextension = "tsx"   
            elif "actions" in res:
                testextension = "tpx"
                testfile = res["actions"]                        
            else:
                raise Exception("invalid yaml format")
              
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

            if testextension in ["tpx", "tgx"]:
                doc = TestPlan.DataModel()
            
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
                tests = doc.getSorted()
                
                if testextension == "tpx":
                    success, error_msg = RepoTests.instance().addtf2tp(data_=tests)
                    if success != Context.instance().CODE_OK:
                        raise HTTP_500(
                            'Unable to prepare test plan: %s' %
                            error_msg)
                else:
                    success, error_msg, tests = RepoTests.instance().addtf2tg(data_=tests)
                    if success != Context.instance().CODE_OK:
                        raise HTTP_500(
                            'Unable to prepare test global: %s' %
                            error_msg)    
                            
                            
            testData = {'test-properties': testprops,
                        'test-extension': testextension}
            if testextension == "tsx":
                if "python" in res:
                    testData['test-definition'] = res["python"]
                else:
                    testData['test-definition'] = res["testsuite"]
                testData['test-execution'] = ""
            elif testextension == "tux":
                testData['test-definition'] = res["testunit"]
            else:
                testData['test-execution'] = tests
        except Exception as e:
            raise HTTP_500('Unable to decode yaml: %s' % e)
                

        # now we can create the task
        
        debugEnabled = False
        fromTime = (0, 0, 0, 0, 0, 0)
        toTime = (0, 0, 0, 0, 0, 0)
        message = "success"
        scheduleAt = (0, 0, 0, 0, 0, 0)

        if _debugEnabled is not None:
            debugEnabled = _debugEnabled
        if _fromTime is not None:
            fromTime = _fromTime
        if _toTime is not None:
            toTime = _toTime
        if _scheduleAt is not None:
            scheduleAt = _scheduleAt

        # personalize test description ?
        if _testInputs is not None:
            for newInp in _testInputs:
                if "scope" not in newInp:
                    newInp["scope"] = "local"
                for origInp in testData["test-properties"]['inputs-parameters']['parameter']:
                    if "scope" not in origInp:
                        origInp["scope"] = "local"

                    # if the param exist on the original test than overwrite
                    # them
                    if newInp["name"] == origInp["name"]:
                        origInp["value"] = newInp["value"]
                        origInp["type"] = newInp["type"]
                        origInp["scope"] = newInp["scope"]

        if not filePath.endswith(fileName):
            if len(filePath):
                _testPath = "%s/%s" % (filePath, fileName)
            else:
                _testPath = fileName
            _testPath = os.path.normpath(_testPath)
        else:
            _testPath = filePath

        task = TaskManager.instance().registerTask(
            testData=testData,
            testName=fileName,
            testPath=_testPath,
            testUserId=user_profile['id'],
            testUser=user_profile['login'],
            testId=0,
            testBackground=True,
            runAt=scheduleAt,
            runType=scheduleId,
            runNb=_scheduleRepeat,
            withoutProbes=False,
            debugActivated=debugEnabled,
            withoutNotif=False,
            noKeepTr=False,
            testProjectId=projectId,
            runFrom=fromTime,
            runTo=toTime,
            stepByStep=False,
            breakpoint=False,
            channelId=False
        )

        if task.lastError is not None:
            raise HTTP_500('ERROR: %s' % task.lastError)

        message = "success"
        if task.isRecursive():
            message = "recursive"
        if task.isPostponed():
            message = "postponed"
        if task.isSuccessive():
            message = "successive"
        return {"cmd": self.request.path,
                "message": message,
                "job-id": task.getId(),
                "execution-id": task.getTestID()}
