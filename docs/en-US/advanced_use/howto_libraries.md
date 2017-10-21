---
name: How to use libraries
---

# How to use libraries

* [Purpose](howto_libraries#purpose)
* [Use libraries in your test](howto_libraries#initialize-libraries-in-your-test)

## Purpose

The libraries enables to make small actions like decode or encode an XML message, make compression, etc...
If several adapters make the same functions, it will be interesting to factory the code thanks to the library.

Go to the [Sut Libraries](http://documentations.extensivetesting.org/docs/extensions/libraries) page to see the complete list of all availables libraries. 

You can also add new one if missing, follow the [development guide](http://documentations.extensivetesting.org/docs/personalizations/new_library) to do that.


## Use libraries in your test

1. Add your library, in the `prepare` section, below an example with the hashing library. 
You can use the online assistant to see how to configure your library.

    ```python
    self.LIB_SHA1 = SutLibraries.Hashing.SHA1(
                                                parent=self, 
                                                debug=input('DEBUG')
                                            )
    ```
    
2. Run the test and log the output of the library.

    ```python
    hash_pwd = self.LIB_SHA1.compute(data=input('PASSWORD'), hexdigit=True)
    Trace(self).warning(hash_pwd)
    ```
 