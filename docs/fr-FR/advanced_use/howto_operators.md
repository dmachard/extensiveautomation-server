---
name: How to use operators
---

# How to use operators

* [Purpose](howto_operators#purpose)
* [Create a template model with operators](howto_operators#create-a-template-model-with-operators)
* [Compare the template with a received message](howto_operators#compare-the-template-with-a-received-message)

## Purpose

This page explains how to use operators with templates messages in your test. 

Before to start, read the [test logger](http://documentations.extensivetesting.org/docs/features/mechanism_events#flexible-comparaison-with-operators) page.

## Create a template model with operators

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. Add the following line in the definition part of your test to create a template message

    ```python
    tpl = TestTemplates.TemplateMessage()
    ```
  
3. Add the following lines to create a template layer with operators

    ```python
    layer = TestTemplates.TemplateLayer(name='response')
    layer.addKey(name='code', data=TestOperators.LowerThan(x=500))
    layer.addKey(name='msg', data=TestOperators.Contains(x="hellow"))
    ```
    
4. Construct the final template message

    ```python
    tpl.addLayer(layer=layer)	
    ```
    
5. You will obtains the following template messages:

    ```
    > layer(response)
        - code: **LowerThan**(500)
        - msg: **Contains**(hello world)
    ```

6. Save your test

## Compare the template with a received message.

1. Initialize the adapter in the prepare section

    ```python
    self.ADP_DUMMY = SutAdapter.Adapter(parent=self, debug=input('DEBUG'))
    ```
    
2. In the definition part, generate one fake event received from the sut

    ```python
    tpl = TestTemplates.TemplateMessage()
    layer = TestTemplates.TemplateLayer(name='response')
    layer.addKey(name='code', data='200')
    layer.addKey(name='msg', data='hello world')
    tpl.addLayer(layer=layer)	
    
    self.ADP_DUMMY.logRecvEvent( "fake event", tpl )
    ```
    
3. Add the following lines to make the comparison with operators

    ```python
    evt = self.ADP_DUMMY.received( expected = layer, timeout = input('TIMEOUT') )
    if evt is not None:
        Trace(self).error("no event match")				
    ```
            
4. Execute the test, go the the events windows and locate match events in the list.

    ![](/docs/images/template_events_match.png)

5. Click on the event to load the compare windows, on the left you will see the received message and on the right the expected template.

    ![](/docs/images/templates_compare.png)
    
    The legend for colors:
    
        - green:    match
        - yellow:   not yet tested
        - red:      mismath



