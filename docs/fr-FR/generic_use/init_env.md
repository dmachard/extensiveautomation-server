---
name: Test environment definition
---

# Test environment definition

* [Purpose](init_env#purpose)
* [Environment Json structure](init_env#environment-json-structure)
* [Server Json structure](init_env#server-json-structure)
* [Describe a test environment](init_env#describe-a-test-environment)

## Purpose

Before to start to write your test or campaign of tests, prepare and declare your test environment throught the web interface.
The test environment describes:

 - all tests servers with ip, port, login, password and more
 - all data needed as input for your test.

The test environment will be executed as prerequisites in your test plan. Your test environment content is available from the cache.


## Environment Json structure

This variable must be contains the two following keys:

- `PLATFORM`: contains the list of servers available in your test environment
- `DATASET`: contains the test data to use in your tests


```json
{
    "PLATFORM": {
        "<CLUSTER_NAME>": [
            {
                "<SVR_NAME>": "<PROJECT_NAME>:<VARIABLE_NAME>"
            }
        ]
    },
    "DATASET": [
        {
            "<DATA_NAME>": "<PROJECT_NAME>:<VARIABLE_NAME>"
        }
    ]
}
```

## Server Json structure

This variable must be contains the two following keys:

- `COMMON`: main parameters of your server like hostname, main ip, etc.
- `INSTANCES`: contains all instances available (http, ssh, mysql, etc.) in the server 


```
{
    "COMMON": {
        "HOSTNAME": "extensivetesting",
        "SSH_DEST_HOST": "....",
        "SSH_DEST_PORT": 22,
        "SSH_DEST_LOGIN": "root",
        "SSH_DEST_PWD": "xxxxxx",
        "SSH_PRIVATE_KEY": null,
        "SSH_PRIVATE_KEY_PATH": null,
        "SSH_AGENT_SUPPORT": false,
        "SSH_AGENT": {
            "type": "ssh",
            "name": "agent.win.example01"
        }
    },
    "INSTANCES": {
        "<INSTANCE_TYPE>": {
            "<INSTANCE_NAME>": {}
        },
        "<INSTANCE_TYPE>": {
            "<INSTANCE_NAME>": {
                "HTTP_DEST_HOST": "127.0.0.1",
                "HTTP_DEST_PORT": 8090,
                "HTTP_DEST_SSL": false,
                "HTTP_AGENT_SUPPORT": false,
                "HTTP_AGENT": {
                    "type": "socket",
                    "name": "agent.socket01"
                }
            }
        }
    }
}
```

## Describe a test environment

1. Connect to the web interface and go the menu `Tests > Project variables`

2. Edit the variable SAMPLE_ENVIRONMENT

3. From the client, create a new test plan and insert the snippet `/Snippets/Do/03_Initialize.tux`

4. From test inputs, locate the parameter `ENVIRONMENT` and select the varaible configured on previous step

5. Execute the test, you can see all data available in the cache

    ![](/docs/images/snippets_env_cache.png)
    