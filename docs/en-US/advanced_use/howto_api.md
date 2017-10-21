---
name: How to use server API
---

# How to use server API

* [Purpose](howto_api#purpose)
* [Basic example with the REST API](howto_api#basic-example-with-the-rest-api)
* [Run test with personal parameters](howto_api#run-test-with-personal-parameters)

## Purpose

A REST API is available in the test server, this API enables to control the solution.
The complete details of the APi is available on the [External API](http://documentations.extensivetesting.org/docs/extensions/external_api) page.
The API is protected by a login/password so you need to create an account.

## Basic example with the REST API

1. Call the `/rest/session/login` uri to login on the server. You must provide the login and the sha1 of the password. If the authentication is successful, them you will get a `session_id` in return.
This session_id is mandatory to run the next actions.

    Request:

        POST /rest/session/login HTTP/1.1
        Host: 192.168.1.248
        Content-Type: application/json; charset=utf-8
        Content-Length: 74
        User-Agent: ExtensiveTesting

        {"login": "admin", "password": "da39a3ee5e6b4b0d3255bfef95601890afd80709"}

    Response:

        HTTP/1.1 200 OK
        Date: Wed, 14 Sep 2016 09:01:49 GMT
        Server: WSGIServer/0.1 Python/2.7.5
        Content-Type: application/json
        Set-Cookie: session_id=Mzc2Yjc0ZmFlNmQ5NGU1N2EyNzQ3ZmU2YWEyNWI2NjE1N;expires=Thu, 15-Sep-2016 09:01:49 GMT;  path=/
        Transfer-Encoding: chunked

        82
        {"message": "Logged in", "cmd": "/session/login", "expires": 86400, "session_id": "Mzc2Yjc0ZmFlNmQ5NGU1N2EyNzQ3ZmU2YWEyNWI2NjE1N"}
        0

2. Prepare your HTTP request and add the `session_id` as a cookie. If this cookie is missing then you will get authentication required message.

    Request:

        POST /rest/tests/run HTTP/1.1
        Content-Type: application/json; charset=utf-8
        Host: 192.168.1.248
        cookie: session_id=Mzc2Yjc0ZmFlNmQ5NGU1N2EyNzQ3ZmU2YWEyNWI2NjE1N
        Content-Length: 64
        User-Agent: ExtensiveTesting

        {"test-path": "Basics/Do/01_Wait.tux", "project-name": "Common"}

    Response:

        HTTP/1.1 200 OK
        Date: Wed, 14 Sep 2016 09:02:02 GMT
        Server: WSGIServer/0.1 Python/2.7.5
        Content-Type: application/json
        Transfer-Encoding: chunked

        44
        {"cmd": "/tests/run", "test-id": "5aef7d9ea5b22038348f92f582554d68"}
        0

3. Call the `/rest/session/logout` uri to logout from the server. This step is optional, but it's will be nice to run-it if you can.


    Request:

        GET /rest/session/logout HTTP/1.1
        Host: 192.168.1.248
        cookie: session_id=Mzc2Yjc0ZmFlNmQ5NGU1N2EyNzQ3ZmU2YWEyNWI2NjE1N
        Content-Length: 0
        User-Agent: ExtensiveTesting

    Response:

        HTTP/1.1 200 OK
        Date: Wed, 14 Sep 2016 09:02:23 GMT
        Server: WSGIServer/0.1 Python/2.7.5
        Content-Type: application/json
        Set-Cookie: session_id=DELETED;expires=Thu, 01 Jan 1970 00:00:00 GMT;  path=/
        Transfer-Encoding: chunked

        33
        {"message": "logged out", "cmd": "/session/logout"}
        0
        
# Run test with personal parameters

The API enables to run a test by provided the test properties. 
You can take a look to the folder `/Self Testing/REST API/006_Tests` for a complete example.

Configure properly the /rest/tests/run function and specify the test to execute with inputs and agent to use.

    json = {"test-path": input('PRJ_TEST'), "project-name": input('PRJ_NAME') }
    json["test-inputs"] = [{"name": "DURATION", "type": "int", "value": "1"}]
    json["test-agents"] = [{"name": "AGENT", "type": "dummy", "value": "hello"}]

    self.ADP_REST.sendRest(
                            uri='/rest/tests/run', 
                            host=input('DEST_IP'), 
                            json=json, method='POST', 
                            httpHeaders={'cookie':  'session_id=%s' % sessionId} 
                        )
