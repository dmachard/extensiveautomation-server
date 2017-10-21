---
name: How to use the storage
---

# How to store or read data from your tests

* [Purpose](howto_storage#purpose)
* [Add files in the testcase's private storage](howto_storage#add-files-in-the-testcase’s-private-storage)
* [Add files in the adapter's private storage](howto_storage#add-files-in-the-adapter’s-private-storage)
* [Manage the private storage](howto_storage#manage-the-private-storage)
* [Get files from the public storage](howto_storage#get-files-from-the-public-storage)

## Purpose

Use the **private storage** feature to save logs during the execution of a test. Logs can be saved from tescases or each adapters.
At the end of a test, all logs are automatically zipped in the file `private_storage.zip`, this file can be downloaded from the client

![](/docs/images/private_storage.png)

## Add files in the testcase's private storage

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line to save the string data "hello world" in the private storage of the testcase.
 
    ```python
    Private(self).saveFile(destname="my_logs", data="hello world")
    ```
 
    Append new data to the same file

    ```python
    Private(self).appendFile(destname="my_logs", data="hello world2")
    ```
    
3. Run this test and download the private_storage.zip from the test archives. 

4. Unzip the zip file, the zip contains a folder named `TC-TESTCASE-#1` with a `my_logs` file inside

![](/docs/images/private_storage_zip.png)

## Add files in the adapter's private storage

From a adapter, you can also save files. To do that, you can use the following functions:

![](/docs/images/adaper_private.png)

This is exactly the same behavoir as for the testcase except that data are saved in a dedicated folder for the adapter.

## Manage the private storage

If you have a lot of data to save, you can organize your data by folders. 

Use the `addFolder` or `privateAddFolder` functions to add folder in the private storage

## Get files from the public storage

The public storage enables to make availables files to all tests. This storage can be used to store huge file.

The files must be uploaded to the folder `/opt/xtc/current/Var/Public/` in the test server.

**Notes:** 

- Be careful, all files added in the public storage are accessible to all users 
