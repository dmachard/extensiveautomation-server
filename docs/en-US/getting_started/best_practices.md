---
name: Best practices
---

# Best practices

- [Kept the readability of your tests](best_practices#kept-the-readability-of-your-tests)
- [Always define steps](best_practices#always-define-steps)
- [Always use of the test properties](best_practices#always-use-of-the-test-properties)

## Kept the readability of your tests

As Python is used to write tests, don't use the try/except! Exceptions are handled by the test framework.

## Always define steps 

Steps must be always exists on your test because these are used to generate a test report.
So take the time to write properly each steps of your test. Example below:

```python
# steps description
self.step1 = self.addStep(
                            expected="Test final verdict retrieved", 
                            description="Get the verdict of a test", 
                            summary="Get the verdict of a test", 
                            enabled=True
                        )
```

```python 
if self.step1.isEnabled():
    self.step1.start()
        
    (... your test ...)
    
    self.step1.setPassed(actual="success")
```
    
## Always use of the test properties

Don't write values in hard in your test, instead of that use the test properties