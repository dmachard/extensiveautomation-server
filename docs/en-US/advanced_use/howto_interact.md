---
name: How to make interactive testing
---

# How  to make interactive testing

* [Purpose](howto_interact#purpose)
* [Write interactive test with script](howto_interact#write-interactive-test-with-script)
* [Write interactive test with automation assistant](howto_interact#write-interactive-test-with-automation-assistant)

## Purpose

If you want to ask something to the tester during the test execution, you can use the **interact** feature to do that.
This feature can be usefull to configure a server or application in interact mode for example.

# Write interactive test with script

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line

    ```python
    user_rsp = self.interact(ask="Your name?", timeout=30.0, default=None)
    ```
 
3. Execute the test, the framework will stop automatically and ask to the tester to respond to the question.

    ![](/docs/images/client_interact.png)

4. When the user responded until the timeout, you can get the response and make what you want with it.

# Write interactive test with automation assistant

1. Open the automation assistant and go to the `Basic Action Automator` tabulation

2. Select the `ASK SOMETHING` action in the combobox list

3. Specify the question to ask to the user and how to save the response in the cache

4. Click on the button `Add Action` to save the action

    ![](/docs/images/interact_automation.png)
 
 
**Notes:** 

- If the tester does not provide the response, you can set a default response with the `default` argument
