---
name: Migration Guide
---

# Migration Guide

This part can be useful to deploy a new test server with old data. Read the **[backup](http://documentations.extensivetesting.org/docs/administration/configure_server#make-backups)** page for more details about backups.

## Migration

1. Make a new from scratch deployment, follow the **[installation](server_deployment/installation)** guide.

2. Retrieve all backups from the old server (folder `/opt/xtc/current/Var/Backups`)

    - Tests
    - Adapters
    - Librairies
    - Database dump
    - Tasks

3. Restore adapters package in `/opt/xtc/current/Packages/SutAdapters/`

4. Restore libraries package in `/opt/xtc/current/Packages/SutLibraries/`

5. Import the dump of the database

    - users table
    - projects table
    - environment data table

6. Restore all tests, unzip your backup in `/opt/xtc/current/Var/Tests/`

7. And finally, restore tasks backup in `/opt/xtc/current/Var/Backups/Tasks/`