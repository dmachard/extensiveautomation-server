---
name: Add new agent
---

# Development guide to add a new agent 

* [For Linux](new_agent#for-linux)
* [For Windows](new_agent#for-windows)

## For Linux

* [Prepare sources](new_agent#prepare-sources)
* [Add a new agent](new_agent#add-a-new-agent)
* [Test your agent](new_agent#test-your-agent)

### Prepare sources

1. Retrieve the Toolbox for Linux and deploy-it on a dedicaded machine. Follow the [installation](http://documentations.extensivetesting.org/docs/toolbox_deployment/installation#package-for-linux) guide

2. Check to start a `dummy` agent

    ```
    ./toolagent <test_server_ip> <test_server_port> True dummy "agent.test" "my first agent"
    ```

3. Go to the the web interface `Overview > Agents` to check if the agent is running properly.

### Add a new embedded agent

1. Go to the folder `./Embedded/` and copy the dummy agent

    ```
    cp DummyAgent.py MyAgent.py
    ```

2. Edit the new file and change the type of your agent according to your need.

    ```python
    __TYPE__="""myagent"""
    ```
    
3. Update the name of the class `Dummy` by the name of your agent and also the `initialize` function.

    ```python
    class MyAgent(GenericTool.Tool):
    ```

    ```python
    def initialize (controllerIp, ......):
        """
        Wrapper to initialize the object agent
        """
        return MyAgent(....
    ```

4. Save all changes in the file

5. Finally, declare this new agent in the Python `__init__` file, add the following line:


    ```python
    from Embedded import MyAgent
    ```

6. After that, your agent must appear on the documentation of the `./toolagent` script

### Test your agent

1. Start your agent as below:

    ```
    ./toolagent <test_server_ip> <test_server_port> True myagent "agent.test" "my first agent"
    ```

2. Check on the web interface `Overview > Agents` if the agent appears on the list

## For Windows

* [Prerequisites](new_agent#prerequisites)
* [Prepare sources](new_agent#prepare-sources-1)
* [Configure your plugin](new_agent#configure-your-plugin)
* [Build and test the plugin](new_agent#build-and-test-the-plugin)

### Prerequisites

Prepare your environment, install the following packages:

- Python 3.4 32bits or 64bits
- PyQT4 or 5
- cx_Freeze

### Prepare sources

1. Retrieve plugins from the [remote git](http://support.extensivetesting.org/extensivetesting/plugins-client.git)

2. Copy the folder `dummy` to the folder `myexample`

3. Go to the folder Scripts in your plugin folder and execute the powershell script CodePrepare.ps1. 
This script retrieves automatically the generic module.

4. Finally, edit the file `MyPlugin.py` and change the key `DEBUG` to `True`,

    ```python
    # debug mode
    DEBUGMODE=True
    ```
    
    Activate the debug mode to run the plugin without the client.

### Configure your plugin

1. Edit the file `config.json` and configure your plugin

    ```
    {
        "plugin": {
                    "name": "MyExample", 
                    "version": "1.0.0" 
                    }
    }
    ```
    
2. Edit the file `MyPlugin.py` and update the following keys
    
    ```python
    # name of the main developer
    __AUTHOR__ = 'Denis Machard'
    # email of the main developer
    __EMAIL__ = 'd.machard@gmail.com'
    ```
    
### Build and test the plugin

1. Execute the file `MakeExe3.bat` in the `Scripts` folder. This file will automatically create a binary.   

2. Deploy the output on the client plugins folder. Read the [installation](http://documentations.extensivetesting.org/docs/client_plugin_deployment/installation) guide.


