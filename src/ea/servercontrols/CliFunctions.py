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

import sys
import os
import signal
import subprocess
from binascii import hexlify
import base64
import sqlite3
import platform
import shutil
try:
    import cStringIO
except ImportError:  # support python 3
    import io as cStringIO
try:
    import cPickle
except ImportError:  # support python 3
    import pickle as cPickle
from pathlib import Path
import yaml

from ea.libs import Settings, Logger
from ea.libs.FileModels import TestResult as TestResult
from ea.serverrepositories import (RepoAdapters, RepoTests)

from ea.libs.FileModels import TestSuite as TestSuite
from ea.libs.FileModels import TestUnit as TestUnit
from ea.libs.FileModels import TestPlan as TestPlan

Settings.initialize()


def querySQL(query, db):
    """
    """
    try:
        conn = sqlite3.connect(db)

        c = conn.cursor()
        c.execute(query)
        
        rows = []
        for row in c.fetchall():
            fields = map(lambda x: x[0], c.description)
            rows.append(dict(zip(fields, row)))

        c.close()

        conn.commit()
        conn.close()
    except Exception as e:
        print("[query] %s - %s" % (str(e), query))
        sys.exit(1)
    return rows

db_name = "%s/%s/%s" % (Settings.getDirExec(),
                        Settings.get('Paths', 'var'),
                        Settings.get('Database', 'db'))


def error(msg):
    """
    """
    print("ERROR: %s" % msg)


def str_presenter(dumper, data):
  if isinstance(data, str) and "\n" in data:
    return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
  return dumper.represent_scalar('tag:yaml.org,2002:str', data)

yaml.add_representer(str, str_presenter)

def align_up(x, n):
    return ((x+n-1)//n)*n
    
def reformat_str(s, tab_size=4):
    pos = 0
    res = ''
    for c in s:
        if c=='\t':
            aligned = align_up(pos, tab_size)
            if pos%4!=0:
                num_spaces = aligned - pos
            else:
                num_spaces = tab_size
            co = ' ' * num_spaces
            pos += num_spaces
        else:
            co = c
            pos += 1
        res = res + co
    return res
    
class CliFunctions(Logger.ClassLogger):
    """
    """

    def __init__(self, parent):
        """
        """
        self.parent = parent

    def version(self):
        """
        Get version of the server
        """
        sys.stdout.write("Server version: %s\n" % Settings.getVersion())

    def installAdapter(self, name):
        """
        """
        RepoAdapters.initialize(context=None)

        folder_lib = "%s/%s/%s" % (Settings.getDirExec(),
                                   Settings.get(
            'Paths', 'packages-sutadapters'),
            name)
        folder_lib = os.path.normpath(folder_lib)
        if os.path.exists(folder_lib):
            try:

                # install dependancies according to the plugin with pip
                pip_list = "%s/deps/pip_list.txt" % folder_lib
                pip_list = os.path.normpath(pip_list)
                if os.path.exists(pip_list) and os.path.getsize(pip_list) > 0:
                    if platform.system() == "Windows":
                        cmd = "%s -m pip install -r \"%s\"" % (Settings.get('Bin', 'python-win'),
                                                               pip_list)
                    else:
                        cmd = "%s -m pip install -r %s" % (Settings.get('Bin', 'python'),
                                                           pip_list)
                    subprocess.call(cmd, shell=True)

                # system detect
                yum_list = "%s/deps/yum_list.txt" % folder_lib
                yum_list = os.path.normpath(yum_list)
                if os.path.exists(yum_list) and os.path.getsize(yum_list) > 0:
                    if os.path.exists("/etc/os-release"):
                        os_id = ""
                        with open("/etc/os-release") as f:
                            for line in f:
                                if "=" in line:
                                    k, v = line.rstrip().split("=")
                                    if k == "ID":
                                        os_id = v.strip('"')
                                        break

                        if "centos" in os_id or "rhel" in os_id:
                            cmd = "yum -y install `cat %s | tr '\n' ' '`" % yum_list
                            subprocess.call(cmd, shell=True)

                RepoAdapters.instance().updateMainInit()

                # install samples according to the plugin
                if os.path.exists("%s/samples/" % folder_lib):
                    folder_sample = "%s/%s/1/Samples/Adapter_%s" % (Settings.getDirExec(),
                                                                    Settings.get(
                                                                        'Paths', 'tests'),
                                                                    name)
                    shutil.copytree("%s/samples/" % folder_lib, folder_sample)

                print("Sut Adapter installation process terminated")
            except Exception as e:
                print("unable to install adapter: %s" % e)

        else:
            print("Sut Adapter (%s) not found!" % name)

        RepoAdapters.instance().updateMainInit()

    def decodeTrx(self, filename):
        """
        Decode a test result
        """
        doc = TestResult.DataModel()
        doc.error = error

        print("Reading the testresult...")
        res = doc.load(absPath=filename)
        if res:
            self.decodeTrxStats(tr=doc)

    def decodeTrxStats(self, tr):
        """
        """
        statisticsEvents = {'nb-total': 0,
                            'nb-info': 0,
                            'nb-error': 0,
                            'nb-warning': 0,
                            'nb-debug': 0,
                            'nb-timer': 0,
                            'nb-step': 0,
                            'nb-adapter': 0,
                            'nb-match': 0,
                            'nb-section': 0,
                            'nb-others': 0,
                            'nb-step-failed': 0,
                            'nb-step-passed': 0}
        errorsEvents = []
        try:
            f = cStringIO.StringIO(tr.testresult)
        except Exception:
            print("unable to read test result..")
        else:
            all = f.readlines()
            try:
                for line in all:
                    statisticsEvents["nb-total"] += 1

                    line_decoded = base64.b64decode(line)
                    event = cPickle.loads(line_decoded)

                    if "level" in event:
                        if event["level"] == "info":
                            statisticsEvents["nb-info"] += 1
                        if event["level"] == "warning":
                            statisticsEvents["nb-warning"] += 1
                        if event["level"] == "error":
                            statisticsEvents["nb-error"] += 1
                            errorsEvents.append(event)
                        if event["level"] == "debug":
                            statisticsEvents["nb-debug"] += 1

                        if event["level"] in ["send", "received"]:
                            statisticsEvents["nb-adapter"] += 1
                        if event["level"].startswith("step"):
                            statisticsEvents["nb-step"] += 1
                        if event["level"].startswith("timer"):
                            statisticsEvents["nb-timer"] += 1
                        if event["level"].startswith("match"):
                            statisticsEvents["nb-match"] += 1
                        if event["level"] == "section":
                            statisticsEvents["nb-section"] += 1
                    else:
                        statisticsEvents["nb-others"] += 1

            except Exception as e:
                print("unable to unpickle: %s" % e)
            else:
                self.displayTrxStats(statisticsEvents)
                self.displayTrxErrors(errorsEvents)

    def displayTrxErrors(self, errors):
        """
        """
        print("errors listing (%s):" % len(errors))
        for err in errors:
            print("\t%s - %s" % (err['timestamp'], err['short-msg']))

    def displayTrxStats(self, stats):
        """
        """

        nbDebugPercent = 0
        nbInfoPercent = 0
        nbWarningPercent = 0
        nbErrorPercent = 0
        if stats["nb-total"]:
            nbDebugPercent = (stats["nb-debug"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbInfoPercent = (stats["nb-info"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbWarningPercent = (stats["nb-warning"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbErrorPercent = (stats["nb-error"] * 100) / stats["nb-total"]

        nbAdapterPercent = 0
        nbTimerPercent = 0
        nbStepPercent = 0
        nbMatchPercent = 0
        if stats["nb-total"]:
            nbAdapterPercent = (stats["nb-adapter"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbTimerPercent = (stats["nb-timer"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbStepPercent = (stats["nb-step"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbMatchPercent = (stats["nb-match"] * 100) / stats["nb-total"]

        nbSectionPercent = 0
        nbOthersPercent = 0
        if stats["nb-total"]:
            nbSectionPercent = (stats["nb-section"] * 100) / stats["nb-total"]
        if stats["nb-total"]:
            nbOthersPercent = (stats["nb-others"] * 100) / stats["nb-total"]

        print("statistics:")
        print("\ttotal events:\t\t%s\t\t(100%%)" % stats["nb-total"])
        print("")
        print("\tdebug events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-debug"], nbDebugPercent))
        print("\tinfo events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-info"], nbInfoPercent))
        print("\twarning events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-warning"], nbWarningPercent))
        print("\terror events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-error"], nbErrorPercent))
        print("")
        print("\tadapter events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-adapter"], nbAdapterPercent))
        print("\ttimer events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-timer"], nbTimerPercent))
        print("\tstep events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-step"], nbStepPercent))
        print("\tmatch events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-match"], nbMatchPercent))
        print("")
        print("\tsection events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-section"], nbSectionPercent))
        print("\tothers events:\t\t%s\t\t(%.2f%%)" %
              (stats["nb-others"], nbOthersPercent))
        print("")

    def generateKey(self, username, size=20):
        """
        Generate a key for the rest api
        """
        apikey_id = username
        apikey_secret = hexlify(os.urandom(size))
        if sys.version_info > (3,):
            apikey_secret = apikey_secret.decode("utf8")

        querySQL(query="UPDATE `users` SET apikey_id=\"%s\", apikey_secret=\"%s\" WHERE login=\"%s\"" % (username,
                                                                                                         apikey_secret,
                                                                                                         username), db=db_name)

        print("API Key ID: %s" % apikey_id)
        print("API Key Secret: %s" % apikey_secret)
        
        print("...")
        self.reload()
        
    def getSecret(self, username, size=20):
        """
        Get secret for the rest api
        """
        apikey_id = username
        apikey_secret = hexlify(os.urandom(size))
        if sys.version_info > (3,):
            apikey_secret = apikey_secret.decode("utf8")

        sql_query = "SELECT apikey_id, apikey_secret from users WHERE login=\"%s\"" % (username)
        rows = querySQL(query=sql_query, db=db_name)
        
        if len(rows):
            print("API key: %s" % rows[0]["apikey_id"])
            print("API secret: %s" % rows[0]["apikey_secret"])
        else:
            print("error: user not found")
            
    def reload(self):
        """
        Reload configuration
        Send a signal to the process
        """
        sys.stdout.write("Reloading configuration...\n")
        if not self.parent.status():
            sys.stdout.write("Server not started...\n")
        else:
            pid = self.parent.getPid()
            if pid is not None:
                self.parent.sendSignal(pid, signal.SIGHUP)
                sys.stdout.write("Configuration reloaded!\n")

                RepoAdapters.initialize(context=None)
                RepoAdapters.instance().updateMainInit()
                sys.stdout.write("Adapters reloaded!\n")

        sys.stdout.flush()

    def show_data_storage(self):
        """show data storage path"""
        storage = "%s%s" % (Settings.getDirExec(),
                             Settings.get('Paths', 'var'))
                                        
        sys.stdout.write("%s\n" % storage)
        
    def convert2yaml(self):
        """convert test files to yaml"""
        RepoTests.initialize(context=None)

        for root,d_names,f_names in os.walk(RepoTests.instance().testsPath):
            for f in f_names:
                pth = os.path.join(root, f)
                file_name, file_ext = os.path.splitext( Path(pth).name )
    
                if file_ext.lower() == ".tgx":
                    doc = TestPlan.DataModel()
                    res = doc.load(pth)   
                    if res:
                        f = {"properties": {"descriptions": {}, "parameters": []}}
                        for d in doc.properties["properties"]["descriptions"]["description"]:
                            if d["key"] in [ "author", "summary", "name", "requirement"] :
                                f["properties"]["descriptions"][d["key"]] = d["value"]
                        for p in doc.properties["properties"]["inputs-parameters"]["parameter"]:
                            f["properties"]["parameters"].append({
                                "description": p["description"],
                                "name": p["name"],
                                "scope": p["scope"],
                                "type": p["type"],
                                "value": p["value"]
                            })
                        f["testglobal"] = []  
                        for tf in doc.testplan['testplan']['testfile']:
                            tf_dict =    {
                                    "alias": tf["alias"],
                                    "description": tf["description"],
                                    "file": tf["file"],
                                    "id": tf["id"],
                                    "parent": tf["parent"],
                                    "parameters": []
                                }
                            for p in tf["properties"]["inputs-parameters"]["parameter"]:
                                tf_dict["parameters"].append({
                                    "description": p["description"],
                                    "name": p["name"],
                                    "scope": p["scope"],
                                    "type": p["type"],
                                    "value": p["value"]
                                })
                            f["testglobal"].append(tf_dict)
                        
                        doc_yaml = yaml.dump(f, allow_unicode=True)
                        with open(os.path.join(root, "%s.yml" % file_name), "w") as f:
                            f.write(doc_yaml)
                            print("testglobal file %s converted" % file_name )
                        
                if file_ext.lower() == ".tpx":
                    doc = TestPlan.DataModel()
                    res = doc.load(pth)   
                    if res:
                        f = {"properties": {"descriptions": {}, "parameters": []}}
                        for d in doc.properties["properties"]["descriptions"]["description"]:
                            if d["key"] in [ "author", "summary", "name", "requirement"] :
                                f["properties"]["descriptions"][d["key"]] = d["value"]
                        for p in doc.properties["properties"]["inputs-parameters"]["parameter"]:
                            f["properties"]["parameters"].append({
                                "description": p["description"],
                                "name": p["name"],
                                "scope": p["scope"],
                                "type": p["type"],
                                "value": p["value"]
                            })
                        f["testplan"] = []  
                        for tf in doc.testplan['testplan']['testfile']:
                            tf_dict =    {
                                    "alias": tf["alias"],
                                    "description": tf["description"],
                                    "file": tf["file"],
                                    "id": tf["id"],
                                    "parent": tf["parent"],
                                    "parent-condition": "0",
                                    "parameters": []
                                }
                            if tf["parent-condition"] == "1":
                                tf["parent-condition"] = "failure"
                            for p in tf["properties"]["inputs-parameters"]["parameter"]:
                                tf_dict["parameters"].append({
                                    "description": p["description"],
                                    "name": p["name"],
                                    "scope": p["scope"],
                                    "type": p["type"],
                                    "value": p["value"]
                                })
                            f["testplan"].append(tf_dict)
                        
                        doc_yaml = yaml.dump(f, allow_unicode=True)
                        with open(os.path.join(root, "%s.yml" % file_name), "w") as f:
                            f.write(doc_yaml)
                            print("testplan file %s converted" % file_name )
                            
                if file_ext.lower() == ".tux":
                    doc = TestUnit.DataModel()
                    res = doc.load(pth)
                    if res:
                        f = {"properties": {"descriptions": {}, "parameters": []}}
                        for d in doc.properties["properties"]["descriptions"]["description"]:
                            if d["key"] in [ "author", "summary", "name", "requirement"] :
                                f["properties"]["descriptions"][d["key"]] = d["value"]
                        for p in doc.properties["properties"]["inputs-parameters"]["parameter"]:
                            f["properties"]["parameters"].append({
                                "description": p["description"],
                                "name": p["name"],
                                "scope": p["scope"],
                                "type": p["type"],
                                "value": p["value"]
                            })
                            
                        code = []
                        for line_content in doc.testdef.splitlines():
                            line_content = line_content.rstrip()
                            if '\t' in line_content:
                                line_content = reformat_str(s=line_content, tab_size=4)
                            code.append(line_content)

                        f["testunit"] =  "\n".join(code)
                        doc_yaml = yaml.dump(f, allow_unicode=True)
                        with open(os.path.join(root, "%s.yml" % file_name), "w") as f:
                            f.write(doc_yaml)
                            print("testunit file %s converted" % file_name )

                if file_ext.lower() == ".tsx":
                    doc = TestSuite.DataModel()
                    res = doc.load(pth)   
                    if res:
                        f = {"properties": {"descriptions": {}, "parameters": []}}
                        for d in doc.properties["properties"]["descriptions"]["description"]:
                            if d["key"] in [ "author", "summary", "name", "requirement"] :
                                f["properties"]["descriptions"][d["key"]] = d["value"]
                        for p in doc.properties["properties"]["inputs-parameters"]["parameter"]:
                            f["properties"]["parameters"].append({
                                "description": p["description"],
                                "name": p["name"],
                                "scope": p["scope"],
                                "type": p["type"],
                                "value": p["value"]
                            })
                            
                        code = []
                        for line_content in doc.testdef.splitlines():
                            line_content = line_content.rstrip()
                            if '\t' in line_content:
                                line_content = reformat_str(s=line_content, tab_size=4)
                            code.append(line_content)

                        code.append("")
                        
                        for line_content in doc.testexec.splitlines():
                            line_content = line_content.rstrip()
                            if '\t' in line_content:
                                line_content = reformat_str(s=line_content, tab_size=4)
                            code.append(line_content)    
                        f["testsuite"] =  "\n".join(code)
                        doc_yaml = yaml.dump(f, allow_unicode=True)

                        with open(os.path.join(root, "%s.yml" % file_name), "w") as f:
                            f.write(doc_yaml)
                            print("testsuite file %s converted" % file_name )
                            
CLI = None  # singleton


def instance():
    """
    Returns the singleton
    """
    return CLI


def initialize(parent):
    """
    Instance creation
    """
    global CLI
    CLI = CliFunctions(parent=parent)


def finalize():
    """
    Destruction of the singleton
    """
    global CLI
    if CLI:
        CLI = None
