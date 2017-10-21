---
name: Update Guide
---

# Update Guide

## Update

1. Upload the new package `Y.Y.Y` on your automation test server. Be careful to have enough disk space.

2. Untar the new package and go inside the folder.

3. Execute the script `./update.sh` 

    - `X.X.X` : The old version
    - `Y.Y.Y` : The new version

Responds `yes` to start the update

```
# ./update.sh
================================================
=  - Update of the ExtensiveTesting product -  =
=              Denis Machard                   =
=          www.extensivetesting.org            =
================================================
* Detecting the operating system                           [  OK  ]
* Detecting the system architecture                        [  OK  ]
Current product version X.X.X
Current database name xtcXXX
New product version: Y.Y.Y
New database name: xtcYYY
Are you sure to update the product? (yes or no ) yes
Starting update...
* Stopping the current version X.X.X                       [  OK  ]
* Detecting the operating system                           [  OK  ]
* Detecting the system architecture                        [  OK  ]
* Detecting Perl, Python                                   [  OK  ]
* Detecting primary network address (192.168.1.19)         [  OK  ]
* Adding external libraries ...............                [  OK  ]
* Detecting Apache                                         [  OK  ]
* Detecting MySQL/MariaDB                                  [  OK  ]
* Detecting Postfix                                        [  OK  ]
* Detecting Openssl                                        [  OK  ]
* Detecting Php                                            [  OK  ]
* Copying source files                                     [  OK  ]
* Adding startup service                                   [  OK  ]
* Updating configuration files                             [  OK  ]
* Creating extensivetesting user                           [  OK  ]
* Updating folders rights                                  [  OK  ]
* Updating iptables                                        [  OK  ]
* Updating php configuration                               [  OK  ]
* Updating httpd configuration                             [  OK  ]
* Adding virtual host                                      [  OK  ]
* Restarting httpd                                         [  OK  ]
* Restarting firewall                                      [  OK  ]
* Restarting MySQL/MariaDB                                 [  OK  ]
* Restarting postfix                                       [  OK  ]
* Adding the ExtensiveTesting database                     [  OK  ]
* Starting the ExtensiveTesting Y.Y.Y                      [  OK  ]
* Stopping the new version Y.Y.Y                           [  OK  ]
* Restoring SUT adapters from X.X.X to Y.Y.Y       	       [  OK  ]
* Restoring SUT libraries from X.X.X to Y.Y.Y      	       [  OK  ]
* Restoring database from X.X.X to Y.Y.Y           	       [  OK  ]
* Updating database model to Y.Y.Y                     	   [  OK  ]
* Restoring tests from X.X.X to Y.Y.Y              	       [  OK  ]
* Restoring tasks from X.X.X to Y.Y.Y              	       [  OK  ]
* Restarting the new version Y.Y.Y                         [  OK  ]
=========================================================================
- Update terminated!
- Continue and go to the web interface (https://xxxxxxxxx/web/index.php)
=========================================================================
```

**Notes:**

- If not previous version is detected then the procedure is automatically aborted.
