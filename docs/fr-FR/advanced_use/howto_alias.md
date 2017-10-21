---
name: How to use aliases
---

# How to use aliases

* [Purpose](howto_alias#purpose)
* [Use aliases in test plan](howto_alias#use-aliases-in-test-plan)

## Purpose

As you see, tests are embedded with tests parameters and can be overwrited in a testplan. 
If you want to miniize the maintenance of your tests, you can use the **aliases** feature.

Example:

- A test `test1` contains the parameter named `MY_PARAM`
- This test is imported in a test plan  
- In the testplan, this parameter is not enough clear. So you need to change the name in the original test but it's not very efficient.
- The solution is to use aliases to avoid to modify the original test `test1`

## Use aliases in test plan

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add the following line in your test and save it 

    ```python
    Trace(self).info(txt=input('TIMEOUT'), bold=False, italic=False, multiline=False, raw=False)
    ```
    
3. Click on the button ![](/docs/images/client_new_tpx.png) to create a new test plan and change the value of `TIMEOUT` on the top of the treeview as below

    ![](/docs/images/client_testplan_parameters.png)

4. Import the previous test and run the test. At this state, the value of the parameter `TIMEOUT` in the `test1` will be the value of the parent.

5. From the test plan, click on the test1 and add the parameter `TIMEOUT_BIS` with the type `str`

    ![](/docs/images/client_alias_bis.png)

6. Click on the parameter `TIMEOUT`, choose alias and select the `TIMEOUT_BIS` parameter.

7. Copy the `TIMEOUT_BIS` parameter and put-it on the top

    ![](/docs/images/client_alias_param.png)

8. Run the test plan, you will see the value of the alias instead of the value of the original parameter.
 
 