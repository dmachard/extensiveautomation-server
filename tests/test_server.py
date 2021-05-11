#!/usr/bin/python

# -------------------------------------------------------------------
# Copyright (c) 2010-2021 Denis Machard
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
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

    def run_test_login(self):
        print("Login to API")

        # prepare the request
        payload = {"login": self.login, "password": self.password}
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

        self.run_job_schedule(file="/workflows/features/testlibrary.yml")

        print("SUCCESS")

    def run_tests_api(self):
        print("Testing REST API...")

        self.run_job_schedule(file="/workflows/features/restapi_session.yml")
        self.run_job_schedule(file="/workflows/features/restapi_users.yml")
        self.run_job_schedule(file="/workflows/features/restapi_projects.yml")
        self.run_job_schedule(file="/workflows/features/restapi_tests_files.yml")
        self.run_job_schedule(file="/workflows/features/restapi_tests_run.yml")
        self.run_job_schedule(file="/workflows/features/restapi_variables.yml")
        self.run_job_schedule(file="/workflows/features/restapi_tasks.yml")
        self.run_job_schedule(file="/workflows/features/restapi_system.yml")
        
        print("SUCCESS")

    def run_job_schedule(self, file):
        """schedule job"""
        # prepare the request
        payload = {"yaml-file": file,
                   'schedule-id': 0,
                   'schedule-at': [0,0,0,0,0,0] }
        headers = {'content-type': 'application/json',
                   'cookie': 'session_id=%s' % self.sessionid}
        url = "%s/v1/jobs?workspace=1" % self.url

        # send the request
        r = requests.post(url,
                          data=json.dumps(payload),
                          headers=headers)
        if r.status_code != 200:
            print("ERROR JOB SCHEDULE %s - %s" % (r.status_code, r.text))
            sys.exit(1)
        else:
            # decode response
            rsp = json.loads(r.text)

            self.run_result_details(testid=rsp["execution-id"])

    def run_result_details(self, testid, logs_index=0):
        payload = {"test-id": testid,
                   "project-id": 1,
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