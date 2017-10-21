---
name: How to use custom properties
---

# How to use custom properties

* [Purpose](howto_custom#purpose)
* [Prepare my first custom withs inputs](howto_custom#prepare-my-first-custom-withs-inputs)
* [Prepare custom input with cache value](howto_custom#prepare-custom-input-with-cache-value)
* [Capture data and save it in cache](howto_custom#capture data and save it in cache)

## Purpose

The custom properties is available from the test properties.
This type enables to construct advanced inputs.

## Prepare my first custom withs inputs

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the test inputs properties part, add the following inputs

    ![](/docs/images/custom_inputs.png)

3. Edit the parameter `DEST_URL` and add the following content

    ![](/docs/images/custom_config.png)

4. In the definition part, add the following line 

    ```python
    Trace(self).info(txt=input('DEST_URL'))
    ```
    
5. Execute the test

    ![](/docs/images/custom_example.png)


## Prepare custom input with cache value

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the test inputs properties part, add the following inputs

    ![](/docs/images/custom_inputs.png)
    
3. In the definition part, add the following line 

    ```python
    Cache().set(name="url_params", data="welcome?user=hello", flag=False)
    ```
    
4. Edit the parameter `DEST_URL` and add the following content

    ![](/docs/images/custom_config_cache.png)

5. In the definition part, add the following line 

    ```python
    Trace(self).info(txt=input('DEST_URL'))
    ```

6. Execute the test

    ![](/docs/images/custom_example_cache.png)
    

## Capture data and save it in cache

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line 

    ```python
	h  = "Set-Cookie: session_id=Mjc5YTg1NjJjNDA3NDU5ZDliNDAwZWJiYjQxMmRjMDI5M;expires=Tue, 02-May-2017 19:43:26 GMT; path=/"
    Cache().capture(data=h, regexp=input('REGEXP'))
    
    session_id =Cache().get(name="SESSIONID")
    Trace(self).warning( "session_id: %s" % session_id)
    ```
    
3. In the test inputs properties part, add the following inputs

    ```
	REGEXP = .*session_id=[!CAPTURE:SESSIONID:];expires.*
    ```
    
4. Execute the test, with the previous custom param, the session_id will be automatically saved in the cache with the provided key.
    
    
5. If you want you can also provided a regex and disable the greedy mode

    ```
	REGEXP = .*session_id=[!CAPTURE:SESSIONID:.*?];.*
    ```
    