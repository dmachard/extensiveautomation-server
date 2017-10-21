---
name: How to use agents
---

# How to use agents

* [Purpose](howto_agents#purpose)
* [Configure adapters with agents](howto_agents#configure_adapters_with_agents)

## Purpose

The adapters can be used in agent mode. When this mode is activated, the adapter no more interacts in direct with the SUT but throught the agent configured.

Go to the [Sut Adapters](http://documentations.extensivetesting.org/docs/extensions/adapters) page to see which adapters can be used with an agent. 

## Configure adapters with agents

1. Connect your adapter to a agent, to do that go to the test properties and right click to add a new key.
Select the desired agent from the combolist. Add a parameter `SUPPORT_AGENT`, this parameter can be used to disable the agent mode.

    ![](/docs/images/client_properties_agent.png)

    ![](/docs/images/client_agent_support.png)
    
2. Modify the adapter to use this agent as below

    ```python
    agentSupport=input('SUPPORT_AGENT'), 
    agent=agent('AGENT_SOCKET')
    ```

    ```python                          
    self.ADP_REST= SutAdapters.REST.Client(
                                            parent=self,
                                            destinationIp=input('HOST'),
                                            destinationPort=input('PORT'),
                                            debug=input('DEBUG'),
                                            sslSupport=input('USE_SSL'),
                                            agentSupport=input('SUPPORT_AGENT'), 
                                            agent=agent('AGENT_SOCKET')
                                            )
    ```
    
3. From the test events logger, a new layer is added when you running in agent mode

    ![](/docs/images/client_events_logger_agent.png)    
