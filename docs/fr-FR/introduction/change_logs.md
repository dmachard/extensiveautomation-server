---
name: Change Logs
---

# Change Log

## In progress

### v1x.x.x - xx/xx/xxxx

- Packages
  
- Bug fixes

- Improvements

## Current Version

### v17.1.0 - 22/10/2017

- Packages

  * app-client - 17.1.0
  * core-server - 17.1.0
  * build-server - 17.1.0
  * web-server - 17.1.0
  * app-toolbox - 12.1.0
  * test-library - 17.1.0
  * test-interop - 1.4.0
  * plugins-adapters - 11.1.0
  * plugins-libraries - 8.0.0
  
- Bug fixes

  * app-client - (medium) bad test archive name when the username contains dot
  * app-client - (minor) small changes on minimize application to avoid problems with the next major qt5 framework
  * app-client - (medium) changes on toolbar to avoid graphical issue with Qt5
  * app-client - (minor) test abstract: fix error on deletion when no element is selected
  * app-client - (minor) fix bad call reference, occured only with local repository
  * app-client - (minor) test plan/global: fix bad columns order in print view
  * plugin-adapters - (medium) ssl: disable SNI feature
  * plugin-adapters - (minor) ssh client: disconnected status not set properly on bad authentication and negotiation 
  * core-server - (minor) test Model: fix bad generic adapters/libraries version in loading modules event
  * core-server - (minor) repo archives: no more log an error when the test result is not found in repository
  * core-server - (minor) task manager: fix issue to enable to receive basic report by email
  * test-library - (medium) bad test executed on fail condition, only for testplan/testglobal
  * test-library - (minor) wrong reference name for TestOperatorsLib in line 4456 - Issue #3
  * test-library - (minor) condition and Label methods of TestCase class missing in help - Issue #4
  * test-library - (minor) fix error in test logger xml, bad variable name

- Improvements

  * app-client - (minor) Assistant: web part changed to support the new function doSwitchToDefaultWindow
  * app-client - (minor) Test properties: update to support new keywords (ABORTONFAIL and ABORTONSUCCESS) on custom type
  * app-client - (medium) Test properties: new test parameter "json"
  * app-client - (minor) Scroll the contents one pixel at a time in the informations tree view
  * app-client - (medium) Assistant: internal webkit browser marked as deprecated and removed (not really usefull) 
  * app-client - (minor) Main tab orientation added in settings file (south by default)
  * app-client - (medium) Code cleanup to support the next graphical library QT5 and python36, not yet terminated
  * app-client - (minor) Restore the main application from test properties after snapshot
  * app-client - (medium) Improvment to support ubuntu, experimental support
  * app-client - (minor) Assistant updated to support change in test executor library
  * build-server - (minor) some improvements in default snippets (run_cmd,...)
  * build-server - (medium) new sut adapters 11.1.0
  * build-server - (major) executable client, toolboxes and plugins are no more embedded by default, can be always added manually
  * build-server - (medium) new client 12.1.0
  * build-server - (major) new nodejs v6.11 embedded by default
  * plugin-adapters - (minor) Gui selenium: new high level function doSwitchToDefaultWindow
  * plugin-adapters - (medium) Tcp server: update to support agent mode
  * plugin-adapters - (medium) Http server: update to support agent mode
  * plugin-adapters - (medium) Ssh terminal: opened event splitted in two, first screen event added
  * plugin-adapters - (minor) Ssh terminal: no more possible to send data if not connected
  * plugin-adapters - (minor) Ssh client: new handleConnectionFailed on bad authentication and negotiation
  * plugin-adapters - (medium) Ssh terminal: new event "open error" when the authentication failed
  * plugin-adapters - (minor) Tcp: wait complete ssl handshake on connection
  * web-server - (minor) display download links only if additionals packages exists in server
  * web-server - (minor) alphabetical ordered for all users and projects list
  * core-server - (medium) Cli: new state to indicate when the server is booting or not
  * core-server - (medium) New script to generate api key for user
  * core-server - (medium) Rest API: return None instead of undefined when the test result is not yet available
  * core-server - (medium) Task Manager: new function to send test report in attachment
  * core-server - (minor) Rest API: /results/status updated to return the progress of the execution in percent
  * test-library - (major) new feature to save cache data in memory instead of a file
  * test-library - (major) New function to terminate or interrupt a test or a testcase
  * test-library - (minor) add wait message in the basic report
  * test-library - (medium) new json test properties 
  * test-library - (minor) new function to get previous step from a testcase
  * test-interop - (medium) New email interop library 
  * app-toolbox - (medium) Binary SoapUI is no more embedded by default, must be installed manually
  * app-toolbox - (medium) Support tcp server on socket agent 
  * app-toolbox - (medium) Build: android.smsgateway apk no more embedded by default
  * app-toolbox - (minor) Build: Gecko Driver updated to 0.18.0
  * app-toolbox - (minor) Build: Chrome driver updated to 2.30
  * app-toolbox - (minor) Build: Opera driver updated to 2.29
  * app-toolbox - (minor) Build: Java JRE updated to the version 8u141 x64

### v17.0.0 - 04/06/2017

- Packages

  * app-client - 17.0.0
  * core-server - 17.0.0
  * build-server - 17.0.0
  * web-server - 17.0.0
  * app-toolbox - 12.0.0
  * test-library - 17.0.0
  * test-interop - 1.3.0
  * plugins-adapters - 11.0.0
  * plugins-libraries - 8.0.0
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
  
### v16.1.0 - 30/03/2017

- Packages

  * app-client - 16.1.0
  * core-server - 16.1.0
  * build-server - 16.1.0
  * web-server - 16.0.1
  * app-toolbox - 11.1.0
  * test-library - 16.0.1
  * test-interop - 1.2.0
  * plugins-adapters - 10.2.0
  * plugins-libraries - 7.3.1
  
- Bug fixes

  * More details on each HISTORY files

- Improvements

  * More details on each HISTORY files

### v16.0.0 - 25/02/2017

- Packages

  * app-client - 16.0.0
  * core-server - 16.0.0
  * app-toolbox - 11.0.0
  * test-library - 16.0.0
  * test-interop - 1.2.0
  * plugins-adapters - 10.1.0
  * plugins-libraries - 7.3.0
  
- Bug fixes

  * More details on each HISTORY files

- Improvements

  * More details on each HISTORY files

### v15.0.3 - 04/11/2016

- Packages

  * app-client - 15.0.1
  * core-server - 15.0.3
  * app-toolbox - 10.0.0
  * test-library - 15.0.0
  * test-interop - 1.1.1
  * plugins-adapters - 10.0.0
  * plugins-libraries - 7.2.1

- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v14.0.0 - 27/08/2016

- Packages

  * app-client - 14.0.0
  * core-server - 14.0.0
  * app-toolbox - 9.1.0
  * test-library - 14.0.0
  * test-interop - 1.0.0
  * plugins-adapters - 9.3.0
  * plugins-libraries - 7.2.1

- Bug fixes

  * More details on each HISTORY files

- Improvements

  * More details on each HISTORY files
  
### v13.0.0 - 2016-06-23

- Packages

  * app-client - 13.0.0
  * core-server - 13.0.0
  * app-toolbox - 9.0.0
  * test-library - 13.0.0
  * plugins-adapters - 9.2.0
  * plugins-libraries - 7.2.0
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v12.1.0 - 2016-04-29

- Packages

  * app-client - 12.1.0
  * core-server - 12.1.0
  * app-toolbox - 8.1.0
  * test-library - 12.1.0
  * plugins-adapters - 9.1.0
  * plugins-libraries - 7.1.0 
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v12.0.0 - 2016-02-12

- Packages

  * app-client - 12.0.0
  * core-server - 12.0.0
  * app-toolbox - 8.0.0
  * test-library - 12.0.0
  * plugins-adapters - 9.0.0
  * plugins-libraries - 7.0.0 
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v11.2.0 - 2015-11-22

- Packages

  * app-client - 11.2.0
  * core-server - 11.2.0
  * app-toolbox - 7.0.0
  * test-library - 11.2.0
  * plugins-adapters - 8.0.0
  * plugins-libraries - 6.0.0 
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v11.1.0 - 2015-10-18

- Packages

  * app-client - 11.1.0
  * core-server - 11.1.0
  * app-toolbox - 6.1.0
  * test-library - 11.1.0
  * plugins-adapters - 7.0.0
  * plugins-libraries - 5.2.0 
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v11.0.0 - 2015-09-14

- Packages

  * app-client - 11.0.0
  * core-server - 11.0.0
  * app-toolbox - 6.0.0
  * test-library - 11.0.0
  * plugins-adapters - 6.2.0
  * plugins-libraries - 5.1.0 
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v10.1.0 - 2015-07-12

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v10.0.0 - 2015-05-28

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
     
### v9.1.0 - 2015-03-22

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v9.0.0 - 2015-01-05

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v8.0.0 - 2014-10-25

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v7.1.0 - 2014-09-20

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v7.0.0 - 2014-08-08

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v6.2.0 - 2014-06-02

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v6.1.0 - 2014-04-25

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v6.0.0 - 2014-03-23

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
  
### v5.2.0 - 2014-01-12

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
 
### v5.1.0 - 2013-12-08

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v5.0.0 - 2013-09-15

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v4.2.0 - 2013-04-08

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v4.1.0 - 2013-03-10

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v4.0.0 - 2013-01-30

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v3.2.0 - 2012-09-29

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
  
### v3.1.0 - 2012-07-14

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
 
### v3.0.0 - 2012-06-09

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v2.2.0 - 2012-03-28

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v2.1.0 - 2012-02-27

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v2.0.0 - 2012-02-13

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v1.2.0 - 2012-01-14

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files
 
### v1.1.0 - 2011-12-29

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v1.0.0 - 2011-12-13

- Packages

  * More details on each HISTORY files
  
- Bug fixes

  * More details on each HISTORY files
  
- Improvements

  * More details on each HISTORY files

### v1.0.0 beta - 2010-05-17

- First beta release