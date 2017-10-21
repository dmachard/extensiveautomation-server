#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -------------------------------------------------------------------
# This file is part of the extensive testing project
# Copyright (c) 2010-2017 Denis Machard
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
#
# Gfi Informatique, Inc., hereby disclaims all copyright interest in the
# extensive testing project written by Denis Machard
# 
# Author: Denis Machard
# Contact: d.machard@gmail.com
# Website: www.extensivetesting.org
# -------------------------------------------------------------------

try:
    from PyQt4.QtCore import ( QObject, pyqtSignal )         
except ImportError:
    from PyQt5.QtCore import ( QObject, pyqtSignal )  
    
from Core import Settings

import win32com.client as win32client
import pythoncom
import os
import time

class ComHpAlmClient(QObject):
    """
    COM HP ALM client
    """
    Error = pyqtSignal(object)
    TestsExported = pyqtSignal()
    ResultsExported = pyqtSignal()
    ConnectionOk = pyqtSignal()
    LogTestsStatus = pyqtSignal(str)
    LogResultsStatus = pyqtSignal(str)
    def __init__(self, parent, core):
        """
        """
        QObject.__init__(self, parent)

        self.__core = core
        self.qc_cx = None

        self.loadConfig()

    def loadConfig(self):
        """
        """
        self.login = self.core().settings().cfg()["credentials"]["login"]
        self.password = self.core().settings().cfg()["credentials"]["password"]
        self.url = self.core().settings().cfg()["qc-server"]["url"]
        self.domain = self.core().settings().cfg()["qc-server"]["domain"]
        self.project = self.core().settings().cfg()["qc-server"]["project"]

    def core(self):
        """
        """
        return self.__core

    def __splitpath(self, path):
        """
        """
        allparts = []
        while 1:
            parts = os.path.split(path)
            if parts[0] == path:  # sentinel for absolute paths
                allparts.insert(0, parts[0])
                break
            elif parts[1] == path: # sentinel for relative paths
                allparts.insert(0, parts[1])
                break
            else:
                path = parts[0]
                allparts.insert(0, parts[1])
        return allparts
    
    def testConnection(self, config={}):
        """
        """
        try:
            # connect
            self.logTestsStatus( "Connection to the COM API..." )
            pythoncom.CoInitialize()
            qc_cx = win32client.Dispatch("TDApiOle80.TDConnection")
            qc_cx.InitConnectionEx(self.url)
            qc_cx.Login(self.login, self.password)
            qc_cx.Connect(self.domain, self.project)
            self.logTestsStatus( "Connected" )
            
            
            # disconnect
            self.logTestsStatus("Disconnection from the COM API..." )
            qc_cx.Logout()
            qc_cx.ReleaseConnection()
            self.logTestsStatus("Disconnected" )
            self.ConnectionOk.emit()
        except pythoncom.com_error as e:
            hr,msg,exc,arg = e.args
            if exc is None:
                details = "HP connect missing!"
            else:  
                _, _, details, _, _, _ = exc
            self.logTestsStatus("Error on HP connection" )
            self.Error.emit( "%s: %s" % (msg, details) )
        except Exception as e:
            self.logTestsStatus("Error on HP connection" )
            self.Error.emit( "%s" % e )
    
    def addResultsInTestLab(self, testcases, config={}):
        """
        """
        try:
            # connect
            self.logResultsStatus( "Connection to the COM API..." )

            pythoncom.CoInitialize()
            qc_cx = win32client.Dispatch("TDApiOle80.TDConnection")
            qc_cx.InitConnectionEx(self.url)
            qc_cx.Login(self.login, self.password)
            qc_cx.Connect(self.domain, self.project)
            self.logResultsStatus( "Connected" )
            
            # find path folder in test lab
            self.logResultsStatus("Finding path in test lab..." )
            if config["Add_Folders"]:
                testsetpath="Root/%s" % ( config["TestSet_Path"] )
                testsetpath = os.path.normpath(testsetpath)
                testsetpathSplit = self.__splitpath(path=testsetpath)

                treeManager = qc_cx.TestSetTreeManager
                tl = "Root/"
                if len(testsetpathSplit) == 1:
                    testLabFolder = treeManager.NodeByPath(os.path.normpath(tl))
                
                for f in testsetpathSplit[1:]:
                    try:
                        testLabFolder = treeManager.NodeByPath(os.path.normpath("%s/%s" % (tl, f)))
                        tl = os.path.normpath("%s/%s" % (tl, f))
                    except pythoncom.com_error as e:
                        self.logResultsStatus("Creating folder %s in test lab..." % f )
                        testLabFolder = treeManager.NodeByPath(os.path.normpath("%s" % tl))
                        testLabFolder = testLabFolder.AddNode(f)
                        tl = os.path.normpath("%s/%s" % (tl, f))
            else:
                treeManager = qc_cx.TestSetTreeManager
                testsetpath="Root/%s" % ( config["TestSet_Path"] )
                testsetpath = os.path.normpath(testsetpath)
                testLabFolder = treeManager.NodeByPath(testsetpath) 
                if testLabFolder is None:  raise Exception( 'Unable to find the provided path in test lab' )
            
                
            # create the testset according to the testset name provided
            if config["Add_TestSet"]:
                self.logResultsStatus("Creating testset (%s) in test lab..." % config["TestSet_Name"] )
                testsetFactory = testLabFolder.TestSetFactory
                testset = testsetFactory.AddItem(None)
                testset.Name = config["TestSet_Name"]
                testset.SetField("CY_COMMENT", u"<html><body>%s</body></html>" % "testset generated automatically")
                testset.Post()
            else:
                # find testset name
                self.logResultsStatus("Searching testset (%s) in test lab..." % config["TestSet_Name"] )
                testset = None
                testsets = testLabFolder.FindTestSets(config["TestSet_Name"])
                if testsets is None:  raise Exception( 'Unable to find the test set in test lab' )
                for ts in testsets:
                    if ts.Name == config["TestSet_Name"]:
                        testset = ts
                        break
                if testset is None: raise Exception( 'Testset (%s) not found in test lab' % config["TestSet_Name"] )
            
            # add test instance in testset ?
            if config["Add_TestInstance"]:
                self.logResultsStatus("Finding test(s) from testplan..." )
                tsTestFactory = testset.TSTestFactory

                treeTpManager = qc_cx.TreeManager
                for tc1 in testcases:
                    testpath="Subject/%s/" % tc1['testpath']
                    testpath = os.path.normpath(testpath)
                    try:
                        testPlanFolder = treeTpManager.NodeByPath(testpath) 
                    except pythoncom.com_error as e:
                        raise Exception( 'Unable to find the provided path %s in test plan' %  tc1['testpath'] )
                    
                    try:
                        testsTp = testPlanFolder.FindTests(tc1['testname'])
                    except pythoncom.com_error as e:
                        raise Exception( 'Test (%s) not found in test plan (%s)' % (tc1['testname'],tc1['testpath'])  )
                    
                    objTestTp = None
                    if testsTp is not None:
                        for tTp in testsTp:
                            if tTp.Name == tc1['testname']:
                                objTestTp = tTp
                                break
                    if objTestTp is None:raise Exception( 'Test object (%s) not found in test plan (%s)' % (tc1['testname'], tc1['testpath']) )
                    
                    testInstance = tsTestFactory.AddItem(None)
                    testInstance.Status = "No Run"
                    testInstance.SetField("TC_TEST_ID", objTestTp)
                    testInstance.Post()

            

            self.logResultsStatus("Finding test instance in test lab..." )
            
            #find testset name
            self.logResultsStatus("Refreshing testset (%s) from test lab..." % config["TestSet_Name"] )
            testset = None
            testsets = testLabFolder.FindTestSets(config["TestSet_Name"])
            if testsets is None:  raise Exception( 'Unable to find the test set in test lab' )
            for ts in testsets:
                if ts.Name == config["TestSet_Name"]:
                    testset = ts
                    break
            if testset is None: raise Exception( 'Testset (%s) not found in test lab' % config["TestSet_Name"] )

            # get tests instance
            testsetList = testset.TSTestFactory.NewList("")
            testInstances = []
            for ti in testsetList:
                testInstances.append(ti)
            if not len(testInstances): raise Exception( 'Testset (%s) is empty' % config["TestSet_Name"])
    
            # finally run all testcases instances
            for tc in testcases:

                testI = None
                testIN = tc["name"]
                self.logResultsStatus("Test instance to search in testset: (%s)" % testIN )
                for ti in testInstances:
                    self.logResultsStatus("Test instance detected: (%s)" % ti.Name )
                    if ti.Name == testIN:
                        testI = ti
                        break
                if testI is None:
                    raise Exception("test instance (%s) not found" % testIN )
         
                self.logResultsStatus("Running test instance (%s)..." % testIN )
                # run test instance
                runFactory = testI.RunFactory
                runName = "%s_%s" % (Settings.instance().readValue( key = 'Common/name' ),
                                    time.strftime('%d-%m-%y %H:%M',time.localtime()) )
                runInstance = runFactory.AddItem(runName)
                runInstance.Status = tc["result"]
                runInstance.CopyDesignSteps() 
                runInstance.Post()
                
                # set steps results
                if "steps" in tc: 
                    i = 0
                    for stepFactory in runInstance.StepFactory.NewList(""):
                        try:
                            stp = tc["steps"][i]
                        except Exception as e:
                            raise Exception("step %s is missing" % i )
                        else:
                            stepFactory.Status = stp["result"]
                            stepFactory.SetField("ST_ACTUAL", stp["actual"])
                            stepFactory.post() 

                            stepFactory.UnLockObject()
                            i += 1
                            
                # if no step is provided but exists on qc 
                # then you set all steps with the result of the testcase
                else:
                    for stepFactory in runInstance.StepFactory.NewList(""):
                        stepFactory.Status = tc["result"]
                        stepFactory.post() 
                        stepFactory.UnLockObject()
                            
            # disconnect
            self.logResultsStatus("Disconnection from the COM API..." )
            qc_cx.Logout()
            qc_cx.ReleaseConnection()
            self.logResultsStatus("Disconnected" )
            
            self.ResultsExported.emit()
        except pythoncom.com_error as e:
            hr,msg,exc,arg = e.args
            if exc is None:
                details = "HP connect missing!"
            else:  
                _, _, details, _, _, _ = exc
            self.logTestsStatus("Error on test(s) export" )
            self.Error.emit( "%s: %s" % (msg, details) )
        except Exception as e:
            self.logResultsStatus("Error on results(s) export" )
            self.Error.emit( "%s" % e )
            
    def addTestsInTestPlan(self, testcases, config={}):
        """
        """
        try:
            # connect
            self.logTestsStatus( "Connection to the COM API..." )
            pythoncom.CoInitialize()
            qc_cx = win32client.Dispatch("TDApiOle80.TDConnection")
            qc_cx.InitConnectionEx(self.url)
            qc_cx.Login(self.login, self.password)
            qc_cx.Connect(self.domain, self.project)
            self.logTestsStatus( "Connected" )
            
            # find path folder in test lab
            for tc in testcases:
                self.logTestsStatus("Creating path in test plan..." )
                testpath="Subject/%s/%s" % ( tc['testpath'], tc['testname'] )
                testpath = os.path.normpath(testpath)
                testpathSplit = self.__splitpath(path=testpath)

                tp = "Subject/"
                if len(testpathSplit) == 1:
                    treeManager = qc_cx.TreeManager
                    testPlanFolder = treeManager.NodeByPath(os.path.normpath(tp))
                    
                for f in testpathSplit[1:]:
                    treeManager = qc_cx.TreeManager
                    try:
                        testPlanFolder = treeManager.NodeByPath(os.path.normpath("%s/%s" % (tp, f)))
                        tp = os.path.normpath("%s/%s" % (tp, f))
                    except pythoncom.com_error as e:
                        if not config["Add_Folders"]:
                            raise Exception( 'Folder (%s) is missing in test plan' % os.path.normpath("%s/%s" % (tp, f) ) )
                        else:
                            testPlanFolder = treeManager.NodeByPath(os.path.normpath("%s" % tp))
                            testPlanFolder = testPlanFolder.AddNode(f)
                            tp = os.path.normpath("%s/%s" % (tp, f))
                
                testFactory = testPlanFolder.TestFactory
                # searching the test if overwrite option is activated
                if config["Overwrite_Tests"]:
                    self.logTestsStatus("Searching test (%s) in test plan..." % tc['testcase'] )
                    testF = None
                    tests = testPlanFolder.FindTests(tc['testcase'])
                    if tests is not None:
                        for t in tests:
                            if t.Name == tc['testcase']:
                                testF = t
                                break
                    
                    if testF is not None:
                        self.logTestsStatus("Removing test (%s) in test plan..." % tc['testcase'] )
                        testFactory.RemoveItem(testF)
                        
                # create the test
                self.logTestsStatus("Exporting test in test plan..." )
                test = testFactory.AddItem(None)
                test.Name = tc['testcase']
                test.Type = config["Test_Type"]
                test.SetField("TS_DESCRIPTION", tc['purpose'])
                if len(config["User_01"]): test.SetField("TS_USER_12", config["User_01"] )
                if len(config["User_02"]): test.SetField("TS_USER_12", config["User_02"] )
                if len(config["User_03"]): test.SetField("TS_USER_12", config["User_03"] )
                if len(config["User_04"]): test.SetField("TS_USER_12", config["User_04"] )
                if len(config["User_05"]): test.SetField("TS_USER_12", config["User_05"] )
                if len(config["User_06"]): test.SetField("TS_USER_12", config["User_06"] )
                if len(config["User_07"]): test.SetField("TS_USER_12", config["User_07"] )
                if len(config["User_08"]): test.SetField("TS_USER_12", config["User_08"] )
                if len(config["User_09"]): test.SetField("TS_USER_12", config["User_09"] )
                if len(config["User_10"]): test.SetField("TS_USER_12", config["User_10"] )
                if len(config["User_11"]): test.SetField("TS_USER_12", config["User_11"] )
                if len(config["User_12"]): test.SetField("TS_USER_12", config["User_12"] )
                if len(config["User_13"]): test.SetField("TS_USER_12", config["User_13"] )
                if len(config["User_14"]): test.SetField("TS_USER_12", config["User_14"] )
                if len(config["User_15"]): test.SetField("TS_USER_12", config["User_15"] )
                if len(config["User_16"]): test.SetField("TS_USER_12", config["User_16"] )
                if len(config["User_17"]): test.SetField("TS_USER_12", config["User_17"] )
                if len(config["User_18"]): test.SetField("TS_USER_12", config["User_18"] )
                if len(config["User_19"]): test.SetField("TS_USER_12", config["User_19"] )
                if len(config["User_20"]): test.SetField("TS_USER_12", config["User_20"] )
                if len(config["User_21"]): test.SetField("TS_USER_12", config["User_21"] )
                if len(config["User_22"]): test.SetField("TS_USER_12", config["User_22"] )
                if len(config["User_23"]): test.SetField("TS_USER_12", config["User_23"] )
                if len(config["User_24"]): test.SetField("TS_USER_12", config["User_24"] )

                # post test
                test.Post()
                        
                # adding step
                self.logTestsStatus("Exporting steps in test plan..." )
                i = 1
                for stp in tc["steps"]:
                    stepFactory = test.DesignStepFactory.AddItem(None)
                    stepFactory.StepName = "Step%s" % i
                    stepFactory.StepDescription = stp["action"]
                    stepFactory.StepExpectedResult = stp["expected"]
                    stepFactory.Post()
                    stepFactory.UnLockObject()
                    i +=1
                test.UnLockObject()
                
            # disconnect
            self.logTestsStatus("Disconnection from the COM API..." )
            qc_cx.Logout()
            qc_cx.ReleaseConnection()
            self.logTestsStatus("Disconnected" )
            
            self.TestsExported.emit()
        except pythoncom.com_error as e:
            hr,msg,exc,arg = e.args
            if exc is None:
                details = "HP connect missing!"
            else:  
                _, _, details, _, _, _ = exc
            self.logTestsStatus("Error on test(s) export" )
            self.Error.emit( "%s: %s" % (msg, details) )
        except Exception as e:
            self.logTestsStatus("Error on test(s) export" )
            self.Error.emit( "%s" % e )

    def logTestsStatus(self, status):
        """
        """
        self.LogTestsStatus.emit( "Status: %s" % status)
        
    def logResultsStatus(self, status):
        """
        """
        self.LogResultsStatus.emit( "Status: %s" % status )