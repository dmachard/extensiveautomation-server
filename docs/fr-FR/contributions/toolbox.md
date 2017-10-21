---
name: Toolbox development
---

## Toolbox development x64 for Windows

If you want to run the toolbox directly from the source code, please to install the following prerequesites:

 - Python - https://www.python.org/downloads/release/python-344/ – version 3.4.4 – 64 bits
 
 - python requests library
 
    ```
    py -3.4 -m pip install requests
    ```

 - python PyMySQL library

    ```
    C:\Users\Denis>py -3.4 -m pip install PyMySQL
    Collecting PyMySQL
    Downloading PyMySQL-0.7.10-py2.py3-none-any.whl (76kB)
    […]
    Successfully installed PyMySQL-0.7.10
    ```
 
 - python psycopg2  library
 
    ```
    C:\Users\Denis>py -3.4 -m pip install psycopg2
    Collecting psycopg2
    Downloading psycopg2-2.7.1-cp34-none-win32.whl (818kB)
    […]
    Successfully installed psycopg2-2.7.1
    ```
    
 - python pymssql  library
 
    ```
    C:\Users\Denis>py -3.4 -m pip install pymssql
    Collecting pymssql
    Downloading pymssql-2.1.3-cp34-cp34m-win32.whl (331kB)
    100% |################################| 337kB 637kB/s
    Installing collected packages: pymssql
    Successfully installed pymssql-2.1.3
    ```
    
 - python paramiko  library

    ```
    py -3.4 -m pip install paramiko
    Collecting paramiko
    Downloading paramiko-2.1.2-py2.py3-none-any.whl (172kB)
    Downloading cryptography-1.8.1-cp34-cp34m-win32.whl (1.1MB)
    Downloading pyasn1-0.2.3-py2.py3-none-any.whl (53kB)
    Downloading cffi-1.9.1-cp34-cp34m-win32.whl (145kB)
    Downloading asn1crypto-0.22.0-py2.py3-none-any.whl (97kB)
    Downloading packaging-16.8-py2.py3-none-any.whl
    Downloading idna-2.5-py2.py3-none-any.whl (55kB)
    Downloading six-1.10.0-py2.py3-none-any.whl
    Downloading pycparser-2.17.tar.gz (231kB)
    Downloading pyparsing-2.2.0-py2.py3-none-any.whl (56kB)
    Running setup.py install for pycparser ... done
    ```
 
 - python selenium-3.3.4-extensivetesting  library

    ```
    C:\Users\Denis>c:\Python34\python.exe setup.py install
    […]
    Installed c:\python34\lib\site-packages\selenium-2.53.1-py3.4.egg
    Processing dependencies for selenium==2.53.1
    Finished processing dependencies for selenium==3.3.1
    ```
