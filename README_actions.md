# Actions

Documentations for default actions.

An action is individual python code source with enriched parameters.

## Table of contents
* [basic/helloworld.yml](#basichelloworldyml)
* [basic/wait.yml](#basicwaityml)
* [cache/log.yml](#cachelogyml)
* [generator/random_string.yml](#generatorrandom_stringyml)
* [generator/random_integer.yml](#generatorrandom_integeryml)
    
## basic/helloworld.yml

This action shows how to write a simple action. 
A action is made up of two parts:
- property parameters
- python code
Parameters can be read from the python code with the function `input`.

1. Write properties of your actions

```yaml
properties:
  parameters:
   - name: msg
     value: hello world
```

2. In the `python` part, you need to create a class inherit from `Action`.

```python
class HelloWorld(Action):
```

3. Create the `definition` function.
The second line show how to get a parameter from properties and log-it.

```python
def definition(self):
    self.info(input("msg")))
```

4. Finally, you must instanciate the class and call the `execute()` function:

```python
HelloWorld().execute()
```

## basic/wait.yml

Do nothing during x second(s).

Parameter(s):
- duration: number of second to wait

## cache/log.yml

Log entry from cache.

Parameter(s):
- key (integer): name of the entry to log

## generator/random_string.yml

Generate a random string

Parameter(s):
- string-length (integer): number of characters
- with-lower-case (boolean): generate using lower-case (a,b,...)
- with-upper-case (boolean): generate using upper-case (A,B,...)
- with-punctuation (boolean): generate using punctuation (!,?,...)
- cache-key (string): name of the random string to save-it in the cache

## generator/random_integer.yml

Generate a random integer

Parameter(s):
- min-interval (integer): minimun interval to generate the number
- max-interval (integer): maximun interval to generate the number
- cache-key (string): name of the random integer to save-it in the cache
