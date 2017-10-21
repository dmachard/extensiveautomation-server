---
name: Uninstall Guide
---

# Uninstall Guide

## Uninstall

1. Go inside the folder used to install the product

2. Execute the script `./uninstall.sh`

```bash
# ./uninstall.sh 
===================================================
=  - Uninstall of the ExtensiveTesting product -  =
=                 Denis Machard                   =
=            www.extensivetesting.org             =
===================================================
* Detecting the operating system                           [  OK  ]
* Detecting the system architecture                        [  OK  ]
* Stopping the ExtensiveTesting server                     [  OK  ]
* Stopping httpd                                           [  OK  ]
* Removing the ExtensiveTesting database                   [  OK  ]
* Removing the ExtensiveTesting source                     [  OK  ]
* Removing the ExtensiveTesting service                    [  OK  ]
* Removing ExtensiveTesting user                           [  OK  ]
* Restoring php                                            [  OK  ]
* Removing httpd configuration                             [  OK  ]
* Restarting httpd                                         [  OK  ]
=========================================================================
- Uninstallation terminated!
=========================================================================
```

**Notes:** 

- If errors occurred during uninstall, you can retry and continue the uninstallation with the option `force`.
