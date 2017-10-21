---
name: Basic features
---

# Basic features

- [Log messages in your test](basic_features#log-messages-in-your-test)
- [Set the result](basic_features#set-the-result)
- [Check the syntax a test](basic_features#check-the-syntax-a-test)
- [Abort a test](basic_features#abort-a-test)

## Log messages in your test

You can log messages during the execution of your test with differents level messages:

- **info**

    ```python
    Trace(self).info(txt="hello world", bold=False, italic=False, multiline=False, raw=False)
    ```

- **warning**

    ```python
    Trace(self).warning(txt="hello world", bold=False, italic=False, multiline=False, raw=False)
    ```

- **error**

    ```python
    Trace(self).error(txt="hello world", bold=False, italic=False, multiline=False, raw=False)
    ```

    Note: if you use the `error` function, the result of your test will be always **FAILED**

## Set the result

A good testcase is defined by one or more steps in the definition part as below:

```python
self.step1 = self.addStep(
                            expected="Logged in", 
                            description="Login throught the rest api", 
                            summary="Login throught the rest api", 
                            enabled=True
                        )
self.step2 = self.addStep(
                            expected="Logged out", 
                            description="Logout from the rest api", 
                            summary="Logout from the rest api", 
                            enabled=True
                        )
```

You must set the result of each steps defined, don't forget that otherwise the result of the testcase will be UNDEFINED.
	
- Set the result to PASS:

    ```python
    self.step1.setPassed(actual="step executed as expected")
    ```

- Set the result to FAILED:

    ```python
    self.step1.setFailed(actual="error to run the step")
    ```

The test framework computes automatically the final result according to each steps.

## Check the syntax a test

Before to run a test, you can check the syntax of your test.
To do that click on the button ![](/docs/images/check_syntax.png)

## Abort a test

You can abort a test what you want, to do this use the following function

```python
Test(self).interrupt(err="aborted by tester")
```
    
When you call this function, the test is automatically aborted and the test goes to the `cleanup` part of your test

```python
def cleanup(self, aborted):
    pass
```
    
One more thing, the cleanup part function if also called at this end of your test. You can make the difference with the argument "aborted".
When the aborted argument is not empty, then this is because the abort function has been called. Also the aborted contains the error message.

An example:

```python
def definition(self):
    Test(self).interrupt("bad response received")
```

```python
def cleanup(self, aborted):
    if aborted: self.step1.setFailed(actual="%s" % aborted)
```
