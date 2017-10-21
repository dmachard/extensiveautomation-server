---
name: Client development
---

## Client development x64 for Windows

If you want to run the client directly from the source code, please to install the following prerequesites:

 - Python  – https://www.python.org/downloads/release/python-344/ – version 3.4.4 – 64 bits
 
 - PyQT  – https://www.riverbankcomputing.com/software/pyqt/download – version 4.11.4 – 64 bits
 
 - InnoSetup  – http://www.jrsoftware.org/isdl.php) – version 5.5
 
 - Intall py2exe
 
    ```
    C:\Windows\system32>py -3.4 -m pip install py2exe
    Collecting py2exe
      Downloading py2exe-0.9.2.2-py33.py34-none-any.whl (270kB)
        100% |################################| 274kB 34kB/s
    Installing collected packages: py2exe
    Successfully installed py2exe-0.9.2.2
    ```

 - Edit the file `icons.py` in `C:\Python34\Lib\site-packages\py2exe\`. Go to the line `if iconheader.idCount >`
and change the value 10 with 14

## Client development x64 on Centos6 or 7

If you want to run the client directly from the source code, please to install the following prerequesites:

```
yum install epel-release PyQt4 python-test
yum install PyQt4-webkit qscintilla-python
yum install python-pip
```


```
pip install dpkt
pip install cx_freeze
```

    
## Client development x64 on Ubuntu 17.04

If you want to run the client directly from the source code, please to install the following prerequesites:

```
sudo apt-get -y install python-qt4
sudo apt-get –y install python-qscintilla2
sudo apt-get -y install python-pip
sudo pip install dpkt
```


```
sudo apt-get –y install python3-pyqt5
sudo apt-get –y install python3-pyqt5.qsci
sudo apt-get –y install python3-pyqt5.qtwebengine
```
