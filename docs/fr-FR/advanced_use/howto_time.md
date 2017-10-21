---
name: How to handle the time
---

# How to handle the time

* [Purpose](howto_time#purpose)
* [Make a pause in your test](howto_time#make-a-pause-in-your-test)
* [Make a pause until a specific date and time](howto_time#make-a-pause-until-a-specific-date-and-time)

## Purpose

This feature enables to make some sleep during the execution of your test.

## Make a pause in your test

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line to do nothing during 10 seconds

    ```python
    Time(self).wait(timeout=10)
    ```
    
3. Execute your test

## Make a pause until a specific date and time

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. In the definition part, add the following line to do nothing during 10 seconds

    ```python
    Time(self).waitUntil(dt='2016-09-12 02:00:00', fmt='%Y-%m-%d %H:%M:%S', delta=0)
    ```
    
3. Execute your test.

