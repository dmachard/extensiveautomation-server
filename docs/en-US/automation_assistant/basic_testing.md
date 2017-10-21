---
name: Basic testing
---

# Basic testing

* [Introduction](basic_testing#introduction)
* [Write a test](basic_testing#write-a-test)

## Introduction

This part enables to write simple actions in your test like:

|Action Name|Description|
|-----:|:-----|
|LOG MESSAGE|Display an information message|
|LOG WARNING|Display a warning message|
|SET VALUE|Save data in cache|
|RESET CACHE|Delete all data from the cache|
|USERCODE|Add specific actions in generated test|
|WAIT DURING|Just wait during XX seconds|
|CHECK IF VALUE|Checking the value and expect to find something|
|ASK SOMETHING|Interact with user|

## Write a test

1. Connect the remote test server and from the welcome page of the client, click on the `New Basic Test` link 

    ![](/docs/images/aa_basic_link.png)

2. Select the `LOG MESSAGE` action and specify the message `hello world`

    ![](/docs/images/aa_basic.png)
    
3. Click on the button `Add Action` to register your step in the list of actions

4. Select the `ASK SOMETHING` action, provide the question to ask to the user during the execution and save the response in the cache with the key `username`

    ![](/docs/images/aa_basic.png)

5. Log the response provided in the test, do to that select the `LOG MESSAGE` action. Select the `CACHE` type in the combo list and set the text to `username`

    ![](/docs/images/aa_basic_log.png)
    
6. Select the `CHECK IF VALUE` from the list of actions, this actions enables to check a specific value in the response provided by the user during the execution of the test.

7. Specify the previous key name `username` in the `Checking from` field

8. Select the operator (Contains by default) but you can also choose regexp for example

9. Specify the string to find in the response, if not found then the test will be failed.

    ![](/docs/images/aa_basic_check.png)

10. Your test should be as below

    ![](/docs/images/aa_basic_test.png)

11. Finally click on the button `Create test` to generate your test

**Notes:** 

Go the [manage inputs](http://documentations.extensivetesting.org/docs/automation_assistant/make_generic) page for more informations about the management of the cache in the automation assistant. 