---
name: How to use the cache
---

# How to use the cache

* [Purpose](howto_cache#purpose)
* [Save data in the cache](howto_cache#save-data-in-the-cache)
* [Read data from the cache](howto_cache#read-data-from-the-cache)
* [Sharing data between testcases](howto_cache#sharing-data-between-testcases)
* [Capture data with regular expressions and save-it in cache](howto_cache#capture-data-with-regular-expressions-and-save-it-in-cache)

## Purpose

Running several testcases sharing the same data can be done thanks to the **cache storage** feature. 
When you run a test (unit, testplan, etc..), a cache is shared between all tests. The cache is based on a dictionnary with key/value.

![](/docs/images/client_cache.png)
    
## Save data in the cache

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line to save the string data "hello" in the cache.

    ```python
    Cache().set(name="my_data", data="hello")
    ```

3. Save this test

## Read data from the cache

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line to get data

    ```python
    my_data= Cache().get(name="my_data")
    Trace(self).warning(my_data)
    ```
    
3. Save this second test. If you try to run this test, my_data will be empty

## Sharing data between testcases

1. Click on the button ![](/docs/images/client_new_tpx.png) to create a new test plan.

2. Import the two previous tests as bellow:

    ![](/docs/images/client_cache_testplan.png)

3. Run your test plan, as expected the 2nd test can read the value saved by the first test.

## Capture data with regular expressions and save-it in cache

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line

    ```python
    my_data="March, 25 2017 07:38:58 AM"
    ```

3. Always in the definition part, add the following lines to capture just the  time from the string. 
The time extracted is saved in the cache with the key name `TIME`.

    ```python
    Cache().capture(data=my_data, regexp=".* (?P<TIME>\d{2}:\d{2}:\d{2}) .*")
    ```
    
4. Display the time stored in the cache after the capture

    ```python
    Trace(self).info( txt=Cache().get(name="TIME") )
    ```
    
5. Execute the test, you will obtains the following result.

    ![](/docs/images/client_cache_capture.png)