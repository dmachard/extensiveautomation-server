---
name: Add adapter
---

# Development guide to add a new adapter

* [Create a new package of adapters](new_adapter#create-a-new-package-of-adapters)
* [Add an adapter](new_adapter#add-an-adapter)
* [Create the online documentation](new_adapter#create-the-online-documentation)
* [Test your adapter](new_adapter#test-your-adapter)

## Create a new package of adapters

1. From the client, go the adapter repository `Modules Listing > Adapters`

2. Select the set to adapters where you want to add a new adapter. 

    ![](/docs/images/client_adapters.png)
    
3. Right click on it and click on the menu `Add Adapter` . Set the name of your adapter with the value `Example`.

    ![](/docs/images/adapter_name.png)

4. Generate the adapter's package by clicking on `OK`, the package will appears on the tree with a init default file

    ![](/docs/images/adapters_listing.png)

5. Edit the init file of the set of adapters. 

    ![](/docs/images/adapters_init.png)

6. Reach the end of the file and add the following lines. Change the name of the import with the name of your adapter. This two lines are necessary to enable the automatic generation of the online documentations.
    
    ```python
    import Example
    __HELPER__.append("Example") 
    ```
    
## Add an adapter

1. From the workspace, click on the button ![](/docs/images/new_adapter.png) to add a adapter. A adapter is provided by default named `MyAdapter`.

The Python language is used to develop adapter.

    ```python
    class MyAdapter(TestAdapter.Adapter):
    ```
  
2. Got the end of the file and add the following function to your adapter:

    ```python
	def hello(self):
		"""
		Log a hello world message
		"""
		self.warning("hello world")
    ```
    
3. Save the file with the name `myexample`. Choose the folder created previously as destination.

    ![](/docs/images/adapter_class.png)

4. Edit the file `init` and add the following line on the beginning, after the header.
    
    ```python
    from client import *
    ```

5. Save your file.

## Create the online documentation

1. Edit the `init` file of your adapter's package

2. Configure the variable `__DESCRIPTION__` to add a description

    ```python
    __DESCRIPTION__ = "Description of my first adapter"
    ```
3. Configure the variable `__HELPER__` as below, this variable enables to list functions to add on the assistant.

    ```python
    __HELPER__ =    [
                        ("MyAdapter", ["__init__", "hello"])
                    ]
    ```
    
4. Save the change.

5. Finally, click on the following button 
    
    ![](/docs/images/client_assistant.png). 
    
    After the generation, your adapter will appears on the list like below

    ![](/docs/images/client_assistant_adapters.png)

## Test your adapter

1. Create a basic test unit ![](/docs/images/client_tux.png) and try to import your new adapter as below:

    1. Initialize the adapter in the `prepare` section
    
        ```python
        def prepare(self):
            self.ADP_EXAMPLE = SutAdapters.Example.MyAdapter(parent=self, debug=input('DEBUG'))
        ```
  
    2. Call the function `hello` of the adapter in the `definition` section as below:
    
        ```python
        def definition(self):
            self.ADP_EXAMPLE.hello()
        ```
5. Run the test, the hello message should appears.

    ![](/docs/images/client_result_events.png)
