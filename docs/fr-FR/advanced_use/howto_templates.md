---
name: How to use templates
---

# How to use templates messages

* [Purpose](howto_templates#purpose)
* [Create a template model](howto_templates#create-a-template-model)
* [Read a template message](howto_templates#read-a-template-message)

## Purpose

This page explains how to work with templates messages in your test. 

Before to start, read the [test logger](http://documentations.extensivetesting.org/docs/features/mechanism_events) page.

## Create a template model

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add the following line in the definition part of your test to create a template message

    ```python
    tpl = TestTemplates.TemplateMessage()
    ```
  
3. Add the following lines to create a template layer

    ```python
    layer = TestTemplates.TemplateLayer(name='response')
    layer.addKey(name='code', data='200')
    layer.addKey(name='msg', data='hello world')
    ```
    
4. Construct the final template message

    ```python
    tpl.addLayer(layer=layer)	
    ```
    
5. You will obtains the following template messages:

    ```
    > layer(response)
        - code: 200
        - msg: hello world
    ```

6. Save your test
    
## Read a template message

1. Open the previous test

2. Add the following lines to get the layer named `response` from a template message `tpl`:

    ```python
    layer = tpl.getLayer("response")
    ```

3. Read the value of the key `msg`

    ```python
    value = layer.get("msg")
    Trace(self).warning(value)
    ```


