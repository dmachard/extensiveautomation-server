---
name: HP ALM QC
---

# HP ALM QC

* [Introduction](hpqc#introduction)
* [How to install it?](selenium_ide#how-to-install-it)
* [Configure the plugin](hpqc#configure-the-plugin)
* [How to export tests?](hpqc#how-to-export-tests)
* [How to export results?](hpqc#how-to-export-results)

## Introduction

This plugin enables to make a link with the HP QualityCenter tools. You can use-it to:

- Exports ExtensiveTesting tests to the testplan of QC
- Exports results in the testlab of QC

## How to install it

Like all the other Extensive Testing plugins, simply copy the plugin in the plugins directory of your Exensive Testing installation.
At Extensive Testing launch, the shell recorder plugin will be automatically available along with the other installed plugins.

## Configure the plugin

1. From the main menu, click on the menu `Plugins > HP ALM QC`

2. Go to the `Settings` tabulations

3. Configure the following informations:

    - QualityCenter url, the url must be ended with `qcbin`
    - Login
    - Password
    - The domain authorized according to the login
    - The destination project and authorized according to the login

4. Click on the `Test Connection` button. If OK then click on the button `Save Settings`

## How to export tests

1. Open your test in the workspace.

2. Click on the button ![](/docs/images/generate_design.png) to generate the design of your test

3. Click on the button ![](/docs/images/design_qc_plugin.png)

4. The plugin appears automatically with the previous test design loaded. If you want you can edit tests before to export it

    ![](/docs/images/qc_plugin.png)

5. Select the testcase to export and click on the button `Export Test`

## How to export results

1. From the `Tests Archives` tabulations, click on a test result to load the report.

2. From the toolbar, click on the button ![](/docs/images/design_qc_plugin.png)

3. The plugin appears automatically with the previous test report loaded. 

    ![](/docs/images/qc_plugin_exportresults.png)

4. Select the testcase to export and click on the button `Export Results`

