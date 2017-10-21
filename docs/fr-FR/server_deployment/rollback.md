---
name: Rollback Guide
---

# Rollback Guide

## Rollback

1. Go inside the folder used to install the product

2. Execute the script `./rollback.sh` and provies the previous targetted version `X.X.X`


```
# ./rollback.sh X.X.X
==================================================
=  - Rollback of the ExtensiveTesting product -  =
=                 Denis Machard                  =
=            www.extensivetesting.org            =
==================================================
* Detecting the operating system                           [  OK  ]
* Detecting the system architecture                        [  OK  ]
* Stopping the ExtensiveTesting server                     [  OK  ]
* Rollbacking to ExtensiveTesting-X.X.X                    [  OK  ]
* Restarting the ExtensiveTesting server                   [  OK  ]
=========================================================================
- Rollback terminated!
=========================================================================
```
