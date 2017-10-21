---
name: Add library
---

# Development guide to add a new library

* [Create a new package of libraries](new_library#create-a-new-package-of-libraries)
* [Add a library](new_library#add-an-library)
* [Create the online documentation](new_library#create-the-online-documentation)
* [Test your library](new_library#test-your-library)

## Create a new package of libraries

1. From the client, go the library repository `Modules Listing > Libraries`

2. Select the set to libraries where you want to add a new library. 

    ![](/docs/images/client_libraries.png)
    
3. Right click on it and click on the menu `Add Library` . Set the name of your library with the value `Example`.

    ![](/docs/images/library_name.png)

4. Generate the library's package by clicking on `OK`, the package will appears on the tree with a init default file

    ![](/docs/images/libraries_listing.png)

5. Edit the init file of the set of libraries. 

    ![](/docs/images/libraries_init.png)

6. Reach the end of the file and add the following lines. Change the name of the import with the name of your library. This two lines are necessary to enable the automatic generation of the online documentations.
    
    ```python
    import Example
    __HELPER__.append("Example")
    ```
    
## Add an library

1. From the workspace, click on the button ![](/docs/images/new_library.png) to add a MyLibrary. A MyLibrary is provided by default named `MyLibrary`.

The Python language is used to develop MyLibrary.

    ```python
    class MyLibrary(TestLibrary.Library):
    ```
  
2. Got the end of the file and add the following function to your MyLibrary:

    ```python
	def hello(self):
		"""
		Log a hello world message
		"""
		self.warning("hello world")
    ```
    
3. Save the file with the name `myexample`. Choose the folder created previously as destination.

    ![](/docs/images/library_class.png)

4. Edit the file `init` and add the following line on the beginning, after the header.
    
    ```python
    from client import *
    ```

5. Save your file.

## Create the online documentation

1. Edit the `init` file of your MyLibrary's package

2. Configure the variable `__DESCRIPTION__` to add a description

    ```python
    __DESCRIPTION__ = "Description of my first MyLibrary"
    ```
3. Configure the variable `__HELPER__` as below, this variable enables to list functions to add on the assistant.

    ```python
    __HELPER__ =    [
                        ("MyLibrary", ["__init__", "hello"])
                    ]
    ```
    
4. Save the change.

5. Finally, click on the following button 
    
    ![](/docs/images/client_assistant.png). 
    
    After the generation, your library will appears on the list like below

    ![](/docs/images/client_assistant_libraries.png)

## Test your library

1. Create a basic test unit ![](/docs/images/client_tux.png) and try to import your new library as below:

    1. Initialize the library in the `prepare` section
    
        ```python
        def prepare(self):
            self.LIB_EXAMPLE = SutLibraries.Example.MyLibrary(parent=self, debug=input('DEBUG'))
        ```
  
    2. Call the function `hello` of the library in the `definition` section as below:
    
        ```python
        def definition(self):
            self.LIB_EXAMPLE.hello()
        ```
5. Run the test, the hello message should appears.

    ![](/docs/images/client_result_events_lib.png)
