---
name: Server disaster
---

# Recover after a server disaster

In case of a disaster of the server, you can try to follow the procedure bellow:

1. Install a new server from scratch

2. Retrieve all backups files from the folder `/opt/xtc/current/Var/Backups` or from your safe remote storage.
    - tests
    - adapters
    - libraries
    - database dump
    - tasks
    
3. Re-deploy adapters in `/opt/xtc/current/Packages/SutAdapters/`

4. Re-deploy libraries in `/opt/xtc/current/Packages/SutLibraries/`

5. Import database dump

6. Import tests in `/opt/xtc/current/Var/Tests/`

7. And finally, restore tasks backup in `/opt/xtc/current/Var/Backups/Tasks/`