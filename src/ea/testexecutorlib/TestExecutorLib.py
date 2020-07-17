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

from xml.sax.saxutils import escape
import time
import threading
import sys
import os
import datetime
import copy
import base64
import json
import re
import platform

from ea.libs.NetLayerLib import Messages as Messages
from ea.testexecutorlib import TestSettings
from ea.testexecutorlib import TestClientInterface as TCI
from ea.testexecutorlib import TestAdapterLib
from ea.testexecutorlib import TestOperatorsLib
from ea.testexecutorlib import TestPropertiesLib
from ea.testexecutorlib import TestTemplatesLib
from ea.testexecutorlib import TestDataStorage as TDS
from ea.testexecutorlib import TestLoggerXml as TLX

# unicode = str with python3
if sys.version_info > (3,):
    unicode = str


__DESCRIPTION__ = """This library enable to create testcase with step support."""

__HELPER__ = [
    ('BreakPoint', ['__init__']),
    ('Cache', ['capture', 'set', 'all', 'get', 'delete', 'reset']),
    ('Interact', ['interact']),
    ('Private', ['__init__', 'getPath', 'getFile',
                             'addFolder', 'saveFile', 'appendFile']),
    ('Public', ['__init__', 'getPath', 'getFile',
                            'addFolder', 'saveFile', 'appendFile']),
    ('Step', ['__init__', 'setDisabled', 'setEnabled', 'isEnabled',
                          'setSummary', 'setDescription', 'setExpected',
                          'getId', 'start', 'setFailed', 'setPassed']),
    ('Test', ['terminate', 'interrupt']),
    ('TestCase', ['__init__', 'getPreviousStep', 'setPurpose',
                              'setRequirement', 'setName', 'getId',
                              'addStep', 'findAdapter', 'label', 'condition']),
    ('Timer', ['sleep', 'sleepUntil',
               'wait', 'waitUntil', 'utc', 'local']),
    ('Trace', ['info', 'error', 'warning'])
]

PASS = "PASS"
FAIL = "FAIL"
UNDEFINED = "UNDEFINED"

TU = "TESTUNIT"
TC = "TESTCASE"
TS = "TESTSUITE"
TP = "TESTPLAN"
TG = "TESTGLOBAL"
STP = "STEP"

TEST_RESULT_VERDICT_EXT = 'trv'
TEST_RESULT_REPORT_EXT = 'trp'
TEST_RESULT_DESIGN_EXT = 'trd'
TEST_RESULT_BASIC_REPORT_EXT = 'tbrp'

TEST_RESULT_VERDICT_XML_EXT = 'tvrx'
TEST_RESULT_REPORT_XML_EXT = 'trpx'
TEST_RESULT_DESIGN_XML_EXT = 'tdsx'

LEVEL_USER = 'USER'
LEVEL_TE = 'TE'

# exceptions


class AgentDownException(Exception):
    pass


class DeprecatedException(Exception):
    pass


class StepException(Exception):
    pass


class BreakpointException(Exception):
    pass


class TestWaitException(Exception):
    pass


class TimeException(Exception):
    pass


class AbortException(Exception):
    pass


class AbortStopException(Exception):
    pass


class ForceStopException(Exception):
    pass


class ForceTerminateTestException(Exception):
    pass


class PrivateException(Exception):
    pass


class PublicException(Exception):
    pass


# can be use in the test execution from a test suite
class AbortTestSuite(object):
    def __init__(self, reason=None):
        if reason is not None:
            raise Exception("Test suite aborted: %s" % reason)
        raise Exception("Test suite aborted!")


CHART_JS_VERSION = "2.1.4"

# xml.sax.saxutils.escape only escapes &, <, and > by default,
# but it does provide an entities parameter to additionally escape other
# strings:


def xmlescape(data):
    """
    """
    return escape(data, entities={
        "'": "&apos;",
        "\"": "&quot;"
    })


def filter_non_printable(str):
    """
    """
    return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])


class TestSuitesManager(object):
    """
    Test suites manager
    """

    def __init__(self):
        """
        Constructor for the test suites manager
        """
        self.id__ = 0
        self.tcs = {}
        self.__filename = ''
        self.__filename_report = ''
        self.__path = ''
        self.__userId = 0
        self.__projectId = 0
        # test plan
        self.__tp_name = None
        self.__tp_sutinputs = []
        self.__tp_datainputs = []
        self.__tp_sutoutputs = []
        self.__tp_dataoutputs = []
        self.__tp_datasummary = ''
        self.__tp_startedat = ''
        self.__tp_duration = 0
        self.__tp_verdict = UNDEFINED
        self.__tp_global = False
        self.__sub_tp = 0
        self.__final_result = UNDEFINED
        # csv
        self.csv_separator = ','
        # new
        self.__stepByStep = False
        self.__breakpoint = False
        self.__testId = 0
        # header for report and description
        self.report_header = ''
        self.description = []
        self.scriptDuration = 0
        # new in v13
        self.__testname = ''
        self.__testpath = ''
        self.__username = ''
        self.__projectname = ''
        # new in v13.1
        self.basic_report_tpl = ''
        self.__filename_basic_report = ''
        # new in v16
        self.__mainDescriptions = []
        # new in v17.1
        self.nbtests = 0
        self.progress = 0

        self.PNG_BASE64_PASSED = ""
        self.PNG_BASE64_FAILED = ""
        self.PNG_BASE64_UNDEFINED = ""

    def prepareReportImages(self):
        """
        """
        PATH_TPL = TestSettings.get('Paths', 'templates')

        with open("%s/png_passed.base64" % PATH_TPL, "r") as fd_png:
            self.PNG_BASE64_PASSED = fd_png.read()

        with open("%s/png_failed.base64" % PATH_TPL, "r") as fd_png:
            self.PNG_BASE64_FAILED = fd_png.read()

        with open("%s/png_undefined.base64" % PATH_TPL, "r") as fd_png:
            self.PNG_BASE64_UNDEFINED = fd_png.read()

    def setNbTests(self, nb):
        """
        """
        self.nbtests = nb + 1

    def saveProgress(self):
        """
        """
        if self.nbtests:
            p = (self.progress * 100) / self.nbtests
            f = open("%s/PROGRESS" % self.__path, "w")
            f.write(json.dumps({"percent": p, "total": self.nbtests}))
            f.close()
        else:
            f = open("%s/PROGRESS" % self.__path, "w")
            f.write(json.dumps({"percent": 0, "total": 0}))
            f.close()

    def testcases(self):
        """
        """
        ret = []
        subtp = None
        for tsId, ts in self.tcs.items():
            if ts['is-testplan'] and ts['is-tp-started']:
                sub_name = ts["name"]
                if "alias" in ts:
                    if len(ts["alias"]):
                        sub_name = ts["alias"]
                subtp = sub_name
            if ts['is-testplan'] and not ts['is-tp-started']:
                subtp = None
                continue

            # append all testcases
            for tc in ts['tc']:
                testcase = {}
                testcase["id"] = tc.getId()

                if self.__tp_name is not None:
                    testcase["root"] = self.__tp_name

                    ts_name = ts["name"]
                    if "alias" in ts:
                        if len(ts["alias"]):
                            ts_name = ts["alias"]

                    if subtp is not None:
                        testcase["parent"] = r"%s\%s" % (subtp, ts_name)
                    else:
                        testcase["parent"] = ts_name

                else:
                    testcase["root"] = ts["name"]
                    testcase["parent"] = ts["name"]

                testcase["name"] = tc.getTestname()
                testcase["verdict"] = tc.get_final_verdict()

                # append all steps
                steps = []
                for stp in tc.getSteps():
                    step = {}
                    step["id"] = stp.getId()
                    step["verdict"] = stp.getVerdict()

                    step["summary"] = stp.getSummary()
                    step["expected"] = stp.getExpected()
                    step["actual"] = stp.getActual()
                    step["action"] = stp.getAction()

                    steps.append(step)

                testcase["steps"] = steps

                ret.append(testcase)
        return ret

    def setTestGlobal(self):
        """
        Is test global
        """
        self.__tp_global = True

    def isTestPlanInTestGlobal(self):
        """
        Is testplan in testglobal
        """
        if int(self.__sub_tp) > 0:
            return True
        else:
            return False

    def initialize(self, path, testname, replayId, userId, projectId, stepByStep,
                   breakpoint, testId, relativePath='',
                   testpath='', userName='', projectName=''):
        """
        Initialize
        """
        self.__testname = testname
        self.__testpath = testpath
        self.__username = userName
        self.__projectname = projectName

        self.__testId = testId
        self.__stepByStep = stepByStep
        self.__breakpoint = breakpoint
        self.__userId = userId
        self.__projectId = projectId
        self.__path = path
        self.__relativePath = relativePath
        self.__filename = "%s_%s.%s" % (testname,
                                        replayId,
                                        TEST_RESULT_VERDICT_EXT)
        self.__filename_report = "%s_%s.%s" % (testname,
                                               replayId,
                                               TEST_RESULT_REPORT_EXT)
        self.__filename_design = "%s_%s.%s" % (testname,
                                               replayId,
                                               TEST_RESULT_DESIGN_EXT)

        self.__filename_xml = "%s_%s.%s" % (testname,
                                            replayId,
                                            TEST_RESULT_VERDICT_XML_EXT)
        self.__filename_report_xml = "%s_%s.%s" % (testname,
                                                   replayId,
                                                   TEST_RESULT_REPORT_XML_EXT)
        self.__filename_design_xml = "%s_%s.%s" % (testname,
                                                   replayId,
                                                   TEST_RESULT_DESIGN_XML_EXT)

        # new in v13.1
        self.__filename_basic_report = "%s_%s.%s" % (testname,
                                                     replayId,
                                                     TEST_RESULT_BASIC_REPORT_EXT)

        self.prepareReportImages()

    def getTestId(self):
        """
        Returns the test id (tab id on user client)
        """
        return self.__testId

    def getId(self):
        """
        """
        return self.id__

    def getStepByStep(self):
        """
        Returns the step by step
        """
        return self.__stepByStep

    def getBreakpoint(self):
        """
        Returns the breakpoint
        """
        return self.__breakpoint

    def getProjectID(self):
        """
        Return the project id
        """
        return self.__projectId

    def saveDesignsXml(self):
        """
        Save designs as xml
        """
        try:
            i = 0
            designs = [u'<?xml version="1.0" encoding="UTF-8"?>']

            # new in v16
            mainDescrs = []
            for d in self.__mainDescriptions:
                if d["key"].lower() == "comments":
                    continue

                val = d["value"]
                k = d["key"].replace(" ", "_")
                mainDescrs.append("%s=\"%s\"" % (k, xmlescape(val)))
            # end of new

            designs.append(u'<designs>')
            # iterate each testsuites
            for tsId, ts in self.tcs.items():
                # iterate each testcases
                for tc in ts['tc']:
                    i += 1
                    designs.append(u"\t<design id=\"%s\" >" % (i))
                    design = []
                    design.append(
                        u"\t\t<user>%s</user>" %
                        xmlescape(
                            self.__username))
                    design.append(
                        u"\t\t<fileproject>%s</fileproject>" %
                        xmlescape(
                            self.__projectname))
                    design.append(
                        u"\t\t<filepath>%s</filepath>" %
                        xmlescape(
                            self.__testpath))
                    design.append(
                        u"\t\t<filename>%s</filename>" %
                        xmlescape(
                            self.__testname))
                    design.append(
                        u"\t\t<testproject>%s</testproject>" %
                        xmlescape(
                            ts["project"]))
                    design.append(
                        u"\t\t<testpath>%s</testpath>" %
                        xmlescape(
                            ts["path"]))

                    # new in v16
                    tsName = xmlescape(ts['name'])
                    if len(ts['alias']):
                        tsName = xmlescape(ts['alias'])
                    # end of new

                    design.append(u"\t\t<testname>%s</testname>" % tsName)
                    for line in tc.getStepsManager().getDesignXml():
                        design.append(u"\t\t%s" % line)
                    designs.extend(design)
                    designs.append(u"\t</design>")
            designs[1] = u'<designs max="%s" %s >' % (i, " ".join(mainDescrs))
            designs.append(u'</designs>')
        except Exception as e:
            print('contruct design xml error: %s' % str(e))
        else:
            try:
                # save to file
                f = open(
                    '%s/%s' %
                    (self.__path, self.__filename_design_xml), 'w')
                f.write(self.__safestr2(datas=designs))
                f.close()
            except Exception as e:
                print('save design xml error: %s' % str(e))

    def saveDesigns(self):
        """
        Save all designs
        """
        try:
            i = 0
            designs = []
            designs.append(u'<html>')
            designs.append(u'<head>')
            designs.append(
                u'<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />')
            designs.append(u"<style>")
            designs.append(u"table {border-collapse: collapse;}\n")
            designs.append(u"th {background-color: #4CAF50;color: white;}")
            designs.append(u"</style>")
            designs.append(u'</head>')
            designs.append(u'<body>')

            # iterate each testsuites
            for tsId, ts in self.tcs.items():
                # iterate each testcases
                for tc in ts['tc']:
                    i += 1

                    # new in v16
                    tsName = xmlescape(ts['name'])
                    if len(ts['alias']):
                        tsName = xmlescape(ts['alias'])
                    # end of new

                    designs.append(u"%s" % tc.getStepsManager().getDesign(i,
                                                                          testName=tsName,
                                                                          testPath=ts["path"],
                                                                          userName=self.__username,
                                                                          projectName=self.__projectname))
                    designs.append(u"<br /><br />")

            designs.append(u"</body>")
            designs.append(u"</html>")
        except Exception as e:
            print('contruct design error: %s' % str(e))
        else:
            try:
                # save to file
                f = open('%s/%s' % (self.__path, self.__filename_design), 'w')
                f.write(self.__safestr2(datas=designs))
                f.close()
            except Exception as e:
                print('save design error: %s' % str(e))

    def setReportHeader(self, header):
        """
        """
        self.report_header = header

    def setBasicReportTemplate(self, template):
        """
        """
        self.basic_report_tpl = template

    def setDescription(self, description):
        """
        """
        self.description = description

    def setMainDescriptions(self, descriptions):
        """
        """
        self.__mainDescriptions = descriptions

    def __initBasicReportTpl(self):
        """
        Initiliaze the report template
        """
        tpl_path = "%s/basic_report.tpl" % (
            TestSettings.get('Paths', 'templates'))
        try:
            fd = open(tpl_path, "r")
            tpl_report = fd.read()
            fd.close()
        except Exception as e:
            print('unable to read the basic report template: %s' % str(e))
        else:
            # save the final html header report
            self.setBasicReportTemplate(tpl_report)

    def __initReportHeaderTpl(self):
        """
        Initiliaze the report template
        """
        tpl_path = "%s/report_header.tpl" % (
            TestSettings.get('Paths', 'templates'))
        try:
            fd = open(tpl_path, "r")
            tpl_report = fd.read()
            fd.close()
        except Exception as e:
            print('unable to read report header template: %s' % str(e))
        else:

            # new in v12.2 additional js script
            js_lib = ''
            try:
                fd = open(
                    "%s/chart.bundle.min.%s.js" %
                    (TestSettings.get(
                        'Paths',
                        'templates'),
                        CHART_JS_VERSION),
                    "r")
                js_lib = fd.read()
                fd.close()
            except Exception as e:
                print('unable to read javascript lib: %s' % e)
            else:
                tpl_report = tpl_report.replace("<!-- REPLACE_ME -->", js_lib)

            # save the final html header report
            self.setReportHeader(tpl_report)

    def getHeaderReport(self):
        """
        Return the text report header
        """
        header = u"<div class='report_header'>Test report auto-generated by "
        header += "<a href='https://www.extensiveautomation.org/'>Extensive Automation</a> "
        header += "- Copyright (c) 2010-2019 - Denis Machard</div>"
        return header

    def prepareParameters(self, parameters):
        """
        """
        inputs_str = []
        for i in parameters:
            if i['type'] in ['snapshot-image',
                             'local-file', 'local-image', 'dataset']:
                inputs_str.append(
                    u'* %s (%s) = ...binary...' %
                    (i['name'], i['type']))
            else:
                if i['type'] in ["shared"]:
                    val_tmp = TestPropertiesLib.instance(
                    ).readShared(shared=i['value'])
                elif i['type'] in ["list-shared"]:
                    val_tmp = TestPropertiesLib.instance(
                    ).readListShared(shared=i['value'])
                else:
                    try:
                        val_tmp = str(i['value'])
                    except Exception:
                        val_tmp = i['value'].encode('utf8')

                    if sys.version_info < (3,):
                        val_tmp = val_tmp.decode("utf8")

                inputs_str.append(u'%s (%s) = %s' % (str(i['name']),
                                                     str(i['type']),
                                                     val_tmp)
                                  )
        return inputs_str

    def prepareStatistics(self, statistics, statisticsTu,
                          statisticsTs,
                          statisticsTp, statisticsTg):
        """
        """
        # prepare testcase stats
        total = (
            statistics['PASSED'] +
            statistics['FAILED'] +
            statistics['UNDEFINED'])
        if total > 0:
            pass_test = (statistics['PASSED'] * 100) / total
            fail_test = (statistics['FAILED'] * 100) / total
            undef_test = (statistics['UNDEFINED'] * 100) / total
        else:
            pass_test = 0
            fail_test = 0
            undef_test = 0

        # prepare testunit stats
        total_tu = (
            statisticsTu['PASSED'] +
            statisticsTu['FAILED'] +
            statisticsTu['UNDEFINED'])
        if total_tu > 0:
            pass_test_tu = (statisticsTu['PASSED'] * 100) / total_tu
            fail_test_tu = (statisticsTu['FAILED'] * 100) / total_tu
            undef_test_tu = (statisticsTu['UNDEFINED'] * 100) / total_tu
        else:
            pass_test_tu = 0
            fail_test_tu = 0
            undef_test_tu = 0

        # prepare testsuites stats
        total_ts = (
            statisticsTs['PASSED'] +
            statisticsTs['FAILED'] +
            statisticsTs['UNDEFINED'])
        if total_ts > 0:
            pass_test_ts = (statisticsTs['PASSED'] * 100) / total_ts
            fail_test_ts = (statisticsTs['FAILED'] * 100) / total_ts
            undef_test_ts = (statisticsTs['UNDEFINED'] * 100) / total_ts
        else:
            pass_test_ts = 0
            fail_test_ts = 0
            undef_test_ts = 0

        # prepare testplan stats
        total_tp = (
            statisticsTp['PASSED'] +
            statisticsTp['FAILED'] +
            statisticsTp['UNDEFINED'])
        if total_tp > 0:
            pass_test_tp = (statisticsTp['PASSED'] * 100) / total_tp
            fail_test_tp = (statisticsTp['FAILED'] * 100) / total_tp
            undef_test_tp = (statisticsTp['UNDEFINED'] * 100) / total_tp
        else:
            pass_test_tp = 0
            fail_test_tp = 0
            undef_test_tp = 0

        # prepare testglobal stats
        total_tg = (
            statisticsTg['PASSED'] +
            statisticsTg['FAILED'] +
            statisticsTg['UNDEFINED'])
        if total_tg > 0:
            pass_test_tg = (statisticsTg['PASSED'] * 100) / total_tg
            fail_test_tg = (statisticsTg['FAILED'] * 100) / total_tg
            undef_test_tg = (statisticsTg['UNDEFINED'] * 100) / total_tg
        else:
            pass_test_tg = 0
            fail_test_tg = 0
            undef_test_tg = 0

        ret = ['<table id="statistics">']
        ret.append(
            "<tr><td></td><td>PASS</td><td>FAIL</td><td>UNDEF</td><td>TOTAL</td></tr>")

        tmp_tc = ["<tr><td>TESTCASE:</td><td>%s " % statistics['PASSED']]
        if pass_test > 0:
            tmp_tc.append(
                "<small><font color='#008000'>(%s%%)</font></small>" %
                pass_test)
        tmp_tc.append("</td><td>%s " % statistics['FAILED'])
        if fail_test > 0:
            tmp_tc.append(
                "<small><font color='#FF00000'>(%s%%)</font></small>" %
                fail_test)
        tmp_tc.append("</td><td>%s " % statistics['UNDEFINED'])
        if undef_test > 0:
            tmp_tc.append("<small>(%s%%)</small>" % undef_test)
        tmp_tc.append("</td><td>%s</td></tr>" % total)
        ret.append("".join(tmp_tc))

        tmp_tu = ["<tr><td>TESTUNIT:</td><td>%s " % statisticsTu['PASSED']]
        if pass_test_tu > 0:
            tmp_tu.append(
                "<small><font color='#008000'>(%s%%)</font></small>" %
                pass_test_tu)
        tmp_tu.append("</td><td>%s " % statisticsTu['FAILED'])
        if fail_test_tu > 0:
            tmp_tu.append(
                "<small><font color='#FF00000'>(%s%%)</font></small>" %
                fail_test_tu)
        tmp_tu.append("</td><td>%s " % statisticsTu['UNDEFINED'])
        if undef_test_tu > 0:
            tmp_tu.append("<small>(%s%%)</small>" % undef_test_tu)
        tmp_tu.append("</td><td>%s</td></tr>" % total_tu)
        ret.append("".join(tmp_tu))

        tmp_ts = ["<tr><td>TESTSUITE:</td><td>%s " % statisticsTs['PASSED']]
        if pass_test_ts > 0:
            tmp_ts.append(
                "<small><font color='#008000'>(%s%%)</font></small>" %
                pass_test_ts)
        tmp_ts.append("</td><td>%s " % statisticsTs['FAILED'])
        if fail_test_ts > 0:
            tmp_ts.append(
                "<small><font color='#FF00000'>(%s%%)</font></small>" %
                fail_test_ts)
        tmp_ts.append("</td><td>%s " % statisticsTs['UNDEFINED'])
        if undef_test_ts > 0:
            tmp_ts.append("<small>(%s%%)</small>" % undef_test_ts)
        tmp_ts.append("</td><td>%s</td></tr>" % total_ts)
        ret.append("".join(tmp_ts))

        tmp_tp = ["<tr><td>TESTPLAN:</td><td>%s " % statisticsTp['PASSED']]
        if pass_test_tp > 0:
            tmp_tp.append(
                "<small><font color='#008000'>(%s%%)</font></small>" %
                pass_test_tp)
        tmp_tp.append("</td><td>%s " % statisticsTp['FAILED'])
        if fail_test_tp > 0:
            tmp_tp.append(
                "<small><font color='#FF00000'>(%s%%)</font></small>" %
                fail_test_tp)
        tmp_tp.append("</td><td>%s " % statisticsTp['UNDEFINED'])
        if undef_test_tp > 0:
            tmp_tp.append("<small>(%s%%)</small>" % undef_test_tp)
        tmp_tp.append("</td><td>%s</td></tr>" % total_tp)
        ret.append("".join(tmp_tp))

        tmp_tg = ["<tr><td>TESTGLOBAL:</td><td>%s " % statisticsTg['PASSED']]
        if pass_test_tg > 0:
            tmp_tg.append(
                "<small><font color='#008000'>(%s%%)</font></small>" %
                pass_test_tg)
        tmp_tg.append("</td><td>%s " % statisticsTg['FAILED'])
        if fail_test_tg > 0:
            tmp_tg.append(
                "<small><font color='#FF00000'>(%s%%)</font></small>" %
                fail_test_tg)
        tmp_tg.append("</td><td>%s " % statisticsTg['UNDEFINED'])
        if undef_test_tg > 0:
            tmp_tg.append("<small>(%s%%)</small>" % undef_test_tg)
        tmp_tg.append("</td><td>%s</td></tr>" % total_tg)
        ret.append("".join(tmp_tg))

        ret.append('</table>')
        return "".join(ret)

    def computeStatistics(self):
        """
        """
        stats = {'PASSED': 0, 'FAILED': 0, 'UNDEFINED': 0}  # tc
        statsTu = {'PASSED': 0, 'FAILED': 0, 'UNDEFINED': 0}
        statsTs = {'PASSED': 0, 'FAILED': 0, 'UNDEFINED': 0}
        statsTp = {'PASSED': 0, 'FAILED': 0, 'UNDEFINED': 0}
        statsTg = {'PASSED': 0, 'FAILED': 0, 'UNDEFINED': 0}

        # compute final result
        isTestGlobal = False
        isTestPlan = 0
        finalResult = None
        for tsId, ts in self.tcs.items():
            tsResult = None
            isTs = False
            isTestPlan += 1
            for tc in ts['tc']:
                if tc.get_final_verdict() == PASS:
                    stats['PASSED'] += 1
                if tc.get_final_verdict() == FAIL:
                    stats['FAILED'] += 1
                if tc.get_final_verdict() == UNDEFINED:
                    stats['UNDEFINED'] += 1

                if ts['is-unit']:
                    if tc.get_final_verdict() == PASS:
                        statsTu['PASSED'] += 1
                    if tc.get_final_verdict() == FAIL:
                        statsTu['FAILED'] += 1
                    if tc.get_final_verdict() == UNDEFINED:
                        statsTu['UNDEFINED'] += 1
                else:  # is testsuite
                    isTs = True
                    if tsResult not in [FAIL, UNDEFINED]:
                        tsResult = tc.get_final_verdict()

                # compute the global result
                if finalResult in [FAIL, UNDEFINED]:
                    continue
                finalResult = tc.get_final_verdict()

            if tsResult is None:
                tsResult = UNDEFINED
            if isTs:
                if tsResult == PASS:
                    statsTs['PASSED'] += 1
                if tsResult == FAIL:
                    statsTs['FAILED'] += 1
                if tsResult == UNDEFINED:
                    statsTs['UNDEFINED'] += 1

            # test plan in test global
            if ts['is-testplan'] and ts['is-tp-started']:
                isTestGlobal = True
                if ts['result'] == PASS:
                    statsTp['PASSED'] += 1
                if ts['result'] == FAIL:
                    statsTp['FAILED'] += 1
                if ts['result'] == UNDEFINED:
                    statsTp['UNDEFINED'] += 1

        if stats['UNDEFINED'] > 0:
            finalResult = UNDEFINED
        if finalResult is None:
            finalResult = UNDEFINED

        # a test global is running ?
        if isTestGlobal:
            if finalResult == PASS:
                statsTg['PASSED'] += 1
            if finalResult == FAIL:
                statsTg['FAILED'] += 1
            if finalResult == UNDEFINED:
                statsTg['UNDEFINED'] += 1
        # a test plan is running ?
        else:
            if isTestPlan > 1:
                if finalResult == PASS:
                    statsTp['PASSED'] += 1
                if finalResult == FAIL:
                    statsTp['FAILED'] += 1
                if finalResult == UNDEFINED:
                    statsTp['UNDEFINED'] += 1

        self.__final_result = finalResult

        return(stats, statsTu, statsTs, statsTp, statsTg)

    def saveBasicReports(self, stoppedAt=0):
        """
        """
        self.__initBasicReportTpl()
        try:
            reports = []
            if TestSettings.get('Tests_Framework', 'header-test-report'):
                reports.append(self.getHeaderReport())

            stats, statsTu, statsTs, statsTp, statsTg = self.computeStatistics()

            reports.append(u'<ul>')
            if self.__tp_name is not None:
                if self.__tp_global:
                    if self.__final_result == PASS:
                        reports.append(u'<li data-type="passed">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#008000">%s</font></label>' %
                            (self.__tp_name))
                    elif self.__final_result == FAIL:
                        reports.append(u'<li data-type="failed">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#FF00000">%s</font></label>' %
                            (self.__tp_name))
                    else:
                        reports.append(u'<li data-type="undefined">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#FFBB3D">%s</font></label>' %
                            (self.__tp_name))
                else:
                    if self.__tp_verdict == PASS:
                        reports.append(u'<li data-type="passed">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#008000">%s</font></label>' %
                            (self.__tp_name))
                    elif self.__tp_verdict == FAIL:
                        reports.append(u'<li data-type="failed">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#FF00000">%s</font></label>' %
                            (self.__tp_name))
                    else:
                        reports.append(u'<li data-type="undefined">')
                        reports.append(
                            u'<input type="checkbox" id="c0" checked  class="isexpanded" />')
                        reports.append(
                            u'<label for="c0"><font color="#FFBB3D">%s</font></label>' %
                            (self.__tp_name))

                reports.append(
                    u" <span class=\"test_time\">(%s, %.3f seconds)</span >" %
                    (self.__tp_startedat, self.__tp_duration))
                reports.append(u"<ul class=\"test_section\">")

            # iterate each testsuites
            index = 1
            for tsId, ts in self.tcs.items():

                tsName = ts['name']
                if len(ts['alias']):
                    tsName = ts['alias']

                if not int(ts['is-enabled']) and not ts['is-testplan']:
                    reports.append(u'<li data-type="norun">')
                    reports.append(
                        u'<input type="checkbox" id="c%s" checked  class="isexpanded" />' %
                        index)
                    reports.append(
                        u'<label for="c%s"><font color="#000000">%s</font></label>' %
                        (index, tsName))
                    index += 1
                    continue

                if not ts['is-executed']:
                    if TestSettings.getInt(
                            'Tests_Framework', 'ignored-testcase-visible-test-report'):
                        reports.append(u'<li data-type="ignored">')
                        reports.append(
                            u'<input type="checkbox" id="c%s" checked   class="isexpanded"/>' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#000000">%s</font></label>' %
                            (index, tsName))
                    index += 1
                    continue

                # decode summary only for testglobal or testplan
                if ts['is-unit']:
                    v = ts['tc'][0].get_final_verdict()
                    if v == PASS:
                        reports.append(u'<li data-type="passed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#008000">%s</font></label>' %
                            (index, tsName))
                    elif v == FAIL:
                        reports.append(u'<li data-type="failed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#FF00000">%s</font></label>' %
                            (index, tsName))
                    else:
                        reports.append(u'<li data-type="undefined">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#FFBB3D">%s</font></label>' %
                            (index, tsName))

                    if self.__tp_name is None:
                        reports.append(
                            u" <span class=\"test_time\">(%s, %.3f seconds)</span >" %
                            (ts['started-at'], ts['duration']))

                elif ts['is-testplan'] and ts['is-tp-started']:
                    checked = "checked"
                    if self.__tp_global:
                        checked = ""

                    v = ts["result"]
                    if v == PASS:
                        reports.append(u'<li data-type="passed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s" %s  class="isexpanded" />' %
                            (index, checked))
                        reports.append(
                            u'<label for="c%s"><font color="#008000">%s</font></label>' %
                            (index, tsName))
                    elif v == FAIL:
                        reports.append(u'<li data-type="failed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s" %s  class="isexpanded" />' %
                            (index, checked))
                        reports.append(
                            u'<label for="c%s"><font color="#FF00000">%s</font></label>' %
                            (index, tsName))
                    else:
                        reports.append(u'<li data-type="undefined">')
                        reports.append(
                            u'<input type="checkbox" id="c%s" %s  class="isexpanded" />' %
                            (index, checked))
                        reports.append(
                            u'<label for="c%s"><font color="#FFBB3D">%s</font></label>' %
                            (index, tsName))

                    if self.__tp_name is None:
                        reports.append(
                            u" <span class=\"test_time\">(%s, %.3f seconds)</span >" %
                            (ts['started-at'], ts['duration']))

                    reports.append(u'<ul>')

                elif ts['is-testplan']:
                    reports.append(u'</ul>')

                else:
                    v = UNDEFINED
                    for tc in ts['tc']:
                        vtc = tc.get_final_verdict()
                        if vtc == UNDEFINED:
                            v = vtc
                            break
                        if v == FAIL and vtc == PASS:
                            continue
                        v = vtc

                    if v == PASS:
                        reports.append(u'<li data-type="passed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#008000">%s</font></label>' %
                            (index, tsName))
                    elif v == FAIL:
                        reports.append(u'<li data-type="failed">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#FF00000">%s</font></label>' %
                            (index, tsName))
                    else:
                        reports.append(u'<li data-type="undefined">')
                        reports.append(
                            u'<input type="checkbox" id="c%s"  class="isexpanded" />' %
                            index)
                        reports.append(
                            u'<label for="c%s"><font color="#FFBB3D">%s</font></label>' %
                            (index, tsName))

                    if self.__tp_name is None:
                        reports.append(
                            u" <span class=\"test_time\">(%s, %.3f seconds)</span >" %
                            (ts['started-at'], ts['duration']))

                reports.append(u'<ul id="testcase">')

                indexTc = 1
                # iterate each testcases

                for tc in ts['tc']:
                    v = tc.get_final_verdict()
                    n = tc.getTestname()

                    if v == PASS:
                        reports.append(u'<li data-type="pass">')
                        reports.append(
                            u'<input type="checkbox" id="c%st%s"  class="isexpanded" />' %
                            (index, indexTc))
                        reports.append(
                            u'<label for="c%st%s"><font color="#008000">%s</font></label>' %
                            (index, indexTc, n))

                        if len(tc.getLogs()):
                            reports.append(
                                u'<input type="checkbox" id="info-c%st%s" class="isexpanded3" />' %
                                (index, indexTc))
                            reports.append(
                                u'<label for="info-c%st%s"><span>[logs details]</span></label>' %
                                (index, indexTc))

                    elif v == FAIL:
                        reports.append(u'<li data-type="fail">')
                        reports.append(
                            u'<input type="checkbox" id="c%st%s" class="isexpanded" />' %
                            (index, indexTc))
                        reports.append(
                            u'<label for="c%st%s"><font color="#FF00000">%s</font></label>' %
                            (index, indexTc, n))

                        if len(tc.getErrors()):
                            reports.append(
                                u'<input type="checkbox" id="err-c%st%s" class="isexpanded2" />' %
                                (index, indexTc))
                            reports.append(
                                u'<label for="err-c%st%s"><span>[errors details]</span></label>' %
                                (index, indexTc))

                        if len(tc.getLogs()):
                            reports.append(
                                u'<input type="checkbox" id="info-c%st%s" class="isexpanded3" />' %
                                (index, indexTc))
                            reports.append(
                                u'<label for="info-c%st%s"><span>[logs details]</span></label>' %
                                (index, indexTc))

                    else:
                        reports.append(u'<li data-type="undef">')
                        reports.append(
                            u'<input type="checkbox" id="c%st%s"  class="isexpanded" />' %
                            (index, indexTc))
                        reports.append(
                            u'<label for="c%st%s"><font color="#FFBB3D">%s</font></label>' %
                            (index, indexTc, n))

                        if len(tc.getErrors()):
                            reports.append(
                                u'<input type="checkbox" id="err-c%st%s" class="isexpanded2" />' %
                                (index, indexTc))
                            reports.append(
                                u'<label for="err-c%st%s"><span>[errors details]</span></label>' %
                                (index, indexTc))

                        if len(tc.getLogs()):
                            reports.append(
                                u'<input type="checkbox" id="info-c%st%s" class="isexpanded3" />' %
                                (index, indexTc))
                            reports.append(
                                u'<label for="info-c%st%s"><span>[logs details]</span></label>' %
                                (index, indexTc))

                    if len(tc.getErrors()):
                        reports.append(u'<div id="errors"><span>')
                        for e in tc.getErrors():
                            reports.append(
                                u'<p>%s</p>' %
                                xmlescape(
                                    filter_non_printable(e)))
                        reports.append(u'</span></div>')

                    if len(tc.getLogs()):
                        reports.append(u'<div id="logs"><span>')
                        for e in tc.getLogs():
                            reports.append(
                                u'<p>%s</p>' %
                                xmlescape(
                                    filter_non_printable(e)))
                        reports.append(u'</span></div>')

                    reports.append(u'<ul id="step">')
                    for stp in tc.getSteps():
                        s = stp.getStep()
                        sv = stp.getVerdict()
                        sum = stp.getSummary()
                        if sv == PASS:
                            reports.append(
                                u'<li data-type="pass"><font color="#008000">%s - %s</font></li>' %
                                (s, sum))
                        elif sv == FAIL:
                            reports.append(
                                u'<li data-type="fail"><font color="#FF00000">%s - %s</font></li>' %
                                (s, sum))
                        else:
                            reports.append(
                                u'<li data-type="undef"><font color="#FFBB3D">%s - %s</font></li>' %
                                (s, sum))

                    reports.append(u'</ul>')

                    reports.append(u'</li>')

                    indexTc += 1

                reports.append(u'</ul>')
                reports.append(u'</li>')

                index += 1

            # closing element for testplan and testglobal
            if self.__tp_name is not None:
                reports.append(u'</ul>')
                reports.append(u'</li>')

            reports.append(u'</ul>')

        except Exception as e:
            print('construct basic reports error: %s' % str(e))
        else:
            try:
                tpl_report = self.basic_report_tpl.replace(
                    "<!-- REPLACE_ME -->", self.__safestr2(datas=reports))

                # save to file
                f = open(
                    '%s/%s' %
                    (self.__path, self.__filename_basic_report), 'w')
                f.write(tpl_report)
                f.close()

            except Exception as e:
                print('save basic reports error: %s' % str(e))

    def saveReports(self, stoppedAt=0):
        """
        Save all reports
        """
        # read template files
        self.__initReportHeaderTpl()

        try:
            # i = 0
            reports = []

            reports.append(u'<html>')
            reports.append(u"%s" % self.report_header)
            reports.append(u"<body>")

            if TestSettings.get('Tests_Framework', 'header-test-report'):
                reports.append(self.getHeaderReport())

            stats, statsTu, statsTs, statsTp, statsTg = self.computeStatistics()

            # html reports
            reports.append(u'<ul>')
            reports.append(u'<li data-type="testdescription">')
            reports.append(u"<h1>General Test Description</h1>")

            reports.append(u"<table id='general'>")
            if self.__final_result == FAIL:
                reports.append(u"<tr><td class=\"header\">Global Result</td><td>")
                reports.append(u"<img alt=\"FAILED\"")
                reports.append(u"src=\"data:image/png;base64,%s\" />" % self.PNG_BASE64_FAILED)
                reports.append(u"</td></tr>")
            elif self.__final_result == UNDEFINED:
                reports.append(u"<tr><td class=\"header\">Global Result</td><td>")
                reports.append(u"<img alt=\"UNDEFINED\" ")
                reports.append(u"src=\"data:image/png;base64,%s\" />" % self.PNG_BASE64_UNDEFINED)
                reports.append(u"</td></tr>")
            else:
                reports.append(u"<tr><td class=\"header\">Global Result</td><td>")
                reports.append(u"<img alt=\"PASSED\" ")
                reports.append(u"src=\"data:image/png;base64,%s\" />" % self.PNG_BASE64_PASSED)
                reports.append(u"</td></tr>")

            reports.append(
                u"<tr><td class=\"header\">Duration</td><td>%.3f seconds</td></tr>" %
                self.scriptDuration)
            reports.append(
                u"<tr><td class=\"header\">Statistics</td><td>%s</td></tr>" %
                self.prepareStatistics(
                    stats, statsTu, statsTs, statsTp, statsTg))
            reports.append(
                u"<tr><td class=\"header\">Terminated At</td><td>%s</td></tr>" %
                time.strftime(
                    "%d/%m/%Y %H:%M:%S",
                    time.localtime(stoppedAt)))
            for (k, v) in self.description:
                if isinstance(v, list):
                    reports.append(
                        u"<tr><td class=\"header\">%s</td><td>%s</td></tr>" %
                        (k.title(), u'<br />'.join(v)))
                else:
                    reports.append(
                        u"<tr><td class=\"header\">%s</td><td>%s</td></tr>" %
                        (k.title(), v))
            reports.append(u"</table>")
            reports.append(u'</li><br />')

            # new in v16
            if TestSettings.get('Tests_Framework',
                                'expand-test-report') == "1":
                expanded = "checked"
            else:
                expanded = ""
            # end of new

            # adding info for testplan or testglobal
            if self.__tp_name is not None:
                if self.__tp_global:
                    reports.append(u'<li data-type="testglobal">')
                    reports.append(
                        u'<input type="checkbox" id="c0" %s />' %
                        expanded)
                    reports.append(
                        u"<label for=\"c0\"><h1>Test Global - %s</h1></label>" %
                        self.__tp_name)
                else:
                    reports.append(u'<li data-type="testplan">')
                    reports.append(
                        u'<input type="checkbox" id="c0" %s />' %
                        expanded)
                    reports.append(
                        u"<label for=\"c0\"><h1>Test Plan - %s</h1></label>" %
                        self.__tp_name)

                reports.append(u'<ul>')

                reports.append(u"<table id='description'>")
                reports.append(
                    u"<tr><td class=\"header\">Summary</td><td>%s</td></tr>" %
                    self.__tp_datasummary)
                reports.append(
                    u"<tr><td class=\"header\">Started At</td><td>%s</td></tr>" %
                    self.__tp_startedat)
                reports.append(
                    u"<tr><td class=\"header\">Duration</td><td>%.3f seconds</td></tr>" %
                    self.__tp_duration)
                if len(self.__tp_datainputs):
                    reports.append(
                        u"<tr><td class=\"header\">Data Inputs</td><td>%s</td></tr>" %
                        u"<br />".join(
                            self.prepareParameters(
                                self.__tp_datainputs)))
                if len(self.__tp_sutinputs):
                    reports.append(
                        u"<tr><td class=\"header\">SUT Inputs</td><td>%s</td></tr>" %
                        u"<br />".join(
                            self.prepareParameters(
                                self.__tp_sutinputs)))
                reports.append(u"</table>")

            # iterate each testsuites
            index = 1
            for tsId, ts in self.tcs.items():
                tsName = ts['name']
                if len(ts['alias']):
                    tsName = ts['alias']

                # new in v12.2
                if not int(ts['is-enabled']) and not ts['is-testplan']:
                    if ts['is-unit']:
                        reports.append(u'<li data-type="testdisabled">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Unit - %s [disabled]</i></h1>" %
                            tsName)
                    elif ts['is-tp-from-tg']:
                        reports.append(u'<li data-type="testdisabled">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Plan - %s [disabled]</i></h1>" %
                            tsName)
                    else:
                        reports.append(u'<li data-type="testdisabled">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Suite - %s [disabled]</i></h1>" %
                            tsName)
                    continue
                # end of new

                if not ts['is-executed']:
                    # new in v12.2
                    if ts['is-unit']:
                        reports.append(u'<li data-type="testnotexecuted">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Unit - %s [not executed]</i></h1>" %
                            tsName)
                    elif ts['is-tp-from-tg']:
                        reports.append(u'<li data-type="testnotexecuted">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Plan - %s [not executed]</i></h1>" %
                            tsName)
                    else:
                        reports.append(u'<li data-type="testnotexecuted">')
                        reports.append(
                            u"<h1 class=\"test_disabled\"><i>Test Suite - %s [not executed]</i></h1>" %
                            tsName)
                    # end of new
                    continue

                # decode summary only for testglobal or testplan
                if sys.version_info < (3,):
                    if self.__tp_name is not None:
                        ts['data-summary'] = ts['data-summary'].decode("utf8")

                if ts['is-unit']:
                    reports.append(u'<li data-type="testunit">')
                    reports.append(
                        u'<input type="checkbox" id="c%s" %s />' %
                        (index, expanded))
                    reports.append(
                        u"<label for=\"c%s\"><h1>Test Unit - %s</h1></label>" %
                        (index, tsName))

                    reports.append(u'<ul>')
                    reports.append(u"<table id='description'>")
                    reports.append(
                        u"<tr><td class=\"header\">Summary</td><td>%s</td></tr>" %
                        ts['data-summary'])
                    reports.append(
                        u"<tr><td class=\"header\">Started At</td><td>%s</td></tr>" %
                        ts['started-at'])
                    reports.append(
                        u"<tr><td class=\"header\">Duration</td><td>%.3f seconds</td></tr>" %
                        ts['duration'])
                    if len(ts['data-inputs']):
                        reports.append(
                            u"<tr><td class=\"header\">Data Inputs</td><td>%s</td></tr>" %
                            u"<br />".join(
                                self.prepareParameters(
                                    ts['data-inputs'])))
                    if len(ts['sut-inputs']):
                        reports.append(
                            u"<tr><td class=\"header\">SUT Inputs</td><td>%s</td></tr>" %
                            u"<br />".join(
                                self.prepareParameters(
                                    ts['sut-inputs'])))
                    reports.append(u"</table>")

                elif ts['is-testplan'] and ts['is-tp-started']:
                    reports.append(u'<li data-type="testplan">')
                    reports.append(
                        u'<input type="checkbox" id="c%s" %s />' %
                        (index, expanded))
                    reports.append(
                        u"<label for=\"c%s\"><h1>Test Plan - %s</h1></label>" %
                        (index, tsName))

                    reports.append(u'<ul>')
                    reports.append(u"<table id='description'>")
                    reports.append(
                        u"<tr><td class=\"header\">Summary</td><td>%s</td></tr>" %
                        ts['data-summary'])
                    reports.append(
                        u"<tr><td class=\"header\">Started At</td><td>%s</td></tr>" %
                        ts['started-at'])
                    reports.append(
                        u"<tr><td class=\"header\">Duration</td><td>%.3f seconds</td></tr>" %
                        ts['duration'])
                    reports.append(u"</table>")

                elif ts['is-testplan']:
                    reports.append(u'</ul>')

                else:
                    reports.append(u'<li data-type="testsuite">')
                    reports.append(
                        u'<input type="checkbox" id="c%s" %s />' %
                        (index, expanded))
                    reports.append(
                        u"<label for=\"c%s\"><h1>Test Suite: %s</h1></label>" %
                        (index, tsName))

                    reports.append(u'<ul>')
                    reports.append(u"<table id='description'>")
                    reports.append(
                        u"<tr><td class=\"header\">Summary</td><td>%s</td></tr>" %
                        ts['data-summary'])
                    reports.append(
                        u"<tr><td class=\"header\">Started At</td><td>%s</td></tr>" %
                        ts['started-at'])
                    reports.append(
                        u"<tr><td class=\"header\">Duration</td><td>%.3f seconds</td></tr>" %
                        ts['duration'])
                    if len(ts['data-inputs']):
                        reports.append(
                            u"<tr><td class=\"header\">Data Inputs</td><td>%s</td></tr>" %
                            u"<br />".join(
                                self.prepareParameters(
                                    ts['data-inputs'])))
                    if len(ts['sut-inputs']):
                        reports.append(
                            u"<tr><td class=\"header\">SUT Inputs</td><td>%s</td></tr>" %
                            u"<br />".join(
                                self.prepareParameters(
                                    ts['sut-inputs'])))
                    reports.append(u"</table>")

                # iterate each testcases
                for tc in ts['tc']:
                    # i += 1
                    reports.append(
                        u"<li class=\"step-section\">%s</li>" %
                        tc.getStepsManager().getReport())
                    reports.append(u"<br /><br />")

                if not ts['is-testplan']:
                    reports.append(u'</ul>')
                    reports.append(u'</li>')

                index += 1

            # closing element for testplan and testglobal
            if self.__tp_name is not None:
                reports.append(u'</ul>')
                reports.append(u'</li>')

            reports.append(u'</ul>')

            reports.append(u"</body>")
            reports.append(u"</html>")
        except Exception as e:
            print('construct reports error: %s' % str(e))
        else:
            try:
                # save to file
                f = open('%s/%s' % (self.__path, self.__filename_report), 'w')
                f.write(self.__safestr2(datas=reports))
                f.close()

            except Exception as e:
                print('save reports error: %s' % str(e))

    def saveReportsXml(self):
        """
        Save all reports as xml
        """
        try:
            i = 0
            reports = [u'<?xml version="1.0" encoding="UTF-8"?>']
            reports.append(u'<reports>')
            # iterate each testsuites
            for tsId, ts in self.tcs.items():
                # iterate each testcases
                for tc in ts['tc']:
                    i += 1
                    reports.append(u"\t<report id=\"%s\">" % i)
                    report = []
                    for line in tc.getStepsManager().getReportXml():
                        report.append(u"\t%s" % line)
                    reports.extend(report)
                    reports.append(u"\t</report>")
            reports[1] = u'<reports max="%s">' % i
            reports.append(u'</reports>')
        except Exception as e:
            print('construct reports xml error: %s' % str(e))
        else:
            try:
                # save to file
                f = open(
                    '%s/%s' %
                    (self.__path, self.__filename_report_xml), 'w')
                f.write(self.__safestr2(datas=reports))
                f.close()

            except Exception as e:
                print('save reports xml error: %s' % str(e))

    def saveToCsv(self):
        """
        Save to csv

        {  1: {'result': 'PASS', 'tc': [Testcase], 'name': 'test'}}
        """
        self.csv_separator = TestSettings.get('Csv_Tests_Results', 'separator')
        try:
            # formalize data
            result = [TestSettings.get('Csv_Tests_Results', 'header')]

            tpname = ''
            if self.__tp_name is not None:
                tpname = self.__tp_name
                if self.__tp_global:
                    result.append(self.csv_separator.join([TG,
                                                           tpname,
                                                           '',
                                                           '',
                                                           self.__tp_verdict]))
                else:
                    result.append(self.csv_separator.join([TP,
                                                           tpname,
                                                           '',
                                                           '',
                                                           self.__tp_verdict]))

            # iterate each testsuites
            subtp = None
            for tsId, ts in self.tcs.items():
                if not ts['is-executed']:
                    continue

                # new extract testplan in testglobal
                if ts['is-testplan'] and ts['is-tp-started']:
                    ts_name = ts['name']
                    if 'alias' in ts:
                        if len(ts['alias']):
                            ts_name = ts['alias']
                    if len(tpname):
                        tsname = r"%s\%s" % (tpname, ts_name)
                    else:
                        tsname = ts_name

                    result.append(self.csv_separator.join([TP,
                                                           tsname,
                                                           '',
                                                           '',
                                                           ts['result']]))
                    subtp = ts_name
                    continue
                if ts['is-testplan'] and not ts['is-tp-started']:
                    subtp = None
                    continue
                # end of new

                if subtp is None:
                    ts_name = ts['name']
                    if 'alias' in ts:
                        if len(ts['alias']):
                            ts_name = ts['alias']
                    if len(tpname):
                        tsname = r"%s\%s" % (tpname, ts_name)
                    else:
                        tsname = ts_name
                else:
                    ts_name = ts['name']
                    if 'alias' in ts:
                        if len(ts['alias']):
                            ts_name = ts['alias']
                    if len(tpname):
                        tsname = r"%s\%s\%s" % (tpname, subtp, ts_name)
                    else:
                        tsname = ts_name

                if ts['is-unit']:
                    result.append(self.csv_separator.join([TU,
                                                           tsname,
                                                           '',
                                                           '',
                                                           ts['result']]))
                else:
                    result.append(self.csv_separator.join([TS,
                                                           tsname,
                                                           '',
                                                           '',
                                                           ts['result']]))

                # iterate each testcases
                for tc in ts['tc']:
                    result.append(self.csv_separator.join([TC,
                                                           tsname,
                                                           tc.getTestname(),
                                                           '',
                                                           tc.get_final_verdict()]))

                    # iterate each steps
                    for stp in tc.getSteps():
                        result.append(self.csv_separator.join([STP,
                                                               tsname,
                                                               tc.getTestname(),
                                                               stp.getStep(),
                                                               stp.getVerdict()]))
        except Exception as e:
            print('construct csv error: %s' % str(e))
        else:
            try:
                # save to file
                f = open('%s/%s' % (self.__path, self.__filename), 'w')
                f.write(self.__safestr2(datas=result))
                f.close()
            except Exception as e:
                print('save csv error: %s' % str(e))

    def saveVerdictToXml(self):
        """
        Save verdict to xml
        """
        try:
            verdicts = [u'<?xml version="1.0" encoding="UTF-8"?>']
            attrs = []
            attrs.append("max=\"%s\"" % len(self.tcs))
            attrs.append("user=\"%s\"" % self.__username)
            attrs.append("project=\"%s\"" % xmlescape(self.__projectname))
            attrs.append("path=\"%s\"" % xmlescape(self.__testpath))
            attrs.append("name=\"%s\"" % xmlescape(self.__testname))
            verdicts.append(u'<tests %s>' % (" ".join(attrs)))

            i = 0
            for tsId, ts in self.tcs.items():
                if ts['is-testplan'] and not ts['is-tp-started']:
                    continue

                i += 1

                ts_name = ts['name']
                if 'alias' in ts:
                    if len(ts['alias']):
                        ts_name = ts['alias']

                status = "not-executed"
                if ts['is-executed']:
                    status = "executed"
                if not int(ts['is-enabled']) and not ts['is-testplan']:
                    status = "disabled"

                ext = ""
                if ts["is-unit"]:
                    ext = "tux"
                elif ts["is-testplan"]:
                    ext = "tpx"
                elif ts["is-tp-from-tg"]:  # test disabled
                    ext = "tpx"
                else:
                    ext = "tsx"

                test_attrs = []
                test_attrs.append("id=\"%s\"" % i)
                test_attrs.append("name=\"%s\"" % xmlescape(ts_name))
                test_attrs.append("result=\"%s\"" % ts['result'])
                test_attrs.append("max=\"%s\"" % len(ts['tc']))
                test_attrs.append("status=\"%s\"" % status)
                test_attrs.append("project=\"%s\"" % xmlescape(ts['project']))
                test_attrs.append("path=\"%s\"" % xmlescape(ts['path']))
                test_attrs.append("original=\"%s\"" % xmlescape(ts['name']))
                test_attrs.append("extension=\"%s\"" % ext)
                verdicts.append(u"\t<test %s>" % " ".join(test_attrs))

                j = 0
                for tc in ts['tc']:
                    j += 1

                    tc_end = " />"
                    if len(tc.getSteps()):
                        tc_end = " >"

                    tc_attrs = []
                    tc_attrs.append("id=\"%s\"" % j)
                    tc_attrs.append("name=\"%s\"" % xmlescape(tc.getTestname()))
                    tc_attrs.append("result=\"%s\"" % tc.get_final_verdict())
                    tc_attrs.append("max=\"%s\"" % len(tc.getSteps()))
                    verdicts.append(u"\t\t<testcase %s %s" % (" ".join(tc_attrs), tc_end))

                    h = 0
                    for stp in tc.getSteps():
                        h += 1

                        stp_attrs = []
                        stp_attrs.append("id=\"%s\"" % h)
                        stp_attrs.append("name=\"%s\"" % xmlescape(stp.getStep()))
                        stp_attrs.append("result=\"%s\"" % stp.getVerdict())
                        stp_attrs.append("actual=\"%s\"" % xmlescape(stp.getActual()))
                        verdicts.append(u"\t\t\t<step %s />" % " ".join(stp_attrs))

                    if len(tc.getSteps()):
                        verdicts.append(u"\t\t</testcase>")

                verdicts.append(u"\t</test>")
            verdicts.append(u'</tests>')
        except Exception as e:
            print('constructs verdicts xml error: %s' % str(e))
        else:
            try:
                # save to file
                f = open('%s/%s' % (self.__path, self.__filename_xml), 'w')
                f.write(self.__safestr2(datas=verdicts))
                f.close()
            except Exception as e:
                print('save verdicts xml error: %s' % str(e))

    def __safestr2(self, datas):
        """
        Encode latin1 to utf8
        """
        ret = []
        for l in datas:
            if sys.version_info > (3,):
                ret.append(l)
            else:
                ret.append(l.encode("utf8"))
        return '\n'.join(ret)

    def isTestStarted(self):
        """
        The test is started
        """
        self.tcs[self.id__]['is-executed'] = True

    def newTp(self, name, dataInputs=[], sutInputs=[], summary='',
              startedAt='', dataOutputs=[], sutOutputs=[]):
        """
        Add a new testplan
        """
        self.__tp_name = name
        self.__tp_datainputs = dataInputs
        self.__tp_sutinputs = sutInputs
        if sys.version_info > (3,):
            self.__tp_datasummary = summary
        else:
            self.__tp_datasummary = summary.decode("utf8")
        self.__tp_startedat = startedAt
        self.__tp_dataoutputs = dataOutputs
        self.__tp_sutoutputs = sutOutputs

    def newStopTpInTg(self, name, nameAlias=''):
        """
        Add a stop testplan in a testglobal
        Compute the result
        """
        self.newTs(name=name, isUnit=False, isEnabled=False, isTestPlan=True,
                   startTestPlan=False, isExecuted=True, nameAlias=nameAlias)
        self.getVerdictSubTp()

    def newStartTpInTg(self, name, nameAlias='', summary='',
                       startedAt='', testPath='/', testProject=''):
        """
        Add a start testplan in a testglobal
        """
        self.__sub_tp = self.newTs(name=name, isUnit=False,
                                   isEnabled=False, isTestPlan=True,
                                   startTestPlan=True, isExecuted=True,
                                   nameAlias=nameAlias,
                                   summary=summary, startedAt=startedAt,
                                   testPath=testPath, testProject=testProject)

    def newTs(self, name, isUnit=False, isAbstract=False,
              isEnabled=False, isTestPlan=False,
              startTestPlan=False, isExecuted=False, nameAlias='',
              dataInputs=[], sutInputs=[], summary='',
              startedAt='', dataOutputs=[], sutOutputs=[],
              isTpFromTg=False, testPath='/',
              testProject='', dataDescriptions=[]):
        """
        Add a new testsuite
        """
        # new in 17.1, save the progress
        self.progress += 1
        self.saveProgress()
        # end of new

        self.id__ += 1

        if sys.version_info > (3,):
            _summary = summary
        else:
            _summary = summary.decode("utf8")

        self.tcs[self.id__] = {'result': UNDEFINED,
                               'tc': [],
                               'name': name,
                               'is-unit': isUnit,
                               'is-abstract': isAbstract,
                               'data-outputs': dataOutputs,
                               'sut-outputs': sutOutputs,
                               'is-enabled': isEnabled,
                               'is-executed': isExecuted,
                               'alias': nameAlias,
                               'is-testplan': isTestPlan,
                               'is-tp-started': startTestPlan,
                               'duration': 0,
                               'data-inputs': dataInputs,
                               'sut-inputs': sutInputs,
                               'data-summary': _summary,
                               'path': testPath,
                               'project': testProject,
                               'started-at': startedAt,
                               'is-tp-from-tg': isTpFromTg,
                               'data-descriptions': dataDescriptions,
                               "errors": []}
        return self.id__

    def newTu(self, name, isEnabled=False, nameAlias='', dataInputs=[], sutInputs=[],
              summary='', startedAt='', dataOutputs=[],
              sutOutputs=[], testPath='/', testProject='',
              dataDescriptions=[]):
        """
        Add a new testunit
        """
        self.newTs(name=name, isUnit=True, isEnabled=isEnabled,
                   nameAlias=nameAlias, dataInputs=dataInputs,
                   sutInputs=sutInputs, summary=summary,
                   startedAt=startedAt, dataOutputs=dataOutputs,
                   sutOutputs=sutOutputs, testPath=testPath,
                   testProject=testProject,
                   dataDescriptions=dataDescriptions)

    def addTestDuration(self, duration=0):
        """
        Add test duration
        """
        self.tcs[self.id__]['duration'] = duration

    def updateTestDuration(self, id, duration=0):
        """
        Add test duration
        """
        self.tcs[id]['duration'] += duration

    def getDuration(self):
        """
        """
        return self.tcs[id]['duration']

    def addSubTestPlanDuration(self, duration=0):
        """
        Add test duration
        """
        self.tcs[self.__sub_tp]['duration'] = duration

    def addSummary(self, summary=[]):
        """
        """
        self.tcs[self.id__]['data-summary'] = summary

    def addDescriptions(self, descriptions=[]):
        """
        """
        self.tcs[self.id__]['data-descriptions'] = descriptions

    def addInputs(self, dataInputs=[], sutInputs=[]):
        """
        """
        self.tcs[self.id__]['data-inputs'] = dataInputs
        self.tcs[self.id__]['sut-inputs'] = sutInputs

    def addTestPlanDuration(self, duration=0):
        """
        Add test plan or test global duration
        """
        self.__tp_duration = duration

    def addScriptDuration(self, duration=0):
        """
        Add test duration
        """
        # new in 17.1, save the progress
        self.progress = self.nbtests
        self.saveProgress()
        # end of new

        self.scriptDuration = duration

    def addTc(self, tc):
        """
        Add a new testcase
        """
        self.tcs[self.id__]['tc'].append(tc)

    def computeResults(self):
        """
        Recompute all test result at end (parallel testing changed)
        """
        subTpResult = None
        tpDetected = None
        finalResult = None

        for tsId, test in self.tcs.items():
            if not test['is-executed']:
                continue

            # detect the begin of a test plan
            if test['is-testplan'] and test['is-tp-started']:
                tpDetected = test
                continue

            # detect the end of a test plan
            if test['is-testplan'] and not test['is-tp-started']:
                if subTpResult is None:
                    tpDetected['result'] = UNDEFINED
                else:
                    tpDetected['result'] = subTpResult
                tpDetected = None
                subTpResult = None
                continue

            # recompute all tc results
            tcResults = None
            for tc in test['tc']:
                if tc.get_final_verdict() == PASS and tcResults is None:
                    tcResults = tc.get_final_verdict()

                if tc.get_final_verdict() == FAIL:
                    tcResults = tc.get_final_verdict()

                if tc.get_final_verdict() == UNDEFINED:
                    tcResults = tc.get_final_verdict()
                    break

            if tpDetected is not None:
                if tcResults is None:
                    subTpResult = UNDEFINED
                else:
                    if tcResults == FAIL:
                        subTpResult = FAIL
                    if tcResults == UNDEFINED:
                        subTpResult = UNDEFINED
                    if tcResults == PASS and subTpResult is None:
                        subTpResult = PASS

                if tcResults is None:
                    test['result'] = UNDEFINED
                else:
                    test['result'] = tcResults

                if finalResult == UNDEFINED:
                    continue

                if subTpResult == FAIL:
                    finalResult = FAIL
                if subTpResult == UNDEFINED:
                    finalResult = UNDEFINED
                if subTpResult == PASS and finalResult is None:
                    finalResult = PASS

            else:
                if tcResults is None:
                    test['result'] = UNDEFINED
                else:
                    test['result'] = tcResults

                if finalResult == UNDEFINED:
                    continue

                if test['result'] == FAIL:
                    finalResult = FAIL
                if test['result'] == UNDEFINED:
                    finalResult = UNDEFINED
                if test['result'] == PASS and finalResult is None:
                    finalResult = PASS

        if self.__tp_name is not None:
            if finalResult is None:
                self.__tp_verdict = UNDEFINED
            else:
                self.__tp_verdict = finalResult
        else:
            if finalResult is None:
                finalResult = UNDEFINED

        return finalResult

    def getVerdictSubTp(self):
        """
        Return the verdict of a sub testplan in a testglobal
        """
        verdict = UNDEFINED
        tpDetected = False
        for tid, test in self.tcs.items():
            if tpDetected:
                # detect the end of the testplan
                if test['is-testplan'] and not test['is-tp-started']:
                    break

                if test['result'] == PASS:
                    verdict = PASS
                if test['result'] == UNDEFINED:
                    verdict = UNDEFINED
                    break
                if test['result'] == FAIL:
                    verdict = FAIL
                    break

            # detect the begin of the testplan
            if int(self.__sub_tp) == int(tid):
                tpDetected = True

        # set the final result
        self.tcs[self.__sub_tp]['result'] = verdict
        self.__sub_tp = 0

    def getVerdictTs(self):
        """
        Return the verdict of the testsuite

        @return:
        @rtype:
        """
        verdict = self.tcs[self.id__]['result']
        if len(self.tcs[self.id__]['tc']) == 0:
            return UNDEFINED
        verdict_alway_undef = True
        for tc in self.tcs[self.id__]['tc']:
            if tc.get_final_verdict() == UNDEFINED:
                verdict_alway_undef = False
                verdict = UNDEFINED
            if tc.get_final_verdict() == FAIL:
                verdict_alway_undef = False
                verdict = FAIL
        if verdict_alway_undef:
            verdict = PASS
        self.tcs[self.id__]['result'] = verdict
        return verdict

    def getNbTc(self):
        """
        Return the number of testcase
        """
        nbTc = 0
        for tid, tvar in self.tcs.items():
            nbTc += len(tvar['tc'])
        return nbTc

    def getNbTs(self):
        """
        Return the number of testsuite
        """
        nbTs = 0
        for tid, tvar in self.tcs.items():
            if tvar['is-unit'] is False:
                nbTs += 1
        return nbTs

    def getNbTu(self):
        """
        Return the number of testunit
        """
        nbTu = 0
        for tid, tvar in self.tcs.items():
            if tvar['is-unit'] is True:
                nbTu += 1
        return nbTu

    def getVerdictTp(self):
        """
        Return the verdict of the testplan

        @return:
        @rtype:
        """
        verdict = UNDEFINED
        if len(self.tcs) == 0:
            return UNDEFINED
        badResult = False
        for ts in self.tcs.values():
            if ts['is-testplan'] is True:
                continue

            if not ts['is-executed']:
                continue
            if ts['result'] == UNDEFINED:
                verdict = UNDEFINED
                badResult = True
                break
            if ts['result'] == FAIL:
                verdict = FAIL
                badResult = True
        if not badResult:
            verdict = PASS
        self.__tp_verdict = verdict
        return verdict

    def getTestResult(self):
        """
        Get test result
        """
        return self.__path

    def getRelativeTestResult(self):
        """
        Get test result
        """
        return self.__relativePath


__TestSuitesManager = TestSuitesManager()


def getTsMgr():
    """
    Return the testsuite manager
    """
    global __TestSuitesManager
    ret = __TestSuitesManager
    return ret


class TestCasesManager(object):
    """
    """

    def __init__(self):
        """
        """
        self.__tcs = []

    def addTc(self, tc, tcArgs):
        """
        """
        self.__tcs.append((tc, tcArgs))

    def endingAll(self):
        """
        """
        for (tc, tcArgs) in self.__tcs:
            if tc.hasSharedAdapters():
                tc.endingDelayed(**tcArgs)


__TestCasesManager = TestCasesManager()


def getTcMgr():
    """
    Return the testcae manager
    """
    global __TestCasesManager
    ret = __TestCasesManager
    return ret


class Test(object):
    """
    Test handler
    """

    def __init__(self, parent):
        """
        Constructor
        """
        self.tcparent = parent

    def terminate(self, err=None):
        """
        Use this function to stop the test before the end
        Cleanup is called automatically and the aborted
        argument contains the reason of the termination

        @param err: error message
        @type err: string/none
        """
        err_msg = err
        if err is None:
            err_msg = ''

        self.tcparent.warning("Terminating...")
        raise AbortStopException(err_msg)

    def interrupt(self, err=None):
        """
        Use this function to stop the testcase before the end
        Cleanup is called automatically and the aborted
        argument contains the reason of the interruption

        @param err: error message
        @type err: string/none
        """
        err_msg = err
        if err is None:
            err_msg = ''
        self.tcparent.warning("Interrupting testcase...")
        raise AbortException(err_msg)


class Trace(object):
    """
    Trace message in your test
    """

    def __init__(self, parent):
        """
        Constructor
        """
        self.tcparent = parent

    def info(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an information message
        Nothing is displayed if txt is None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        self.tcparent.info(txt=txt,
                           bold=bold,
                           italic=italic,
                           multiline=multiline,
                           raw=raw)

    def error(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an error message
        Nothing is displayed if txt is None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        self.tcparent.error(txt=txt,
                            bold=bold,
                            italic=italic,
                            multiline=multiline,
                            raw=raw)

    def warning(self, txt, bold=False, italic=False,
                multiline=False, raw=False):
        """
        Display an warning message
        Nothing is displayed if txt is None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        self.tcparent.warning(txt=txt,
                              bold=bold,
                              italic=italic,
                              multiline=multiline,
                              raw=raw)


class Interact(object):
    """
    Interact with user
    """

    def __init__(self, parent):
        """
        Constructor
        """
        self.tcparent = parent

    def interact(self, ask, timeout=30.0, default=None, cache=''):
        """
        Ask a value to the tester during the execution of a test

        @param ask: ask what
        @type ask: string

        @param default: provide a default value
        @type default: string/none

        @param cache: max time to respond (default=30s)
        @type cache: float

        @param timeout: key name
        @type timeout: string

        @return: user response
        @rtype: string
        """
        rsp = self.tcparent.interact(ask=ask,
                                     timeout=timeout,
                                     default=default)
        if len(cache) and rsp is not None:
            Cache().set(name=cache, data=rsp, flag=False)
        return rsp


class Cache(object):
    """
    Cache storage based on key, value
    Shared between all testcases.
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def capture(self, data, regexp):
        """
        Capture group of characters and save it in cache

        @param data: raw data
        @type name: string

        @param regexp: reg exp used to capture string (example: (?P<R>.*))
        @type regexp: string
        """
        reg = re.search(regexp, data, re.S)
        if reg is not None:
            if len(reg.groups()):
                # save group in cache
                cur = TDS.instance().load_data()
                if cur is None:
                    cur = {}

                if not isinstance(cur, dict):
                    return

                cur.update(reg.groupdict())
                TDS.instance().save_data(data=cur)
            else:
                return
        else:
            return

    def set(self, name, data, flag=False):
        """
        Save data in the temporary storage.
        Prefix the name with _ if you want to keep the key in the cache even with a reset

        @param name: key name
        @type name: string

        @param data: data to save
        @type data: string/object
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {name: data}

        if not isinstance(cur, dict):
            return

        cur.update({name: data})
        TDS.instance().save_data(data=cur)

    def all(self):
        """
        Return all content from the cache

        @return: content
        @rtype: object/none
        """
        return TDS.instance().load_data()

    def get(self, name):
        """
        Load data from the temporary storage according to the name passed as argument.

        @param name: key name
        @type name: string

        @return: data saved or None if empty
        @rtype: object/none
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {}

        if not isinstance(cur, dict):
            return

        if name in cur:
            return cur[name]
        else:
            return None

    def delete(self, name):
        """
        Delete data from the temporary storage
        according to the name passed as argument.

        @param name: key name
        @type name: string

        @return: True on success, False otherwise
        @rtype: boolean
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {}

        if not isinstance(cur, dict):
            return
        if name in cur:
            cur.pop(name)
            # save data in cache
            TDS.instance().save_data(data=cur)
            return True
        else:
            return False

    def reset(self, all=False):
        """
        Reset data from the temporary storage.
        Reminder: all keys startswiths "_" are not removed
        """
        if all:
            TDS.instance().save_data(data={})
        else:
            new_cache = {}
            cur = TDS.instance().load_data()
            if cur is None:
                TDS.instance().save_data(data={})
            else:
                if not isinstance(cur, dict):
                    return TDS.instance().save_data(data={})

                for k, v in cur.items():
                    if k.startswith("_"):
                        new_cache[k] = v
                TDS.instance().save_data(data=new_cache)


class Public(object):
    """
    Public storage files
    """

    def __init__(self, parent):
        """
        Constructor for a break point
        Parent should be equal to a testcase
        """
        self.tcparent = parent

    def getPath(self):
        """
        Return path to access to public area

        @return: public path
        @rtype: string
        """
        publicPath = "%s/" % TestSettings.get('Paths', 'public')
        return "%s/" % os.path.normpath(publicPath)

    def getFile(self, pathfile):
        """
        Get file from the public area

        @param pathfile: filename to read
        @type pathfile: string

        @return: file content
        @rtype: string
        """
        data = ''
        try:
            f = open("%s/%s" % (self.getPath(), pathfile), 'rb')
            data = f.read()
            f.close()
        except OSError as e:
            raise PrivateException("os error on get public file: %s" % e)
        return data

    def addFolder(self, folder):
        """
        Add folder in the public area

        @param folder: folder name to add
        @type folder: string
        """
        try:
            os.mkdir("%s/%s" % (self.getPath(), folder), 0o755)
        except OSError as e:
            raise PrivateException("os error on add public folder: %s" % e)

    def saveFile(self, pathfile, data):
        """
        Save file in public area

        @param pathfile: destination path file
        @type pathfile: string

        @param data: data to save
        @type data: string
        """
        try:
            f = open("%s/%s" % (self.getPath(), pathfile), 'wb')
            if sys.version_info > (3,):
                f.write(data.encode())
            else:
                f.write(data)
            f.close()
        except OSError as e:
            raise PrivateException("os error on write public file: %s" % e)

    def appendFile(self, pathfile, data):
        """
        Append data in file in public area

        @param pathfile: destination path file
        @type pathfile: string

        @param data: data to save
        @type data: string
        """
        try:
            f = open("%s/%s" % (self.getPath(), pathfile), 'ab')
            if sys.version_info > (3,):
                f.write(data.encode())
            else:
                f.write(data)
            f.close()
        except OSError as e:
            raise PrivateException("os error on append public file: %s" % e)


class Private(object):
    """
    Private storage files
    """

    def __init__(self, parent):
        """
        Constructor for a break point
        Parent should be equal to a testcase
        """
        self.tcparent = parent

    def getPath(self):
        """
        Return path to access to the private area of the testcase

        @return: public path
        @rtype: string
        """
        privatePath = self.tcparent.getDataStoragePath()
        return "%s/" % os.path.normpath(privatePath)

    def getFile(self, filename):
        """
        Get file in private area

        @param filename: filename to read
        @type filename: string

        @return: file content
        @rtype: string
        """
        data = ''
        try:
            f = open("%s/%s" % (self.getPath(), filename), 'rb')
            data = f.read()
            f.close()
        except OSError as e:
            raise PrivateException("os error on get file: %s" % e)
        return data

    def addFolder(self, folder):
        """
        Add folder in the private area

        @param folder: folder name to add
        @type folder: string
        """
        try:
            os.mkdir("%s/%s" % (self.getPath(), folder), 0o755)
        except OSError as e:
            raise PrivateException("os error on add folder: %s" % e)

    def saveFile(self, destname, data):
        """
        Storing binary data in file. These datas are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        self.tcparent.saveFile(destname=destname, data=data)

    def appendFile(self, destname, data):
        """
        Append binary data in file. These datas are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        self.tcparent.appendFile(destname=destname, data=data)


class BreakPoint(object):
    """
    Add a break point
    """

    def __init__(self, parent):
        """
        Constructor for a break point
        """
        self.tcparent = parent

        if not isinstance(parent, TestCase):
            raise BreakpointException(
                "ERR_BKP_004: testcase expected (%s)" %
                type(parent))

        if getTsMgr().getBreakpoint():
            rsp = self.tcparent.breakpoint(testId=getTsMgr().getTestId())
            if rsp is None:
                raise BreakpointException(
                    "ERR_BKP_003: System error on breakpoint action")
            else:
                if rsp == 'cancel':
                    raise BreakpointException(
                        "ERR_BKP_001: Breakpoint cancelled")
                elif rsp == 'continue':
                    pass
                else:
                    raise BreakpointException(
                        "ERR_BKP_002: System breakpoint - unknown response %s" % rsp)


class Timer(object):
    """
    Time handler
    """

    def __init__(self, parent):
        """
        Constructor for the time handler
        """
        self.tcparent = parent

    def sleep(self, timeout, localshift=True):
        """
        Sleep in seconds with time shifting support

        @param timeout: in second
        @type timeout: integer

        @param localshift: local shift (default=True)
        @type localshift: boolean
        """
        self.tcparent.sleep(timeout=timeout, localshift=localshift)

    def sleepUntil(self, dt="1970-01-01 00:00:00", fmt="%Y-%m-%d %H:%M:%S",
                   localshift=True, delta=0):
        """
        Sleep until a specific date and time with time shifting support

        @param dt: date and time (default=1970-01-01 00:00:00)
        @type dt: string

        @param fmt: date and time format (default=%Y-%m-%d %H:%M:%S)
        @type fmt: string

        @param localshift: local shift (default=True)
        @type localshift: boolean

        @param delta: shift the date in seconds (default=0s)
        @type delta: integer
        """
        self.tcparent.sleepUntil(dt=dt,
                                 fmt=fmt,
                                 localshift=localshift,
                                 delta=delta)

    def wait(self, timeout):
        """
        Just wait during the timeout passed as argument

        @param timeout: in second
        @type timeout: float
        """
        self.tcparent.wait(timeout=timeout)

    def waitUntil(self, dt="1970-01-01 00:00:00",
                  fmt="%Y-%m-%d %H:%M:%S", delta=0):
        """
        Just wait until the date and time passed in argument

        @param dt: date and time (default=1970-01-01 00:00:00)
        @type dt: string

        @param fmt: date and time format (default=%Y-%m-%d %H:%M:%S)
        @type fmt: string

        @param delta: shift the date in seconds (default=0s)
        @type delta: integer
        """
        try:
            self.tcparent.waitUntil(dt=dt.strip(),
                                    fmt=fmt.strip(),
                                    delta=delta)
        except ValueError as e:
            raise TimeException(
                'ERR_TIME_001: bad date/time format provided - %s' %
                e)

    def utc(self, fmt="%Y-%m-%d %H:%M:%S"):
        """
        Return UTC time

        @param fmt: date and time format (default=%Y-%m-%d %H:%M:%S)
        @type fmt: string

        @return: utc time
        @rtype: string
        """
        return time.strftime(fmt, time.gmtime())

    def local(self, fmt="%Y-%m-%d %H:%M:%S"):
        """
        Return local time

        @param fmt: date and time format (default=%Y-%m-%d %H:%M:%S)
        @type fmt: string

        @return: local time
        @rtype: string
        """
        return time.strftime(fmt, time.localtime())


Time = Timer  # just for backward compatibility

STEP_NAME = "Step"


class Step(object):
    """
    Step with definition result support.

    3 states supported:
        - UNDEFINED
        - FAIL
        - PASSED
    """

    def __init__(self, parent, tcid_, id_, expected_, action_, summary_,
                 enabled=True, thumbnail=None):
        """
        Constructor for a step

        @param tcid_:
        @type tcid_:

        @param id_:
        @type id_:

        @param expected_:
        @type expected_:

        @param action_:
        @type action_:

        @param summary_:
        @type summary_:
        """
        self.tcparent = parent
        self.tcid_ = tcid_
        self.id_ = id_
        self.expected_ = expected_
        self.action_ = action_
        self.summary_ = summary_
        self.verdict = UNDEFINED
        self.actual_ = []
        self.actual_raw = ''
        self.started = False
        self.enabled = enabled

        self.actual_thumbnail = None
        self.actual_chart = None
        self.action_thumbnail = thumbnail

    def updateParent(self, parent, tcid):
        """
        """
        self.tcparent = parent
        self.tcid_ = tcid

    def __repr__(self):
        """
        repr
        """
        return STEP_NAME

    def __str__(self):
        """
        str
        """
        return STEP_NAME

    def __unicode__(self):
        """
        unicode
        """
        return STEP_NAME

    def setDisabled(self):
        """
        Disable the step

        """
        self.enabled = False

    def setEnabled(self):
        """
        Enable the step
        """
        self.enabled = True

    def isEnabled(self):
        """
        Return True if the step is enabled

        @return: True for enabled, False otherwise
        @rtype: boolean
        """
        return self.enabled

    def setSummary(self, summary):
        """
        Set the summary

        @param summary: summary
        @type summary: string
        """
        if sys.version_info > (3,):
            self.summary_ = summary
        else:
            self.summary_ = summary.decode("utf8")

    def setDescription(self, description):
        """
        Set action to execute the step

        @param description: description
        @type description: string
        """
        if sys.version_info > (3,):
            self.action_ = description
        else:
            self.action_ = description.decode("utf8")

    def setExpected(self, expected):
        """
        Step the result expected

        @param expected: expected
        @type expected: string
        """
        if sys.version_info > (3,):
            self.expected_ = expected
        else:
            self.expected_ = expected.decode("utf8")

    def getId(self):
        """
        Return id
        """
        return self.id_

    def getStep(self):
        """
        Return step as string
        """
        return "Step %s" % self.id_

    def getVerdict(self):
        """
        Return verdict

        @return:
        @rtype:
        """
        return self.verdict

    def getDesign(self):
        """
        Return the design
        """
        return u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            self.getId(), self.getSummary(),
            self.getAction(), self.getExpected())

    def getDesignXml(self):
        """
        Return design as xml
        """
        ret = [u"\t<step id=\"%s\">" % self.getId()]
        ret.append(
            u"\t\t<summary><![CDATA[%s]]></summary>" %
            self.getSummary())
        ret.append(u"\t\t<action><![CDATA[%s]]></action>" % self.getAction())
        ret.append(
            u"\t\t<expected><![CDATA[%s]]></expected>" %
            self.getExpected())
        ret.append(u"\t</step>")
        return ret

    def getSummary(self):
        """
        Return the summary
        """
        if sys.version_info > (3,):
            return self.summary_
        else:
            return self.summary_.decode("utf8")

    def getExpected(self):
        """
        Return expected string
        """
        if sys.version_info > (3,):
            return self.expected_
        else:
            return self.expected_.decode("utf8")

    def getActual(self):
        """
        Return actual string
        """
        try:
            if self.actual_thumbnail is not None:
                imgB64 = None
                if sys.version_info > (3,):
                    imgB64 = base64.b64encode(self.actual_thumbnail)
                    imgB64 = imgB64.decode("utf8")
                else:
                    imgB64 = base64.b64encode(self.actual_thumbnail)
                if imgB64 is not None:
                    self.actual_.append(
                        u"<img src=\"data:image/png;base64,%s\" alt=\"thumbnail\" >" %
                        imgB64)
        except Exception as e:
            print("get actual on step error: %s" % e)

        try:
            if self.actual_chart is not None:
                self.actual_.append(self.actual_chart)
        except Exception:
            pass

        return u'<br />'.join(self.actual_)

    def getAction(self):
        """
        Return action string
        """
        if sys.version_info > (3,):
            ret = self.action_
        else:
            ret = self.action_.decode("utf8")

        try:
            if self.action_thumbnail is not None:
                imgB64 = None
                if sys.version_info > (3,):
                    imgB64 = base64.b64encode(self.action_thumbnail)
                    imgB64 = imgB64.decode("utf8")
                else:
                    imgB64 = base64.b64encode(self.action_thumbnail)

                if imgB64 is not None:
                    ret = u"%s<br /><img src=\"data:image/png;base64,%s\" alt=\"thumbnail\" >" % (
                        self.action_, imgB64)
        except Exception as e:
            print("get action on step error: %s" % e)

        return ret

    def start(self):
        """
        Begin to run the step
        """
        # already started before ?
        if self.started:
            raise StepException("ERR_STP_001: step %s already started" % self.id_)

        self.started = True
        runStep = False

        if self.summary_ is not None:
            stpSummary = self.summary_
        else:
            stpSummary = self.action_

        # run step by step ?
        if not getTsMgr().getStepByStep():
            runStep = True
        else:
            rsp = self.tcparent.pause(
                testId=getTsMgr().getTestId(),
                stepId=self.id_,
                stepSummary=stpSummary)
            if rsp is None:
                raise StepException("ERR_STP_004: System error on "
                                    "pause action for step %s" % self.id_)
            else:
                if rsp == 'cancel':
                    raise StepException("ERR_STP_002: Step %s cancelled" % self.id_)
                elif rsp == 'run':
                    runStep = True
                else:
                    raise StepException("ERR_STP_003: System pause: unknown "
                                        "response %s for step %s" % (rsp, self.id_))

        if runStep:
            if self.summary_ is not None:
                shortMsg = self.summary_
            else:
                shortMsg = self.action_

            # create template
            tpl = TestTemplatesLib.TemplateMessage()
            tpl_layer = TestTemplatesLib.TemplateLayer(
                name="Step %s" % self.id_)
            if self.summary_ is not None:
                tpl_layer.addKey(name='summary', data=self.summary_)
            tpl_layer.addKey(name='expected', data=self.expected_)
            if self.action_ is not None:
                tpl_layer.addKey(name='action', data=self.action_)
            if self.action_thumbnail is not None:
                tpl_layer.addKey(
                    name='action-thumbnail',
                    data=self.action_thumbnail)
            tpl_layer.addKey(name='result', data=self.verdict)
            tpl.addLayer(tpl_layer)

            # log event
            TLX.instance().log_step_started(dataMsg=tpl.getEvent(),
                                            shortMsg=shortMsg,
                                            fromComponent="%s [Step_%s]" % (
                                                TC, self.id_),
                                            tcid=self.tcid_,
                                            fromlevel=LEVEL_TE,
                                            tolevel=LEVEL_USER,
                                            testInfo=self.tcparent.getTestInfo(),
                                            step_id=self.id_)

            self.saveStep()

    def saveStep(self):
        """
        Save step in file
        """
        step = {'testcase': self.tcparent.getTestname(),
                'id': self.getId(),
                'result': self.getVerdict(),
                'summary': self.getSummary(),
                'expected': self.getExpected(),
                'actual': self.getActual(),
                'action': self.getAction()}
        f = open("%s/STEPS" % self.tcparent.getTestResultPath(), "w")
        f.write(json.dumps(step))
        f.close()

    def setFailed(self, actual, thumbnail=None, chart=None):
        """
        Set the result of the testcase to failed

        @param actual: result description
        @type actual: string

        @param thumbnail: image (default=None)
        @type thumbnail: string/none

        @param chart: chart, only displayed in html report (default=None)
        @type chart: string/none
        """
        if not self.started:
            raise StepException("ERR_STP_005: step %s not started" % self.id_)

        # convert all types to str
        actual = "%s" % actual

        self.actual_thumbnail = thumbnail
        if chart is not None:
            if not chart.startswith("<!-- BEGIN_CHART_REPORT -->"):
                raise StepException("ERR_STP_006: bad begin chart provided")
            if not chart.endswith("<!-- END_CHART_REPORT -->"):
                raise StepException("ERR_STP_006: bad end chart provided")
        self.actual_chart = chart

        if sys.version_info > (3,):
            self.actual_.append(actual)
            self.actual_raw += actual + '\n'
        else:
            self.actual_.append(actual.decode("utf8"))
            self.actual_raw += actual.decode('utf8') + '\n'

        self.verdict = FAIL

        # create template
        tpl = TestTemplatesLib.TemplateMessage()
        tpl_layer = TestTemplatesLib.TemplateLayer(name="Step %s" % self.id_)
        if self.summary_ is not None:
            tpl_layer.addKey(name='summary', data=self.summary_)
        tpl_layer.addKey(name='expected', data=self.expected_)
        if self.action_ is not None:
            tpl_layer.addKey(name='action', data=self.action_)
        if self.action_thumbnail is not None:
            tpl_layer.addKey(
                name='action-thumbnail',
                data=self.action_thumbnail)
        if actual is not None:
            tpl_layer.addKey(name='actual', data=self.actual_raw)
        if thumbnail is not None:
            tpl_layer.addKey(
                name='actual-thumbnail',
                data=self.actual_thumbnail)
        tpl_layer.addKey(name='result', data=self.verdict)
        tpl.addLayer(tpl_layer)

        # log event
        TLX.instance().log_step_failed(dataMsg=tpl.getEvent(),
                                       shortMsg=actual,
                                       fromComponent="%s [Step_%s]" % (
                                           TC, self.id_),
                                       tcid=self.tcid_,
                                       fromlevel=LEVEL_TE,
                                       tolevel=LEVEL_USER,
                                       testInfo=self.tcparent.getTestInfo(),
                                       step_id=self.id_)

        self.saveStep()

        continueRun = TestSettings.getInt(
            'Tests_Framework', 'continue-on-step-error')
        if not continueRun:
            raise AbortException("step on error, don't continue")

    def setPassed(self, actual="", thumbnail=None, chart=None):
        """
        Set the result of the testcase to passed

        @param actual: result description
        @type actual: string

        @param thumbnail: image (default=None)
        @type thumbnail: string/none

        @param chart: chart, only displayed in html report (default=None)
        @type chart: string/none
        """
        if not self.started:
            raise StepException("ERR_STP_005: step %s not started" % self.id_)

        if not (isinstance(actual, str) or isinstance(actual, unicode)):
            raise StepException(
                "ERR_STP_007: bad type provided on actual step (%s)" %
                type(actual))

        self.actual_thumbnail = thumbnail
        if chart is not None:
            if not chart.startswith("<!-- BEGIN_CHART_REPORT -->"):
                raise StepException("ERR_STP_006: bad begin chart provided")
            if not chart.endswith("<!-- END_CHART_REPORT -->"):
                raise StepException("ERR_STP_006: bad end chart provided")
        self.actual_chart = chart

        if sys.version_info > (3,):
            self.actual_.append("%s" % actual)
            self.actual_raw += "%s" % actual + '\n'
        else:
            self.actual_.append(str(actual).decode("utf8"))
            self.actual_raw += str(actual).decode('utf8') + '\n'

        if self.verdict == FAIL:
            pass  # don't change the verdict if the step is already fail,
            # we can call several the setPassed function
        else:
            self.verdict = PASS

        # Create template
        tpl = TestTemplatesLib.TemplateMessage()
        tpl_layer = TestTemplatesLib.TemplateLayer(name="Step %s" % self.id_)
        if self.summary_ is not None:
            tpl_layer.addKey(name='summary', data=self.summary_)
        tpl_layer.addKey(name='expected', data=self.expected_)
        if self.action_ is not None:
            tpl_layer.addKey(name='action', data=self.action_)
        if self.action_thumbnail is not None:
            tpl_layer.addKey(
                name='action-thumbnail',
                data=self.action_thumbnail)
        if actual is not None:
            tpl_layer.addKey(name='actual', data=self.actual_raw)
        if thumbnail is not None:
            tpl_layer.addKey(
                name='actual-thumbnail',
                data=self.actual_thumbnail)
        tpl_layer.addKey(name='result', data=self.verdict)
        tpl.addLayer(tpl_layer)

        # log event
        TLX.instance().log_step_passed(dataMsg=tpl.getEvent(),
                                       shortMsg=actual,
                                       fromComponent="%s [Step_%s]" % (
                                           TC, self.id_),
                                       tcid=self.tcid_,
                                       fromlevel=LEVEL_TE,
                                       tolevel=LEVEL_USER,
                                       testInfo=self.tcparent.getTestInfo(),
                                       step_id=self.id_)
        self.saveStep()


class StepManager(object):
    """
    Step manager
    """

    def __init__(self, tcid, parent=None):
        """
        Constructor for the step manager

        @param tcid:
        @type tcid:
        """
        self.steps_ = []
        self.tcid_ = tcid
        self.parent = parent

    def updateParent(self, parent, tcid):
        """
        """
        self.parent = parent
        self.tcid_ = tcid
        for stp in self.steps_:
            stp.updateParent(parent, tcid)

    def testcase(self):
        """
        accessor
        """
        return self.parent

    def getSteps(self):
        """
        Return all steps
        """
        __steps__ = []
        for stp in self.steps_:
            if stp.isEnabled():
                __steps__.append(stp)
        return __steps__

    def getNbSteps(self):
        """
        Return the number of steps
        """
        return len(self.getSteps())

    def addStep(self, action="", expected="", summary="", enabled=True, thumbnail=None):
        """
        Add a step

        @param action:
        @type action:

        @param expected:
        @type expected:

        @return:
        @rtype:
        """
        stp_ = Step(parent=self.parent, tcid_=self.tcid_, id_=len(self.steps_) + 1,
                    expected_=expected, action_=action, summary_=summary,
                    enabled=enabled, thumbnail=thumbnail)
        self.steps_.append(stp_)
        return stp_

    def getStats(self):
        """
        Return all statistics

        @return:
        @rtype: tuple
        """
        nb_pass = 0
        nb_fail = 0
        nb_und = 0

        for step in self.getSteps():
            if step.getVerdict() == PASS:
                nb_pass += 1
            elif step.getVerdict() == FAIL:
                nb_fail += 1
            elif step.getVerdict() == UNDEFINED:
                nb_und += 1
        return (nb_pass, nb_fail, nb_und)

    def getDesign(self, designId, testName='', testPath='',
                  userName='', projectName=''):
        """
        Return design
        """
        ret = []
        for steps in self.getSteps():
            ret.append(u"\t%s" % steps.getDesign())
        design = self.parent.getDesignTemplate() % (
            designId,
            userName,
            projectName,
            testPath,
            testName,
            self.parent.getTestname(),
            self.parent.getRequirement(),
            self.parent.getPurpose(),
            "\n".join(ret)
        )
        return design

    def getDesignXml(self):
        """
        Return design as xml
        """
        ret = []
        ret.append(
            u'<testcase>%s</testcase>' %
            xmlescape(
                self.parent.getTestname()))
        if self.parent.getRequirement():
            ret.append(
                u'<requirement><![CDATA[%s]]></requirement>' %
                self.parent.getRequirement())
        else:
            ret.append(u'<requirement />')
        if self.parent.getPurpose():
            ret.append(
                u'<purpose><![CDATA[%s]]></purpose>' %
                self.parent.getPurpose())
        else:
            ret.append(u'<purpose />')

        ret.append(u'<steps>')
        for steps in self.getSteps():
            ret.extend(steps.getDesignXml())
        ret.append(u'</steps>')

        return ret

    def getReport(self, isUnit=False, isAbstract=False):
        """
        Return report
        """
        sep = '<br />'
        summaries = []
        actions = []
        expected = []
        actuals = []

        for stp in self.getSteps():
            summaries.append(u"%s. %s" % (stp.getId(), stp.getSummary()))
            actions.append(u"%s. %s" % (stp.getId(), stp.getAction()))
            expected.append(u"%s. %s" % (stp.getId(), stp.getExpected()))
            v = stp.getVerdict()
            if v == FAIL or v == UNDEFINED:
                actuals.append(
                    u'<font color="#FF0000">%s. %s - %s</font>' %
                    (stp.getId(), v, stp.getActual()))
            else:
                actuals.append(
                    u'<font color="#008000">%s. %s - %s</font>' %
                    (stp.getId(), v, stp.getActual()))

        final_verdict = self.parent.get_final_verdict()
        if final_verdict == PASS:
            final_verdict = u'<font color="#008000">%s</font>' % final_verdict
        else:
            final_verdict = u'<font color="#FF0000">%s</font>' % final_verdict

        report_template = unicode(self.parent.getReportTemplate())
        return report_template % (
            self.parent.getTestname(),
            final_verdict,
            self.parent.getPurpose(),
            sep.join(summaries), sep.join(actions),
            sep.join(expected), sep.join(actuals)
        )

    def getReportXml(self):
        """"
        Return report as xml
        """
        ret = []
        summaries = []
        actions = []
        expected = []
        actuals = []

        ret.append(
            u'\t<testcase><![CDATA[%s]]></testcase>' %
            self.parent.getTestname())
        ret.append(
            u'\t<verdict><![CDATA[%s]]></verdict>' %
            self.parent.get_final_verdict())
        ret.append(
            u'\t<purpose><![CDATA[%s]]></purpose>' %
            self.parent.getPurpose())

        for stp in self.getSteps():
            summaries.append(u"%s. %s" % (stp.getId(), stp.getSummary()))
            actions.append(u"%s. %s" % (stp.getId(), stp.getAction()))
            expected.append(u"%s. %s" % (stp.getId(), stp.getExpected()))
            actuals.append(
                u'%s. %s - %s' %
                (stp.getId(),
                 stp.getVerdict(),
                 stp.getActual()))
        ret.append(
            u'\t<steps-summaries><![CDATA[%s]]></steps-summaries>' %
            '\n'.join(summaries))
        ret.append(
            u'\t<steps-actions><![CDATA[%s]]></steps-actions>' %
            '\n'.join(actions))
        ret.append(
            u'\t<steps-expected><![CDATA[%s]]></steps-expected>' %
            '\n'.join(expected))
        ret.append(
            u'\t<steps-actuals><![CDATA[%s]]></steps-actuals>' %
            '\n'.join(actuals))

        return ret

    def getPreviousStep(self):
        """
        """
        if len(self.steps_) <= 1:
            return None
        return self.steps_[len(self.steps_) - 2:-1][0]


_ExecuteTest = True


def dontExecute():
    """
    Dont execute
    """
    global _ExecuteTest
    _ExecuteTest = False


_GeneratorBaseId = 0
_GeneratorBaseIdMutex = threading.RLock()


def _getNewId():
    """
    Generates a new unique ID.

    @return:
    @rtype:
    """
    global _GeneratorBaseId
    _GeneratorBaseIdMutex.acquire()
    _GeneratorBaseId += 1
    ret = _GeneratorBaseId
    _GeneratorBaseIdMutex.release()
    return ret


def wait(timeout):
    """
    Just wait during the timeout passed as argument
    Can be use on test execution

    @param timeout: in second
    @type timeout: float
    """
    try:
        timeout = float(timeout)
    except Exception:
        raise TestWaitException("ERR_TE_002: wait initialization failed, "
                                "wrong type: %s" % str(timeout))
    TLX.instance().log_testsuite_info(message='waiting for %s sec ...' %
                                      str(timeout),
                                      component=TS,
                                      fromlevel=LEVEL_TE,
                                      tolevel=LEVEL_USER)
    time.sleep(timeout)


class AdaptersManager(object):
    """
    Adapters manager
    """

    def __init__(self):
        """
        Constructor for the adapters manager
        """
        self.adps = {}
        self.adps_id = {}

    def addAdp(self, name, value):
        """
        Add adapter
        """
        self.adps[name] = value
        self.adps_id[value.getAdapterId()] = value

    def getAdps(self):
        """
        Return all adapters
        """
        return self.adps

    def getAdp(self, name):
        """
        Return one adapter
        """
        return self.adps[name]


__AdaptersManager = AdaptersManager()
__AdaptersManagerALL = AdaptersManager()


def getAdpsMgr():
    """
    Return adapters manager
    """
    global __AdaptersManager
    ret = __AdaptersManager
    return ret


def getAdpsMgrALL():
    """
    Return adapters manager
    """
    global __AdaptersManagerALL
    ret = __AdaptersManagerALL
    return ret


TESTCASE_NAME = "Testcase"


class TestCase(object):
    """
    Basic test case with steps definition support.

    @param suffix: add a suffix to the testcase name
    @type suffix: string
    """

    def __init__(self, suffix=None, testName=None):
        """
        Construct TestCase
        """
        self.__suffix__ = suffix
        self.__name = testName
        self.__id = _getNewId()
        self.__cpts = {}
        self.__stepsManager = StepManager(tcid=self.__id, parent=self)
        self.__TESTCASE_VERDICT = None
        self.__purpose = ''
        self.__requirement = ''
        self.__tpl_report = ''
        self.__tpl_design = ''
        self.__initReportTpl()
        self.__initDesignTpl()

        self.__hasSharedAdps = False
        self.__testInfo = {}
        self.start_time = 0
        self.__testMgrID = 0

        self.__errors = []
        self.__logs = []

        self.__prepared = False

        if _ExecuteTest:
            if TCI.instance() is not None:
                TCI.instance().onRequest = self.onRequest

            if int(TestSettings.get('Tests_Framework',
                                    'dispatch-events-current-tc')):
                self.__renewAdaps()
            self.initStorageData()

    def hasSharedAdapters(self):
        """
        """
        return self.__hasSharedAdps

    def getTestInfo(self):
        """
        """
        return self.__testInfo

    def getDataStoragePath(self):
        """
        Return the storage data path

        @return: storage path
        @rtype: string
        """
        pathData = TestSettings.get('Paths', 'tmp')

        # remove slash in testcase name, fix issue #7
        tc = self.getTestname()
        tc = tc.replace('/', '')
        tc = tc.replace('\\', '')
        # end of fix

        tmp_path = "%s/TC-%s-#%s/" % (pathData, tc, self.__id)
        if platform.system() == "Windows":
            return os.path.normpath("%s/" % tmp_path)
        else:
            return os.path.normpath("/%s/" % tmp_path)

    def getTestResultPath(self):
        """
        Return the test result path

        @return: storage path
        @rtype: string
        """
        return os.path.normpath("%s/" % TestSettings.get('Paths', 'result'))

    def getPreviousStep(self):
        """
        Return the previous step if exists otherwise none

        @return: step object
        @rtype: step/none
        """
        return self.__stepsManager.getPreviousStep()

    def isPrepared(self):
        """
        Return the status of the testcase preparation

        @return: true on success
        @rtype: boolean
        """
        return self.__prepared

    def initStorageData(self):
        """
        Initiallize the storage data
        """
        pathData = TestSettings.get('Paths', 'tmp')

        if os.path.exists(pathData):
            # create the testcase folder: FolderName-uniqueID

            # remove slash in testcase name, fix issue #7
            tc = self.getTestname()
            tc = tc.replace('/', '')
            tc = tc.replace('\\', '')
            # end of fix

            if platform.system() == "Windows":
                tcDirName = "%s/TC-%s-#%s/" % (pathData,
                                               tc,
                                               self.__id)
            else:
                tcDirName = "/%s/TC-%s-#%s/" % (pathData,
                                                tc,
                                                self.__id)
            tcDirName = os.path.normpath(tcDirName)

            try:
                if not os.path.exists(tcDirName):
                    os.mkdir(tcDirName, 0o755)
            except Exception as e:
                self.error("unable to init storage testcase: %s" % str(e))

    def saveFile(self, destname, data):
        """
        Storing binary data in file. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        # create the file
        try:
            f = open("%s/%s" % (self.getDataStoragePath(), destname), 'wb')
            if sys.version_info > (3,):
                f.write(data.encode())
            else:
                f.write(data)
            f.close()
        except Exception as e:
            self.error("unable to write data in testcase storage: %s" % str(e))

    def appendFile(self, destname, data):
        """
        Append binary data in file. These data are accessible in the archives.

        @param destname: destination name
        @type destname: string

        @param data: data to save
        @type data: string
        """
        # create the file
        try:
            f = open("%s/%s" % (self.getDataStoragePath(), destname), 'ab')
            if sys.version_info > (3,):
                f.write(data.encode())
            else:
                f.write(data)
            f.close()
        except Exception as e:
            self.error(
                "unable to append testcase in data storage: %s" %
                str(e))

    def __renewAdaps(self):
        """
        Renew adapters
        """
        # renew adapters
        for adpId, adp in getAdpsMgr().getAdps().items():
            adp.renewAdp(parent=self)

    def __initReportTpl(self):
        """
        Initiliaze the report template
        """
        tpl_path = "%s/report.tpl" % (TestSettings.get('Paths', 'templates'))
        try:
            fd = open(tpl_path, "r")
            tpl_report = fd.read()
            fd.close()
        except Exception as e:
            self.error('unable to read report template: %s' % str(e))
        else:
            self.__tpl_report = tpl_report

    def __initDesignTpl(self):
        """
        Initialize the design template
        """
        tpl_path = "%s/design.tpl" % (TestSettings.get('Paths', 'templates'))
        try:
            fd = open(tpl_path, "r")
            tpl_design = fd.read()
            fd.close()
        except Exception as e:
            self.error('unable to read design template: %s' % str(e))
        else:
            self.__tpl_design = tpl_design

    def __repr__(self):
        """
        repr
        """
        return TESTCASE_NAME

    def __str__(self):
        """
        str
        """
        return TESTCASE_NAME

    def __unicode__(self):
        """
        unicode
        """
        return TESTCASE_NAME

    def getDesignTemplate(self):
        """
        Return the design template
        """
        return self.__tpl_design

    def getReportTemplate(self):
        """
        Return the report template
        """
        return self.__tpl_report

    def getReportHeaderTemplate(self):
        """
        Return the report template
        """
        return self.__tpl_report_header

    def getStepsManager(self):
        """
        Return the steps manager
        """
        return self.__stepsManager

    def setPurpose(self, purpose):
        """
        Set the purpose of the testcase

        @param purpose: purpose description
        @type purpose: string
        """
        self.__purpose = purpose

    def getPurpose(self):
        """
        Return the purpose
        """
        if sys.version_info > (3,):
            return self.__purpose
        else:
            return self.__purpose.decode("utf8")

    def setRequirement(self, requirement):
        """
        Set the requirement of the testcase

        @param requirement: requirement description
        @type requirement: string
        """
        self.__requirement = requirement

    def getRequirement(self):
        """
        Return the requirement
        """
        if sys.version_info > (3,):
            return self.__requirement
        else:
            return self.__requirement.decode("utf8")

    def getSuffix(self):
        """
        Return the suffix of the testcase

        @return: testcase id
        @rtype: integer
        """
        if self.__suffix__ is not None:
            return self.__suffix__
        else:
            return ""

    def setName(self, name):
        """
        Set the name of the testcase

        @param name: testcase name
        @type name: string
        """
        self.__name = name

    def getTestname(self):
        """
        Return the testname
        """
        tname = self.__class__.__name__
        if self.__name is not None:
            tname = self.__name
        if self.__suffix__ is not None:
            tname = "%s_%s" % (tname, self.__suffix__)

        if sys.version_info > (3,):
            return tname
        else:
            return tname.decode("utf8")

    def getSteps(self):
        """
        Return all steps
        """
        return self.__stepsManager.getSteps()

    def description(self, **kwargs):
        """
        Description function
        """
        pass

    def prepare(self, **kwargs):
        """
        prepare function
        """
        pass

    def cleanup(self, aborted, **kwargs):
        """
        Cleanup the test

        @param aborted: test aborted indication
        @type aborted: boolean
        """
        pass

    def getId(self):
        """
        Return the id of the testcase

        @return: testcase id
        @rtype: integer
        """
        return self.__id

    def abort(self, err=None, stop=False):
        """
        Abort the tescase, cleanup is called automaticly
        Deprecated function

        @param err: error message
        @type err: string/none

        @param stop: force to stop the test after the abort (default=False)
        @type stop: boolean
        """
        err_msg = err
        if err is None:
            err_msg = '--'

        self.error("action aborted: %s" % err_msg)
        if stop:
            # self.warning("Terminating test...")
            raise AbortStopException(err_msg)
        else:
            # self.warning("Aborting testcase...")
            raise AbortException(err_msg)

    def saveData(self, data):
        """
        Save data in the temporary storage.
        The temp storage is share between each testcases.
        Deprecated function, please to use setCache

        @param data: data to save
        @type data: object
        """
        TDS.instance().save_data(data=data)

    def loadData(self):
        """
        Load data from the temporary storage.
        The temp storage is share between each testcases.
        Deprecated, please to use getCache

        @return: data saved or None if empty
        @rtype: string/list/dict/tuple/none
        """
        return TDS.instance().load_data()

    def setCache(self, name, data):
        """
        Deprecated function, please to use the new class Cache
        Save data in the temporary storage.
        The temp storage is share between each testcases.

        @param name: key name
        @type name: string

        @param data: data to save
        @type data: object
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {name: data}

        if not isinstance(cur, dict):
            return

        cur.update({name: data})
        TDS.instance().save_data(data=cur)

    def getCache(self, name):
        """
        Deprecated function, please to use the new class Cache
        Load data from the temporary storage according to the name passed as argument.
        The temp storage is share between each testcases.

        @param name: key name
        @type name: string

        @return: data saved or None if empty
        @rtype: object/none
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {}

        if not isinstance(cur, dict):
            return

        if name in cur:
            return cur[name]
        else:
            return None

    def delCache(self, name):
        """
        Deprecated function, please to use the new class Cache
        Delete data from the temporary storage
        according to the name passed as argument.
        The temp storage is share between each testcases.

        @param name: key name
        @type name: string

        @return: True on success, False otherwise
        @rtype: boolean
        """
        cur = TDS.instance().load_data()
        if cur is None:
            cur = {}

        if not isinstance(cur, dict):
            return
        if name in cur:
            cur.pop(name)
            # save data in cache
            TDS.instance().save_data(data=cur)
            return True
        else:
            return False

    def resetCache(self):
        """
        Deprecated function, please to use the new class Cache
        Reset data from the temporary storage.

        @return: data saved or None if empty
        @rtype: string/list/dict/tuple/none
        """
        cur = {}
        TDS.instance().save_data(data=cur)

    def resetData(self):
        """
        Deprecated function, please to use the new class Cache
        Reset data from the temporary storage.

        @return: data saved or None if empty
        @rtype: string/list/dict/tuple/none
        """
        return TDS.instance().reset_data()

    def setPassed(self):
        """
        Set the result of the testcase to passed.
        """
        self.warning("setPassed: deprecated function")

        if self.__TESTCASE_VERDICT is None:
            self.__TESTCASE_VERDICT = PASS

    def isPassed(self):
        """
        Return the result of testcase

        @return: True if the testcase is pass, False otherwise
        @rtype: boolean
        """
        if self.get_final_verdict() == PASS:
            return True
        return False

    def isFailed(self):
        """
        Return the result of testcase

        @return: True if the testcase is failed or undefined, False otherwise
        @rtype: boolean
        """
        if self.get_final_verdict() in [FAIL, UNDEFINED]:
            return True
        return False

    def setFailed(self, internal=False, internalErr=""):
        """
        Set the result of the testcase to failed.
        """
        if not internal:
            self.warning("setFailed: deprecated function")
        self.__TESTCASE_VERDICT = FAIL
        if len("%s" % str(internalErr)):
            if sys.version_info > (3,):
                self.__errors.append(str(internalErr))
            else:
                self.__errors.append(str(internalErr).decode("utf8"))

    def getErrors(self):
        """
        """
        return self.__errors

    def getLogs(self):
        """
        """
        return self.__logs

    def addStep(self, expected="", description="", summary="",
                enabled=True, thumbnail=None):
        """
        Add step to the testcase with description
        and expected result passed as arguments.

        @param expected: describe expected result
        @type expected: string

        @param description: step description
        @type description: string

        @param summary: very short description
        @type summary: string

        @param enabled: enable the step (default=True)
        @type enabled: boolean

        @param thumbnail: image (default=None)
        @type thumbnail: string/none

        @return: step object
        @rtype: Step
        """
        return self.__stepsManager.addStep(expected=expected,
                                           action=description,
                                           summary=summary,
                                           enabled=enabled,
                                           thumbnail=thumbnail)

    def get_final_verdict(self):
        """
        Return the final verdict

        @return:
        @rtype:
        """

        ret = UNDEFINED

        nb_pass, nb_fail, nb_und = self.__stepsManager.getStats()
        if nb_fail >= 1:
            ret = FAIL
        elif nb_und >= 1:
            ret = UNDEFINED
        elif nb_pass > 0 and nb_fail == 0 and nb_und == 0:
            ret = PASS
        else:
            ret = UNDEFINED

        if self.__TESTCASE_VERDICT is not None:
            ret = self.__TESTCASE_VERDICT

        return ret

    def getRegisteredComponents(self):
        """
        Return all registered components/adapters
        """
        return self.__cpts

    def shareAdapter(self, name, adapter):
        """
        Share an adapter with another test

        @param name: adapter name
        @type name: string

        @param adapter: adapter object
        @type adapter: adapter
        """
        if adapter.isShared():
            return getAdpsMgr().addAdp(name=name, value=adapter)
        else:
            self.error('Can be shared: adapter is not in shared mode')

    def getAdapter(self, name):
        """
        Return a shared adapter

        @param name: adapter name
        @type name: string

        @return: adapter objected
        @rtype: adapter
        """
        adp = getAdpsMgr().getAdp(name=name)
        return adp

    def getSharedAdapter(self, name):
        """
        Return a shared adapter

        @param name: adapter name
        @type name: string

        @return: adapter objected
        @rtype: adapter
        """
        for adpId, adpObj in getAdpsMgr().getAdps().items():
            if adpObj.realname__ == name.upper():
                return adpObj
        return None

    def findAdapter(self, name):
        """
        Return adapter in shared mode according to the name

        @param name: adapter name
        @type name: string

        @return: adapter objected or not if not found
        @rtype: adapter
        """
        return self.getSharedAdapter(name=name)

    def registerComponent(self, component, shared=False):
        """
        Return a component/adapter
        """
        self.__cpts[component.getAdapterId()] = component
        if shared:
            if not int(TestSettings.get('Tests_Framework',
                                        'dispatch-events-current-tc')):
                self.__hasSharedAdps = True
            getAdpsMgr().addAdp(name=component.getAdapterId(),
                                value=component)

        # register all adapters and libraries
        getAdpsMgrALL().addAdp(name=component.getAdapterId(),
                               value=component)

    def dontExecuteMe(self, **kwargs):
        """
        Dont execute the test
        """
        try:
            # Register the testcase
            tsMgr = getTsMgr()
            tsMgr.addTc(tc=self)

            self.description(**kwargs)
        except Exception as e:
            sys.stderr.write('%s\\n' % str(e))

    def execute(self, **kwargs):
        """
        Execute

        @param kwargs:
        @type kwargs:
        """
        no_steps = False

        if not _ExecuteTest:
            self.dontExecuteMe(**kwargs)
        else:
            self.start_time = time.time()
            self.__testMgrID = copy.copy(getTsMgr().getId())
            try:
                name = self.getTestname()
                TLX.instance().log_testcase_started(id_=self.__id,
                                                    name=name,
                                                    fromlevel=LEVEL_TE,
                                                    tolevel=LEVEL_USER,
                                                    testInfo=self.__testInfo)

                # Register the testcase
                tsMgr = getTsMgr()
                tsMgr.addTc(tc=self)

                # new in v12.1
                if not int(TestSettings.get('Tests_Framework',
                                            'dispatch-events-current-tc')):
                    tcMgr = getTcMgr()
                    self.__testInfo = copy.copy(TLX.instance().getTestInfo())
                    tcMgr.addTc(tc=self, tcArgs=kwargs)
                # end of new

                aborted = False
                stopped = False
                self.__prepared = False
                body = getattr(self, 'definition', None)  # new in 3.2.0
                if callable(body):
                    TLX.instance().log_testcase_info('BEGIN [Id=#%s]' % self.__id,
                                                     TC,
                                                     self.__id,
                                                     color_=TLX.instance().INFO_TS,
                                                     fromlevel=LEVEL_TE,
                                                     tolevel=LEVEL_USER,
                                                     testInfo=self.__testInfo,
                                                     flagEnd=False,
                                                     flagBegin=True)
                    try:
                        # new in 6.1.0
                        TLX.instance().log_testcase_internal(message='Designing',
                                                             component=TC,
                                                             tcid=self.__id,
                                                             bold=False,
                                                             italic=True,
                                                             fromlevel=LEVEL_TE,
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testInfo)
                        self.description(**kwargs)
                        # end new in 6.1.0

                        TLX.instance().log_testcase_internal(message='Preparing',
                                                             component=TC,
                                                             tcid=self.__id,
                                                             bold=False,
                                                             italic=True,
                                                             fromlevel=LEVEL_TE,
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testInfo)
                        self.prepare(**kwargs)
                        self.__prepared = True
                        TLX.instance().log_testcase_internal(message='Starting',
                                                             component=TC,
                                                             tcid=self.__id,
                                                             bold=False,
                                                             italic=True,
                                                             fromlevel=LEVEL_TE,
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testInfo)

                        if not len(self.getSteps()):
                            no_steps = True
                            step = self.addStep(summary="initial step")
                            
                        body(**kwargs)
                                                                                     
                        if no_steps:
                            step.start()
                            step.setPassed("success")
                    except AbortException as e:
                        aborted = 'Abort reason: %s' % e
                    except AbortStopException as e:
                        aborted = 'Abort reason: %s' % e
                        stopped = 'Test stopped: %s' % e
                    except TestPropertiesLib.TestPropertiesException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestOperatorsLib.TestOperatorsException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestAdapterLib.TestAdaptersException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestAdapterLib.TestTimerException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestAdapterLib.TestStateException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestTemplatesLib.TestTemplatesException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except StepException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except BreakpointException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestWaitException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TimeException as e:
                        aborted = True
                        self.error(e, raw=True)
                        self.setFailed(internal=True)
                    except TestAdapterLib.ValueException as e:
                        aborted = True
                        self.error('ERR_ADP_100: %s' % e, raw=True)
                        self.setFailed(internal=True)
                    except TestAdapterLib.AdapterException as e:
                        aborted = True
                        self.error('ERR_ADP_200: %s' % e, raw=True)
                        self.setFailed(internal=True)
                    except Exception as e:
                        aborted = True
                        self.error('ERR_TE_001: %s' % e)
                        self.setFailed(internal=True)

                    if int(TestSettings.get('Tests_Framework',
                                            'dispatch-events-current-tc')):
                        TLX.instance().log_testcase_internal(message='Cleaning',
                                                             component=TC,
                                                             tcid=self.__id,
                                                             bold=False,
                                                             italic=True,
                                                             fromlevel=LEVEL_TE,
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testInfo)
                        try:
                            # cleanup done in the test
                            self.cleanup(aborted, **kwargs)
                        except Exception as e:
                            self.setFailed(internal=True, internalErr=str(e))
                            TLX.instance().log_testcase_error(str(e),
                                                              TC,
                                                              self.__id,
                                                              fromlevel=LEVEL_TE,
                                                              tolevel=LEVEL_USER,
                                                              testInfo=self.__testInfo)
                        self.__cleanup()  # internal cleanup
                        TLX.instance().log_testcase_info('END',
                                                         TC,
                                                         self.__id,
                                                         color_=TLX.instance().INFO_TS,
                                                         fromlevel=LEVEL_TE,
                                                         tolevel=LEVEL_USER,
                                                         testInfo=self.__testInfo,
                                                         flagEnd=True,
                                                         flagBegin=False)
                    else:
                        if not self.__hasSharedAdps:
                            TLX.instance().log_testcase_internal(message='Cleaning',
                                                                 component=TC,
                                                                 tcid=self.__id,
                                                                 bold=False,
                                                                 italic=True,
                                                                 fromlevel=LEVEL_TE,
                                                                 tolevel=LEVEL_USER,
                                                                 testInfo=self.__testInfo)
                            try:
                                # cleanup done in the test
                                self.cleanup(aborted, **kwargs)
                            except Exception as e:
                                self.setFailed(
                                    internal=True, internalErr=str(e))
                                TLX.instance().log_testcase_error(str(e),
                                                                  TC,
                                                                  self.__id,
                                                                  fromlevel=LEVEL_TE,
                                                                  tolevel=LEVEL_USER,
                                                                  testInfo=self.__testInfo)
                            self.__cleanup()  # internal cleanup
                            TLX.instance().log_testcase_info('END',
                                                             TC,
                                                             self.__id,
                                                             color_=TLX.instance().INFO_TS,
                                                             fromlevel=LEVEL_TE,
                                                             tolevel=LEVEL_USER,
                                                             testInfo=self.__testInfo,
                                                             flagEnd=True,
                                                             flagBegin=False)
                else:
                    self.error('test definition is missing')

                if int(TestSettings.get('Tests_Framework',
                                        'dispatch-events-current-tc')):
                    stop_time = time.time()
                    duration = stop_time - self.start_time
                    TLX.instance().log_testcase_stopped(id_=self.__id,
                                                        result=self.get_final_verdict(),
                                                        duration=duration,
                                                        prjId=tsMgr.getProjectID(),
                                                        fromlevel=LEVEL_TE, tolevel=LEVEL_USER,
                                                        testInfo=self.__testInfo)

                else:
                    if not self.__hasSharedAdps:
                        stop_time = time.time()
                        duration = stop_time - self.start_time
                        TLX.instance().log_testcase_stopped(id_=self.__id,
                                                            result=self.get_final_verdict(),
                                                            duration=duration,
                                                            prjId=tsMgr.getProjectID(),
                                                            fromlevel=LEVEL_TE, tolevel=LEVEL_USER,
                                                            testInfo=self.__testInfo)

            except Exception as e:
                self.setFailed(internal=True, internalErr=str(e))
                TLX.instance().log_testcase_error(str(e),
                                                  TC,
                                                  self.__id,
                                                  fromlevel=LEVEL_TE,
                                                  tolevel=LEVEL_USER,
                                                  testInfo=self.__testInfo)
                self.__cleanup()
                stop_time = time.time()
                duration = stop_time - self.start_time
                TLX.instance().log_testcase_stopped(id_=self.__id,
                                                    result=self.get_final_verdict(),
                                                    duration=duration,
                                                    prjId=tsMgr.getProjectID(),
                                                    fromlevel=LEVEL_TE,
                                                    tolevel=LEVEL_USER,
                                                    testInfo=self.__testInfo)

            if stopped:
                raise ForceStopException(stopped)

    def __cleanup(self):
        """
        On cleanup, internal function
        """
        for adpId, adp in self.__cpts.items():
            if not adp.isShared():
                try:
                    adp.onTimerReset()
                except Exception as e:
                    TLX.instance().log_testcase_error("timer reset: %s" % str(e),
                                                      TC,
                                                      self.__id,
                                                      fromlevel=LEVEL_TE,
                                                      tolevel=LEVEL_USER,
                                                      testInfo=self.__testInfo)
                try:
                    adp.onReset()
                except Exception as e:
                    TLX.instance().log_testcase_error(str(e),
                                                      TC,
                                                      self.__id,
                                                      fromlevel=LEVEL_TE,
                                                      tolevel=LEVEL_USER,
                                                      testInfo=self.__testInfo)
                try:
                    adp.stop()
                    adp.join()
                except Exception:
                    pass

    def endingDelayed(self, **kwargs):
        """
        """
        aborted = False
        tsMgr = getTsMgr()
        try:
            TLX.instance().log_testcase_internal(message='Cleaning',
                                                 component=TC,
                                                 tcid=self.__id,
                                                 bold=False,
                                                 italic=True,
                                                 fromlevel=LEVEL_TE,
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__testInfo)
            try:
                self.cleanup(aborted, **kwargs)  # cleanup done in the test
            except Exception as e:
                self.setFailed(internal=True)
                TLX.instance().log_testcase_error(str(e),
                                                  TC,
                                                  self.__id,
                                                  fromlevel=LEVEL_TE,
                                                  tolevel=LEVEL_USER,
                                                  testInfo=self.__testInfo)
            TLX.instance().log_testcase_info('END',
                                             TC,
                                             self.__id,
                                             color_=TLX.instance().INFO_TS,
                                             fromlevel=LEVEL_TE,
                                             tolevel=LEVEL_USER,
                                             testInfo=self.__testInfo,
                                             flagEnd=True,
                                             flagBegin=False)

            stop_time = time.time()
            duration = stop_time - self.start_time
            TLX.instance().log_testcase_stopped(id_=self.__id,
                                                result=self.get_final_verdict(),
                                                duration=duration,
                                                prjId=tsMgr.getProjectID(),
                                                fromlevel=LEVEL_TE,
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testInfo)

        except Exception as e:
            TLX.instance().log_testcase_error(str(e),
                                              TC,
                                              self.__id,
                                              fromlevel=LEVEL_TE,
                                              tolevel=LEVEL_USER,
                                              testInfo=self.__testInfo)
            stop_time = time.time()
            duration = stop_time - self.start_time
            TLX.instance().log_testcase_stopped(id_=self.__id,
                                                result=self.get_final_verdict(),
                                                duration=duration,
                                                prjId=tsMgr.getProjectID(),
                                                fromlevel=LEVEL_TE,
                                                tolevel=LEVEL_USER,
                                                testInfo=self.__testInfo)

    def wait(self, timeout):
        """
        Just wait during the timeout passed as argument

        @param timeout: in second
        @type timeout: float
        """
        if not _ExecuteTest:
            return

        try:
            timeout = float(timeout)
        except Exception:
            raise TestWaitException("ERR_TE_003: wait initialization "
                                    "failed, wrong type: %s" % str(timeout))
        if timeout < 0:
            raise TestWaitException("ERR_TE_003: wait can be "
                                    "negative: %s" % str(timeout))

        self.__logs.append('waiting for %s sec ...' % str(timeout))
        TLX.instance().log_testcase_info(message='waiting for %s sec ...' % str(timeout),
                                         component=TC,
                                         tcid=self.__id,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER,
                                         testInfo=self.__testInfo)
        time.sleep(timeout)

    def sleep(self, timeout, localshift=False):
        """
        """
        # global _TimeShift

        if not _ExecuteTest:
            return

        try:
            timeout = int(timeout)
        except Exception:
            raise TestWaitException("ERR_TE_003: sleep initialization "
                                    "failed, wrong type: %s" % str(timeout))
        if timeout < 0:
            raise TestWaitException("ERR_TE_003: sleep can be "
                                    "negative: %s" % str(timeout))

        TLX.instance().log_testcase_info(message='sleeping for %s sec ...' % str(timeout),
                                         component=TC,
                                         tcid=self.__id,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER,
                                         testInfo=self.__testInfo)

        timeref = time.time()
        while True:
            time.sleep(0.1)
            if (time.time() - timeref) >= timeout:
                break

    def sleepUntil(self, dt="1970-01-01 00:00:00",
                   fmt="%Y-%m-%d %H:%M:%S", localshift=False, delta=0):
        """
        """
        # global _TimeShift

        if not _ExecuteTest:
            return

        # get delta
        d = datetime.datetime.strptime(dt, fmt)

        r = (d - datetime.datetime.now())
        timeout = r.seconds + (r.days * 86400) + delta

        if timeout < 0:
            raise TestWaitException("ERR_TE_003: sleep until can "
                                    "be negative: %s" % str(timeout))

        TLX.instance().log_testcase_info(message='sleeping until %s ...' % dt,
                                         component=TC,
                                         tcid=self.__id,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER,
                                         testInfo=self.__testInfo)

        timeref = time.time()
        while True:
            time.sleep(0.1)
            if (time.time() - timeref) >= timeout:
                break

    def waitUntil(self, dt="1970-01-01 00:00:00",
                  fmt="%Y-%m-%d %H:%M:%S", delta=0):
        """
        Just wait until the date and time passed in argument

        @param dt: date and time (default=1970-01-01 00:00:00)
        @type dt: string

        @param fmt: date and time format (default=%Y-%m-%d %H:%M:%S)
        @type fmt: string

        @param delta: shift the date in seconds (default=0s)
        @type delta: integer
        """
        if not _ExecuteTest:
            return

        # get delta
        d = datetime.datetime.strptime(dt, fmt)

        r = (d - datetime.datetime.now())
        timeout = r.seconds + (r.days * 86400) + delta

        if timeout < 0:
            raise TestWaitException("ERR_TE_003: wait until can be "
                                    "negative: %s" % str(timeout))

        TLX.instance().log_testcase_info(message='waiting until %s ...' % dt,
                                         component=TC,
                                         tcid=self.__id,
                                         fromlevel=LEVEL_TE,
                                         tolevel=LEVEL_USER,
                                         testInfo=self.__testInfo)
        time.sleep(timeout)

    def info(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an information message associated to the testcase
        Nothing is displayed if txt=None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        if not _ExecuteTest:
            return

        typeMsg = ''
        if txt:
            if sys.version_info > (3,):
                self.__logs.append(str(txt))
            else:  # for old python
                try:
                    self.__logs.append(str(txt).decode("utf8"))
                except Exception:
                    self.__logs.append(
                        str(txt).decode("utf8", errors="replace"))

            if raw:
                typeMsg = 'raw'
            try:
                TLX.instance().log_testcase_info(message=txt,
                                                 component=TC,
                                                 tcid=self.__id,
                                                 bold=bold,
                                                 italic=italic,
                                                 multiline=multiline,
                                                 typeMsg=typeMsg,
                                                 fromlevel=LEVEL_TE,
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__testInfo)
            except UnicodeEncodeError:
                TLX.instance().log_testcase_info(message=txt.encode('utf8'),
                                                 component=TC,
                                                 tcid=self.__id,
                                                 bold=bold,
                                                 italic=italic,
                                                 multiline=multiline,
                                                 typeMsg=typeMsg,
                                                 fromlevel=LEVEL_TE,
                                                 tolevel=LEVEL_USER,
                                                 testInfo=self.__testInfo)

    def error(self, txt, bold=False, italic=False, multiline=False, raw=False):
        """
        Display an error message associated to the testcase
        Nothing is displayed if txt=None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        if not _ExecuteTest:
            return

        typeMsg = ''
        if txt:
            self.setFailed(internal=True, internalErr=txt)
            if raw:
                typeMsg = 'raw'
            try:
                TLX.instance().log_testcase_error(message=txt, component=TC,
                                                  tcid=self.__id, bold=bold,
                                                  italic=italic, multiline=multiline,
                                                  typeMsg=typeMsg, fromlevel=LEVEL_TE,
                                                  tolevel=LEVEL_USER,
                                                  testInfo=self.__testInfo)
            except UnicodeEncodeError:
                TLX.instance().log_testcase_error(message=txt.encode('utf8'),
                                                  component=TC, tcid=self.__id, bold=bold,
                                                  italic=italic, multiline=multiline,
                                                  typeMsg=typeMsg, fromlevel=LEVEL_TE,
                                                  tolevel=LEVEL_USER,
                                                  testInfo=self.__testInfo)

    def warning(self, txt, bold=False, italic=False,
                multiline=False, raw=False):
        """
        Display an warning message associated to the testcase
        Nothing is displayed if txt=None

        @param txt: text message
        @type txt: string

        @param bold: text is rendered as bold (default=False)
        @type bold: boolean

        @param italic: text is rendered as italic (default=False)
        @type italic: boolean

        @param raw: text is rendered as raw data, html otherwise (default=False)
        @type raw: boolean
        """
        if not _ExecuteTest:
            return

        typeMsg = ''
        if txt:
            if sys.version_info > (3,):
                self.__logs.append(str(txt))
            else:  # for old python
                self.__logs.append(str(txt).decode("utf8"))

            if raw:
                typeMsg = 'raw'
            try:
                TLX.instance().log_testcase_warning(message=txt, component=TC,
                                                    tcid=self.__id,
                                                    bold=bold, italic=italic,
                                                    multiline=multiline,
                                                    typeMsg=typeMsg,
                                                    fromlevel=LEVEL_TE,
                                                    tolevel=LEVEL_USER,
                                                    testInfo=self.__testInfo)
            except UnicodeEncodeError:
                TLX.instance().log_testcase_warning(message=txt.encode('utf8'),
                                                    component=TC, tcid=self.__id,
                                                    bold=bold, italic=italic,
                                                    multiline=multiline, typeMsg=typeMsg,
                                                    fromlevel=LEVEL_TE,
                                                    tolevel=LEVEL_USER,
                                                    testInfo=self.__testInfo)

    def breakpoint(self, testId, timeout=86400.0):
        """
        Breakpoint on the test
        """
        if not _ExecuteTest:
            return

        cmd_data = {'cmd': Messages.CMD_INTERACT, 'breakpoint': True,
                    'test-id': testId, 'timeout': timeout}
        cmd_data.update(TLX.instance().getTestInfo())

        rsp = TCI.instance().cmd(data=cmd_data, timeout=timeout)
        if rsp is None:
            return None
        else:
            if rsp['code'] == Messages.RSP_CODE_OK[0]:
                if rsp['body']['cmd'] == Messages.CMD_INTERACT:
                    return rsp['body']['rsp']
                else:
                    self.error('Breakpoint error')
                    return None
            else:
                self.error('System break error')
                return None

    def pause(self, testId, stepId, stepSummary, timeout=86400.0):
        """
        Pause the test
        """
        if not _ExecuteTest:
            return

        cmd_data = {'cmd': Messages.CMD_INTERACT,
                    'pause': True,
                    'step-id': str(stepId),
                    'step-summary': stepSummary,
                    'test-id': testId,
                    'timeout': timeout}
        cmd_data.update(TLX.instance().getTestInfo())

        rsp = TCI.instance().cmd(data=cmd_data, timeout=timeout)
        if rsp is None:
            return None
        else:
            if rsp['code'] == Messages.RSP_CODE_OK[0]:
                if rsp['body']['cmd'] == Messages.CMD_INTERACT:
                    return rsp['body']['rsp']
                else:
                    self.error('Pause error')
                    return None
            else:
                self.error('System pause error')
                return None

    def interact(self, ask, timeout=30.0, default=None):
        """
        Ask a value to the tester during the execution of a test

        @param ask: ask what
        @type ask: string

        @param default: default value
        @type default: string/none

        @param timeout: max time to respond (default=30s)
        @type timeout: float

        @return: user response
        @rtype: string
        """
        if not _ExecuteTest:
            return
        self.warning('Interaction (max %s sec.): %s ' % (timeout, ask))
        cmd_data = {'cmd': Messages.CMD_INTERACT, 'ask': ask, 'timeout': timeout,
                    'test-id': getTsMgr().getTestId()}
        if default is not None:
            cmd_data.update({'default': default})
        cmd_data.update(TLX.instance().getTestInfo())

        rsp = TCI.instance().cmd(data=cmd_data, timeout=timeout)
        if rsp is None and default is not None:
            return default
        elif rsp is None:
            self.warning('Interaction timeout: no response from user')
            return None
        else:
            if rsp['code'] == Messages.RSP_CODE_OK[0]:
                if rsp['body']['cmd'] == Messages.CMD_INTERACT:
                    if rsp['body']['rsp'] is None:
                        self.warning(
                            'Interaction timeout: no response from user')
                        return None
                    else:
                        if sys.version_info > (3,):
                            return rsp['body']['rsp']
                        else:
                            return rsp['body']['rsp'].encode('utf8')
                else:
                    self.error('Interaction error')
                    return None
            else:
                self.error('System Interaction error')
                return None

    def sendNotifyToAgent(self, adapterId, agentName, agentData):
        """
        Send notify event with data to the agent passed on argument
        """
        if not _ExecuteTest:
            return
        cmd_data = {'event': "agent-notify",
                    'destination-agent': agentName,
                    'source-adapter': str(adapterId),
                    'data': agentData,
                    'result-path': getTsMgr().getRelativeTestResult(),
                    'testcase-name': self.getTestname()}
        cmd_data.update(TLX.instance().getTestInfo())
        TCI.instance().notify(data=cmd_data)

    def sendReadyToAgent(self, adapterId, agentName, agentData):
        """
        Send ready event with data to the agent passed on argument
        """
        if not _ExecuteTest:
            return
        cmd_data = {'event': "agent-ready",
                    'destination-agent': agentName,
                    'source-adapter': str(adapterId),
                    'data': agentData}
        cmd_data.update(TLX.instance().getTestInfo())
        TCI.instance().notify(data=cmd_data)

    def sendInitToAgent(self, adapterId, agentName, agentData):
        """
        Send init event with data to the agent passed on argument
        """
        if not _ExecuteTest:
            return
        cmd_data = {'event': "agent-init",
                    'destination-agent': agentName,
                    'source-adapter': str(adapterId),
                    'data': agentData}
        cmd_data.update(TLX.instance().getTestInfo())
        TCI.instance().notify(data=cmd_data)

    def sendResetToAgent(self, adapterId, agentName, agentData):
        """
        Send reset event with data to the agent passed on argument
        """
        if not _ExecuteTest:
            return
        cmd_data = {'event': "agent-reset",
                    'destination-agent': agentName,
                    'source-adapter': str(adapterId),
                    'data': agentData}
        cmd_data.update(TLX.instance().getTestInfo())
        TCI.instance().notify(data=cmd_data)

    def sendAliveToAgent(self, adapterId, agentName, agentData):
        """
        Send reset event with data to the agent passed on argument
        """
        if not _ExecuteTest:
            return
        cmd_data = {'event': "agent-alive",
                    'destination-agent': agentName,
                    'source-adapter': str(adapterId),
                    'data': agentData}
        cmd_data.update(TLX.instance().getTestInfo())
        TCI.instance().notify(data=cmd_data)

    def onRequest(self, client, tid, request):
        """
        Called from TCI
        """

        try:
            if not _ExecuteTest:
                return
            __body__ = request['body']
            if request['cmd'] == Messages.RSQ_NOTIFY:

                # checking task and test id of the notify
                if __body__['uuid'] == TLX.instance().testUuid:

                    if int(TestSettings.get('Tests_Framework',
                                            'dispatch-events-current-tc')):
                        # checking the adapter id and dispatch it
                        if int(__body__['source-adapter']) in self.__cpts:
                            if __body__['event'] == "agent-data":
                                self.__cpts[int(
                                    __body__['source-adapter'])].receivedDataFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-notify":
                                self.__cpts[int(
                                    __body__['source-adapter'])].receivedNotifyFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-error":
                                self.__cpts[int(
                                    __body__['source-adapter'])].receivedErrorFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-system-error":
                                self.warning(
                                    "Agent '%s' is not running" %
                                    __body__['destination-agent'])
                            else:
                                sys.stderr.write(
                                    "Notify received but with an incorrect event: %s" % str(
                                        __body__['event']))
                    else:
                        if int(__body__['source-adapter']
                               ) in getAdpsMgrALL().adps_id:
                            if __body__['event'] == "agent-data":
                                getAdpsMgrALL().adps_id[int(
                                    __body__['source-adapter'])].receivedDataFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-notify":
                                getAdpsMgrALL().adps_id[int(
                                    __body__['source-adapter'])].receivedNotifyFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-error":
                                getAdpsMgrALL().adps_id[int(
                                    __body__['source-adapter'])].receivedErrorFromAgent(data=__body__['data'])
                            elif __body__['event'] == "agent-system-error":
                                self.warning(
                                    "Agent '%s' is not running" %
                                    __body__['destination-agent'])
                            else:
                                sys.stderr.write(
                                    "Notify (2) received but with an incorrect event: %s" % str(
                                        __body__['event']))

                else:
                    sys.stderr.write("Notify received but not for me")
            else:
                sys.stderr.write("Request received but not for me")
        except Exception as e:
            self.error("request error: %s" % e)

    def virtualRun(self):
        """
        todo
        """
        return not _ExecuteTest

Action = TestCase