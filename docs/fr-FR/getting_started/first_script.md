---
name: Write manually my first test 
---

# Write manually my first test 

Follow this tutorial to write your first basic test and test plan.
Read the [approach](http://documentations.extensivetesting.org/docs/features/file_type_testing) page to known the difference between test unit, test plan, etc...

- [Write a simple test unit](first_script#write-a-simple-test-unit)
- [Write a test plan](first_script#write-a-test-plan)

## Write a simple test unit

1. Click on the button ![](/docs/images/client_new_tux.png) to create a new test

2. The test is ready to use, below some explanations about this test before to run-it

    Test definition:

    - **description**: begin the test with the initialization of all steps

        ```python
        # testcase description
        self.setPurpose(purpose=description('summary'))
        self.setRequirement(requirement=description('requirement'))

        # steps description
        self.step1 = self.addStep(  
                                    expected="result expected", 
                                    description="step description", 
                                    summary="step sample", 
                                    enabled=True
                                )
        ```
        
    - **prepare**: this part enables to initialize all adapters needed for the test
    
        ```python
        pass
        ```
        
    - **definition**: actions to run according to the step defined on the description section
    
        ```python
        if self.step1.isEnabled():
            self.step1.start()
            self.step1.setPassed(actual="success")
        ```
        
    - **cleanup**: this part is called at the end of the test or when an error occurred
    
        ```python
        pass
        ```
        
    Test properties: you can read parameters in the test with the `input` function

    ![](/docs/images/client_test_properties.png)

3. The test do nothing, just initialize a fake step and run-it

4. Click on the button ![](/docs/images/client_execute.png) to execute the test.

5. Add the following input `MY_PARAM` in your test with the value `hello world`

    ![](/docs/images/client_add_param.png) 

6. Modify your test to read this input and log-it

    ```python
	if self.step1.isEnabled():
		self.step1.start()
		self.warning(input('MY_PARAM'))
		self.step1.setPassed(actual="success")
    ```

7. Run a second time your test, the message `hello world` will appears in the test events logger.

8. Save the test in the remote repository

## Write a test plan

1. Click on the button ![](/docs/images/client_new_tpx.png) to create a new test plan.

2. By default, the test plan is empty. 

    ![](/docs/images/client_testplan.png)

3. Click on the button `Insert Child` and select your test created before. 
This action will create a instance of the test previously created and imports all properties.

4. Try to run this test plan, you will see the `hello world` message  appears in the test events logger.

5. Click on the top of the treeview (`SCENARIO`) of your testplan and add the following input `MY_PARAM` in your test with the value `hello world bis`

6. Run the test, you will see the `hello world bis` message appears in the test events logger instead of the value of test unit.
As you can see, you can overwrite test inputs to change value, run the test unit several time with differents values, etc...