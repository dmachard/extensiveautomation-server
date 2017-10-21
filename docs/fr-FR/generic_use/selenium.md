---
name: Selenium
---

# Use selenium

* [Introduction](selenium#introduction)
* [Best pratices](selenium#best-pratices)
* [Selenium compatibilities with browsers](selenium#selenium-compatibilities-with-browsers)

## Introduction

The approach used in this solution is to write snippets screen by screen according to the web page.
A complete sample is available in `/Samples/Tests_Gui/Selenium/`. This sample create a new account in google and cancel before the end.

## Execute the sample

1. Deploy a agent of type `selenium-server` on the machine where the test will be executed. 
Please to follow this [guide](http://documentations.extensivetesting.org/docs/toolbox_deployment/first_connection)

2. From the client, open the test `03_001 Create google account and cancel` in `/Samples/Tests_Gui/Selenium/03_TestGlobal`
Configure your test to use your agent. Go to the tab Test Properties > Miscelleneous

    ![](/docs/images/selenium_agent.png)

3. Go the tab `Test Properties > Test Data > Inputs` and specify the web browser to use, by default the test is configured with `Firefox`

    ![](/docs/images/selenium_browser.png)

4. Click on the button Execute to run the test. After that the browser will be automatically opened on the machine where the agent is deployed.
As you will see during the execution, some inputs are generated in random mode.

    ![](/docs/images/selenium_random_data.png)


## Best pratices

* Split your automation browser test in 3 parts 
 - snippets:  write with the automation assistant, screen by screen to make small test 
 - testplan:  use test plan and insert your snippets inside-it to create the scenario to test
 - testglobal:  use test global and insert all testplans inside-it
 
* Describe your tests data as project variables from the web interface and use the generic test `/Snippets/Generic/09_Init_Env`. This test can be used to run your test in several environment (dev, production) and select automatically the associated data to use.
Please to read this [page](http://documentations.extensivetesting.org/docs/generic_use/init_env)

* Always prefer to use xpath to find and manipulate html element

## Selenium compatibilities with browsers

Minimum version of Java required to run Selenium 3 is Java 8+
 
|Browsers|Selenium version| Gecko|
|:---|---:|:---------:|
|Firefox <47 |Selenium 2|No|
|Firefox >47 |Selenium 3|Yes|
|IE|Selenium 3||
|Chrome|Selenium 3||
