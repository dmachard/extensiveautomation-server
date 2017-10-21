---
name: HTTP requests
---

# HTTP requests

## Introduction

Use generic tests is useful to reduce the maintenance of your tests. No knowledges in scripting are required.
Take a look to the file `/Self Testing/REST API/0001_Rest_Api.tgx` for a complete example.

## Execute the sample in 2 steps

    
1. From the client, open the test `/Self Testing/REST API/0001_Rest_Api.tgx`

1. And run-it


## Send HTTP requests

1. Create a new test plan and insert as child the test `/Snippets/Protocols/02_Send_HTTP.tsx`

    ![](/docs/images/snippets_http_testplan.png)
    
2. From the test inputs, locate all parameters starts with `HTTP_REQ` and edit them according to the HTTP request to sent

    ![](/docs/images/snippets_http_req.png)
    
3. Configure the expected response, regular expressions are supported

    ![](/docs/images/snippets_http_rsp.png)

4. From the test inputs, locate the parameter `SERVERS` and select the remote http server.
The server parameter must be a shared parameter (or a list of shared parameters) with the following mandatory keys:

    - "HTTP_DEST_HOST":           "127.0.0.1",
    - "HTTP_DEST_PORT":           8090,
    - "HTTP_DEST_SSL":            false,

## Capture data in HTTP response

This part will explains to extract data from the HTTP response to re-use it in a next test. 
A complete sample exists in `/Self Testing/REST API/001_Sessions_Login.tpx`. As you can see in the following example, 
the session_id is captured from the headers and save in the cache with the key name `CAPTURED_SESSION_ID`

![](/docs/images/snippets_http_capture.png)
