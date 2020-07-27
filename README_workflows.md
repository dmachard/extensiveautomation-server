# Workflows

Documentations for default workflows.
a workflow is the combination of differents [actions](https://github.com/ExtensiveAutomation/extensiveautomation-server/blob/master/README_actions.md#actions).

## Table of contents
* [basic/helloworld.yml](#basichelloworldyml)
* [basic/wait.yml](#basicwaityml)
* [generator/random.yml](#generatorrandomyml)

## basic/helloworld.yml

This workflow shows how to write a simple workflow with one action. 
A workflow is made up of two parts:
- property parameters
- actions list to execute

Property parameters override the parameters on each actions if the name is the same.
Conditions between actions can be defined too.

1. In the actions part, add the `description` of your action

```yaml
actions:
- description: HelloWorld
```

2. Add the path of the action

```yaml
  file: Common:actions/basic/helloworld.yml
```

3. Overwrite parameters (optional)

```yaml
  parameters:
   - name: msg
     value: Hola Mundo
```
     
## basic/wait.yml

This workflow shows how to call the `wait.yml` action by 
overriding the duration parameter.

## generator/random.yml

This workflow shows how to call two actions one after the other
