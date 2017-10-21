---
name: How to use test configuration
---

# How to use test configuration

* [Purpose](howto_config#purpose)
* [Export test parameters to a test config](howto_config#export-test-parameters-to-a-test-config)
* [Import a test config to your test](howto_config#import-a-test-config-to-your-test)

## Purpose

The test parameters can be exported or imported from/to a test config file. So with this feature, you can prepare different test configurations and import them after.

![](/docs/images/client_testconfig.png) 

## Export test parameters to a test config

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Go the test inputs parameters, and click on the following button to export inputs

    ![](/docs/images/client_testconfig_export.png)
    
3. Save the exported file in the remote test repository.

## Import a test config to your test

1. Open the previous test config file

2. Add a test parameter, and save-it.

3. Go the previous test unit and try to import the new test config.

    ![](/docs/images/client_testconfig_import.png)

4. After the importation, all inputs are replaced by your file.