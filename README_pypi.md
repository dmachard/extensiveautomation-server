
| | |
| ------------- | ------------- |
| ExtensiveAutomation | Python automation server |
| Copyright |  Copyright (c) 2010-2020  Denis Machard <d.machard@gmail.com> |
| License |  LGPL2.1 |
| Homepage |  https://www.extensiveautomation.org/ |
| Docs |  https://extensiveautomation.readthedocs.io/en/latest/ |
| Github |  https://github.com/ExtensiveAutomation |   
| Docker Hub | https://hub.docker.com/u/extensiveautomation |   
| PyPI |  https://pypi.org/project/extensiveautomation-server/ |
| Google Users | https://groups.google.com/group/extensive-automation-users |
| Twitter | https://twitter.com/Extensive_Auto |
| | |

**ExtensiveAutomation**  is a generic automation framework for integration, regression and end-to-end usages. The framework provided a rich and collaborative workspace environment. 
The server can run on both Python 2 and Python 3, and also run on Linux and Windows.
Note: No more support provided with Python 2!

## Installation

1. Run the following command

        python3 -m pip install extensiveautomation_server

2. Type the following command on your shell to start the server

        extensiveautomation --start

## Testing if server running

1. Please to take in consideration the following points:
	
	 - The server is running on the following tcp ports (don't forget to open these ports on your firewall):
	    - tcp/8081: REST API
	    - tcp/8081: Websocket tunnel for app client
	    - tcp/8082: Websocket tunnel for agents
	 - The `admin`, `tester` and `monitor` users are available and the default passoword is `password`. 
	 - The `Common` project is created by default, attached to the previous users.
	 - Swagger for the REST API is available in the `scripts/swagger` folder.
    
2. Checking if the REST api working fine with curl or postman.

       curl -X POST http://127.0.0.1:8081/session/login \
            -H "Content-Type: application/json" \
            -d '{"login": "admin", "password": "password"}'

## Adding plugins

Plugins allow to interact with the system to be controlled. But by default the server is provided without plugins. So you need to install them one by one according to your needs.

* [CLI plugin (ssh)](https://pypi.org/project/extensiveautomation-plugin-cli/)
* [WEB plugin (http/https)](https://pypi.org/project/extensiveautomation-plugin-web/)
* [GUI plugin (selenium, sikulix and adb)](https://pypi.org/project/extensiveautomation-plugin-gui/)
* [And many others...](https://github.com/ExtensiveAutomation/extensiveautomation-plugins-server)
