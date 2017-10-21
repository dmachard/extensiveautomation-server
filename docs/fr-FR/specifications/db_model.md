---
name: Database usage
---

# Database usage

A database is used on the test server to store some important data and statistics.
MySQL is only supported.

## Tables listing


|Name|Description|
|:---:|---------|
|xtc-agents|*Not yet used*|
|xtc-agents-stats|*Not yet used*|
|xtc-config|Contains the server configuration. With the server boot, all configuration from the `settings.ini` file is loaded on the database|
|xtc-probes|*Not yet used*|
|xtc-probes-stats|*Not yet used*|
|xtc-projects|Contains projects|
|xtc-relations-projects|Contains relation between projects and users|
|xtc-scripts-stats|Contains statistics of all scripts executed||
|xtc-tasks-history|Contains the history of all task executed |
|xtc-test-environment|Contains all projects variables shared between tests|
|xtc-testabstracts-stats|Contains statistics of all tests abstracts executed|
|xtc-testcases-stats|Contains statistics of all testcases executed|
|xtc-testglobals-stats|Contains statistics of all tests globals executed|
|xtc-testplans-stats|Contains statistics of all tests plans executed|
|xtc-testsuites-stats|Contains statistics of all tests suites executed|
|xtc-testunits-stats|Contains statistics of all tests units executed|
|xtc-users|Contains users|
|xtc-users-stats|Contains statistics of users connections|
|xtc-writing-stats|Contains statistics of all tests in writing mode|