---
name: Make your test reusable
---

# Make your test reusable

* [Introduction](manage_inputs#introduction)
* [Use aliases](manage_inputs#use-aliases)
* [Use the cache](manage_inputs#use-the-cache)

## Introduction

Make test generic is the best thing to do, you can do it from the automation assistant by using the two following features:

- **CACHE**
- **ALIAS**

## Use aliases

Tests parameters are generated automatically with the automation assistant but the name is not user friendly.

To provide nice parameters to the tester, you can use the ALIAS feature. 
Follow the following procedure to make your first test more generic and reusable.

1. Follow the [system testing](http://documentations.extensivetesting.org/docs/automation_assistant/system_testing) page to generate a test. You will obtains the following test inputs

    ![](/docs/images/aa_generic_inputs.png)

2. Go to the macro mode and edit the `OPEN SESSION ACTION`. Choose the ALIAS option for the host field and specify the value `SERVER_ADDRESS`.

    ![](/docs/images/aa_generic_alias.png)

3. Update the test, you can see a new test input `SERVER_ADDRESS` in the list. If you import this test in a testplan, you can overwrite only this parameter.


## Use the cache

Before to start, read the documentation about the [cache](http://documentations.extensivetesting.org/docs/advanced_use/howto_cache)

Use the cache to provide all inputs you needs to execute your test or save data generated during the test in the cache.