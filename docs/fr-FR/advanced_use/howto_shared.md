---
name: How to use the shared mode
---

# How to use adapter in shared mode

* [Purpose](howto_shared#purpose)
* [Activate the shared mode on a adapter.](howto_shared#activate-the-shared-mode-on-a-adapter)
* [Retrieve a adapter from a testcase](howto_shared#retrieve-a-adapter-from-a-testcase)

## Purpose

The shared mode is a feature used with adapters and libraries. When this mode is enabled, you can share adapters between several tests in a test plan.

An example, you need to execute a application and inspect the behaviour of logs received on a syslog server during the execution of your test.
With a test plan in shared mode: 

- You can inspect in background the syslog server 
- Make actions to test the application
- Modify the test in realtime according the logs read from the syslog server.

## Activate the shared mode on a adapter

The shared mode is supported on all adapters, to activate this mode, you must change the `shared` argument to `True`
When this mode is activated, the adapter continue to run in background.

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Initialize the adapter on the prepare section of your test. Activate the shared mode, define also the name as below:

    ```python
    self.ADP_EXAMPLE = SutAdapters.Dummy.Adapter(
                                                    parent=self, 
                                                    debug=False, 
                                                    name="MY_ADAPTER", 
                                                    shared=True
                                                )
    ```
    
3. Save this test in the remote repository

4. Create a test plan and import the previous test.

## Retrieve a adapter from a testcase

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add the following lines in the prepare section

    ```python
	self.ADP_EXAMPLE = self.findAdapter(name="MY_ADAPTER")
	if self.ADP_EXAMPLE is None: Test(self).interrupt("unable to find the adapter")
    ```
    
3. Import this test in the test plan created before.

4. Execute the test, on the second testcase, you will interact with the adapter initialized from the first testcase.