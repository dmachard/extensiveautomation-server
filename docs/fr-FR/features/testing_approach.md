---
name: The Testing Approach
---

# The Testing Approach

The solution introduces several types of tests format to cover the area of testing and experiences of testers:

![](/docs/images/testing_approach.png)

 - The **Abstract Test** (tax): used to write one test case. A test case can have several steps. This type is oriented modelisation (graphset) of testcase
 
    ![](/docs/images/tax.png)
 
 - The **Unit Test** (tux): used to write one test case. A test case can have several steps. This type is oriented development of scripts
  
    ![](/docs/images/tux.png)
    
 - The **Test Suite** (tsx): used to write several test cases. This type is oriented development of script.
  
    ![](/docs/images/tsx.png)
    
 - The **Test Plan** (tpx): used to write a scenario with the combination of test unit and/or test suite
  
    ![](/docs/images/tpx.png)
    
 - The **Global Test** Plan (tgx): used to write a scenario or matrix with the combination of test unit, test suite and/or test plan.
  
    ![](/docs/images/tgx.png)

But also some tests data formats:

 - The **Test Config (tcx)**: used to save all inputs/outputs after an export or import.
 - The **Test Data (tdx)**: used to have a set of data, can be used as an input of a test.

And test results format:

 - The **Test Result (trx)**: used to store test reports

Finally also somes basic files for developments:

 - Adapters and libraries (py): python text files used for adapters and libraries
 - Test file (txt): text files used for adapters and libraries
 
Go to **[Files format](http://documentations.extensivetesting.org/docs/specifications/files_format)** page for more details.