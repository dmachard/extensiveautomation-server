---
name: How to use project variables
---

# How to use project variables

* [Purpose](howto_projectsvariable#purpose)
* [Add a project variable](howto_projectsvariable#add-a-project-variable)
* [Read project variable from a test](howto_projectsvariable#read-project-variable-from-a-test)
* [Add advanced value in a project variable](howto_projectsvariable#add-advanced-value-in-a-project-variable)

## Purpose

Sometime, it's can be useful to share parameters between all tests. To do that, you can use the **project variables** features.

This features is available only from the web interface in the menu `Tests > Project variables`. The project variables can contains advanced value with the `JSON` format. 

## Add a project variable

1. From the web, connect in your online test center as administrator and navigate in the menu to `Tests > Project variables`

2. Click on ![](/docs/images/server_web_add.png) to add a new parameter

3. Set the name and value of your parameter as below. 

    ![](/docs/images/web_add_project_variables.png)

4. Click on the button `Add` to save this parameter.

## Read project variable from a test

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add a new test parameter with the type shared as below

    ![](/docs/images/client_params_shared.png)

3. Log the new parameter link to the project variable in your test

    ![](/docs/images/client_param_shared.png)

    ```python
    Trace(self).warning(input('PARAM_PROJECT'))
    ```

4. Run the test, you will see the value of the remote variable in the test events logger.
    
## Add advanced value in a project variable

1. Add a new parameter and save the following value. This example enables to save ip/port of a server in one parameter.

    ```
    {
        "IP": "192.168.1.248",
        "PORT": 80
    }
    ```
    
    ![](/docs/images/web_add_project_variables_advanced.png)


2. Add the following parameter as below to read just the IP value

    ![](/docs/images/client_shared_param_json.png)

3. Get the value in your test

    ```python
    Trace(self).warning(input('MY_SERVER'))
    ```