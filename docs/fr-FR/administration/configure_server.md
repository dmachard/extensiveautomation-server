---
name: Configure server
---

# Configure server

* [Make Backups](administration/configure_server#backups)

## Make Backups

By default, a backup of all tests, adapters and libraries are done every day.
You can change the occurence or disable the feature according to the configuration file `setting.ini`
All backups are save in the folder `/opt/xtc/current/Var/Backups`. Save the content of this folder in a safe remote storage.

```
[root@vps Backups]# ll
total 24
drwxr-xr-x 2 xtsys xtsys 4096 Sep  6 23:45 Adapters
drwxr-xr-x 2 xtsys xtsys 4096 Aug 27 13:00 Archives
drwxr-xr-x 2 xtsys xtsys 4096 Sep  6 23:50 Libraries
drwxr-xr-x 2 xtsys xtsys 4096 Sep  7 03:11 Tables
drwxr-xr-x 2 xtsys xtsys 4096 Sep  7 04:38 Tasks
drwxr-xr-x 2 xtsys xtsys 4096 Sep  6 23:40 Tests
```

1. Go to the folder `/opt/xtc/current/` and edit the file `setting.ini`

2. Locate the section `[Backups]` to change the behaviour

3. Update keys according the format value explained below: 

    - Weekly: 6|(day,hour,minute,second)
              day: Monday is 0 and Sunday is 6
    - Daily: 5|(hour,minute,second)
    - Hourly: 4|(minute,second)
   
    Example:
    
        [Backups]
        ; tests repository
        ; 0=disable 1=enable
        tests=1
        ; backup zip name
        tests-name=tests-automatic-backup
        ; backup weekly on sunday at 23:40:00
        tests-at=5|23,40,00

3. Save the file and reload the configuration to take the change in account.

    ```
    xtctl reload
    ```