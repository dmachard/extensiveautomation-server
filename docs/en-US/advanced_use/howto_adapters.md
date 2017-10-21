---
name: How to use adapters
---

# How to use adapters

* [Purpose](howto_adapters#purpose)
* [Use adapters in your test](howto_adapters#initialize-adapters-in-your-test)

## Purpose

The adapters enables to interact with the system under test. For example, if you want to test a server with SSH, you need to use the SSH adapter in your test.

Go to the [Sut Adapters](http://documentations.extensivetesting.org/docs/extensions/adapters) page to see the complete list of all availables adapters. 

You can also add new one if missing, follow the [development guide](http://documentations.extensivetesting.org/docs/personalizations/new_adapter) to do that.

## Use adapters in your test

1. Add your adapter, in the `prepare` section, below an example with the REST adapter. You can use the online assistant to see how to configure your adapter.

    ```python
    self.ADP_REST = SutAdapters.REST.Client(
                                            parent=self, 
                                            destinationIp=input('DEST_IP'), 
                                            destinationPort=input('DEST_PORT'), 
                                            debug=input('DEBUG'), 
                                            sslSupport=input('DEST_SSL')
                                            )
    ```
    
2. Run the test, no errors must occured. Now you can use all functions of the adapters in the `definition` part.

    ```python
    self.ADP_REST.sendRest(
                            uri='/rest/session/logout', 
                            host=input('DEST_IP'), 
                            method='GET'
                          )
    ```
    