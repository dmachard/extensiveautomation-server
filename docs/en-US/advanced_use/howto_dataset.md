---
name: How to use dataset
---

# How to use dataset

* [Purpose](howto_dataset#purpose)
* [Create a dataset file](howto_dataset#create-a-dataset-file)
* [Import dataset in your test](howto_dataset#import-dataset-in-your-test)

## Purpose

Dataset files can be used in your test to use datas in your test. A dataset file is just a basic text file, so it's can be a csv, xml files or as you want.
For example, if your test is used to make a provisionning in a system, you can use a dataset witch contains users informations, etc..

## Create a dataset file

1. Click on the button ![](/docs/images/client_new_tdx.png) to create a new dataset

2. Add the following data in the file, this is a csv format.

    ```
    a;1;administrator
    b;2;tester
    ```
    
3. Save-it

## Import dataset in your test

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add a new test `DATA` parameter of the type `dataset`, select the previous dataset file

    ![](/docs/images/client_testdata.png)
    
3. Read this parameter from your test

    ```python
    for d in input('DATA').splitlines():
        Trace(self).info( d ) 
    ```
    
4. Execute the test