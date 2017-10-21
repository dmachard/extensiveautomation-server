---
name: HTTP example
---

# HTTP example

* [Introduction](http#introduction)
* [Adapter configuration](http#adapter-configuration)
* [Make a basic GET request](http#make-a-basic-get-request)
* [Use operators to describe the expected response ](http#use-operators-to-describe-the-expected-response)

## Introduction

This sample show how to use the HTTP client adapter. 

This adapter enables to send or receive HTTP requests and response with:

- SSL and proxy (socks 4, 5 and http) support
- Chunked or content-length data support
- Basic, digest authentication support

The following explanations are based on the sample available on `/Samples/Tests_Adapters/02_HTTP.tsx`

**Please use [http snippets](http://documentations.extensivetesting.org/docs/generic_use/send_http) for more efficiency**

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_HTTP = SutAdapters.HTTP.Client(
                                                parent=self, 
                                                debug=input('TRACE'), 
                                                destinationIp=input('DST_IP'), 
                                                destinationPort=input('DST_PORT'),
                                                sslSupport = input('SSL_SUPPORT'), 
                                                agent=agent('AGENT_SOCKET'), 
                                                agentSupport=input('SUPPORT_AGENT')
                                            )
    ```
    
    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |TRACE|boolean|False|
    |DST_IP|string|www.google.fr|
    |DST_PORT|integer|443|
    |SSL_SUPPORT|boolean|True|
    |SUPPORT_AGENT|boolean|False|

## Make a basic GET request

1. Make a GET request and set the expected response code as below

    ```python
    rsp = self.ADP_HTTP.GET( 
                                uri="/", 
                                host=input('HOST'), 
                                timeout=input('TIMEOUT'),
                                codeExpected=200
                            )
    if rsp is None:
        self.step1.setFailed(actual="bad response received")	
    else:
        self.step1.setPassed(actual="http response OK")	
    ```
        
## Use operators to describe the expected response 

1. Make a GET request use operators as below to describe the expected response. Go the [operators](http://documentations.extensivetesting.org/docs/advanced_use/howto_operators) guide to have the list of available operators.

    ```python
    headersExpected = { TestOperators.Contains(needle='server'): TestOperators.Any() }
    
    rsp = self.ADP_HTTP.GET( 
                            uri="/", 
                            host=input('HOST'), 
                            timeout=input('TIMEOUT'),
                            versionExpected=TestOperators.Endswith(needle='1.1') ,
                            codeExpected=TestOperators.NotContains(needle='200') ,
                            phraseExpected=TestOperators.NotContains(needle='Testing') ,
                            bodyExpected=TestOperators.Contains(needle='google') )                                    
                            headersExpected=headersExpected
                            )
    if rsp is None:
        self.step1.setFailed(actual="bad response received")	
    else:
        self.step1.setPassed(actual="http response OK")	
    ```
    
   As described above, the response must be in accord with the following statements:
   
    - the version must ends with the value 1.1
    - the code must no contains the value 200
    - the phrase must not contains the value Testing
    - the body must contains the value google.
    - And finally, the http response must contains a header named server with any value