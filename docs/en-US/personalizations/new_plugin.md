---
name: Add plugin for Client
---

# Development guide to add a new plugin for the client

* [Prerequisites](new_plugin#prerequisites)
* [Prepare sources](new_plugin#configure-your-plugin)
* [Configure your plugin](new_plugin#configure-your-plugin)
* [Build and test the plugin](new_plugin#build-and-test-the-plugin)
* [Communicate with the client](new_plugin#communicate-with-the-client)
* [Read or write configuration](new_plugin#read-or-write-configuration)
* [Troubleshooting functions](new_plugin#troubleshooting-functions)

## Prerequisites

Prepare your environment, install the following packages:

- Python 3.4 32bits or 64bits
- PyQT4 or 5
- cx_Freeze

## Prepare sources

1. Retrieve plugins from the [remote git](http://support.extensivetesting.org/extensivetesting/plugins-client.git)

2. Copy the folder `dummy` to the folder `myexample`

3. Go to the folder Scripts in your plugin folder and execute the powershell script `CodePrepare.ps1`. 
This script retrieves automatically the generic module.

4. Finally, edit the file `MyPlugin.py` and change the key `DEBUG` to `True`,

    ```python
    # debug mode
    DEBUGMODE=True
    ```
    
    Activate the debug mode to run the plugin without the client.

## Configure your plugin

1. Edit the file `config.json` and configure your plugin:

    - Define the type
    - Define the name
    - Define the version

    ```
    {
        "plugin": {
                    "name": "MyExample", 
                    "type": "recorder-app", 
                    "version": "1.0.0" 
                    }
    }
    ```
    
2. Edit the file `MyPlugin.py` and update the following keys:
    
    ```python
    # name of the main developer
    __AUTHOR__ = 'Denis Machard'
    # email of the main developer
    __EMAIL__ = 'd.machard@gmail.com'
    ```
    
## Build and test the plugin

1. Execute the file `MakeExe3.bat` in the `Scripts` folder. This file will automatically create a binary.   

2. Deploy the output on the client plugins folder. Read the [installation](http://documentations.extensivetesting.org/docs/client_plugin_deployment/installation) guide.

## Communicate with the client

- To receive data from the client, overwrite the function `insertData` lf the Main widget.
The type of the data argument is json.

```python
class MainPage(QWidget):
    def insertData(self, data):
```

- To send data to the client, use the `sendMessage` function

```python
self.core().sendMessage( cmd='import', data = {"my message": "hello"} )
```

## Read or write configuration

If you need to store some settings, the `config.json` file can be used to do that.

## Troubleshooting functions

Two mode availables to log messages in your code.

- In graphical mode (debug tab page)

    ```
    self.core().debug().addLogWarning("my warning message")
    self.core().debug().addLogError( "my error message")
    self.core().debug().addLogSuccess("my success message" )
    ```

- In the file logs (output.log)
 
    ```
    Logger.instance().debug("my debug message")
    Logger.instance().error("my error message")
    Logger.instance().info("my info message")
    ```



