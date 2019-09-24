#!/usr/bin/python

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

import requests
import json
import sys
import time

class Server():
    def __init__(self):
        self.login = "admin"
        self.password = "password"
        self.url = "http://127.0.0.1:8081"
        self.sessionid = None
        self.prev_len_logs = 0

    def run_test_login(self):
        print("Login to API")

        # prepare the request
        payload = { "login": self.login, "password": self.password  }
        headers = {'content-type': 'application/json'}
        url = "%s/session/login" % self.url

        # send the request
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers)
        if r.status_code != 200:
            print("ERROR LOGIN %s - %s" % (r.status_code, r.text))
            sys.exit(1)
        else:
            # save session_id for other test
            rsp = json.loads(r.text)
            self.sessionid = rsp['session_id']

            print("SUCCESS")

    def run_tests_framework(self):
        print("Testing framework...")

        self.run_task_schedule(testpath="/Samples/Framework_Features",
                               testname="001_All_features",
                               testext="tpx")

        print("SUCCESS")

    def run_tests_api(self):
        print("Testing REST API...")

        self.run_task_schedule(testpath="/Samples/Self Testing",
                               testname="001_REST_API_Session_Auth",
                               testext="tpx")

        print("SUCCESS")

    def run_task_schedule(self, testpath, testname, testext):
        self.prev_len_logs = 0

        # prepare the request
        payload = { "test-path": testpath,
                    "test-name": testname,
                    "test-extension": testext,
                    "project-id": 1,
                    'schedule-id': 0,
                    'schedule-at': [0,0,0,0,0,0] }
        headers = {'content-type': 'application/json',
                   'cookie': 'session_id=%s' % self.sessionid}
        url = "%s/tasks/schedule" % self.url

        # send the request
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers)
        if r.status_code != 200:
            print("ERROR TASK SCHEDULE %s - %s" % (r.status_code, r.text))
            sys.exit(1)
        else:
            # decode response
            rsp = json.loads(r.text)

            self.run_result_details(testid=rsp["test-id"])

    def run_result_details(self, testid, logs_index=0):
        payload = { "test-id": testid,
                    "project-id": 1,
                    #"log-index": self.prev_len_logs,
                    "log-index": logs_index}
        headers = {'content-type': 'application/json',
                   'cookie': 'session_id=%s' % self.sessionid}
        url = "%s/results/details" % self.url
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers)
        if r.status_code != 200:
            print("ERROR RESULT DETAILS %s - %s" % (r.status_code, r.text))
            sys.exit(1)
        else:
            # decode response
            rsp = json.loads(r.text)

            #self.prev_len_logs += len_logs
            if len(rsp["test-logs"]):
                if sys.version_info < (3,):
                    print(rsp["test-logs"].encode('utf8').strip())
                else:
                    print(rsp["test-logs"].strip())

            if rsp["test-verdict"] == None:
                time.sleep(2)
                self.run_result_details(testid=testid,
                                        logs_index=rsp["test-logs-index"])
            else:
                if rsp["test-verdict"] != "pass":
                    print("ERROR ON TEST %s" % rsp["test-verdict"])
                    sys.exit(1)
EA = Server()
EA.run_test_login()
EA.run_tests_framework()
EA.run_tests_api()