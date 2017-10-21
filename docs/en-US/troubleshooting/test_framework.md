---
name: Test Framework
---

# Test Framework

* [Understand errors codes of the test executor (TE) ](test_framework#test-executor-errors-codes)
* [Understand errors codes for step](test_framework#step-errors-codes)
* [Understand errors codes forbreakpoint](test_framework#breakpoint-errors-codes)
* [Understand errors codes for properties](test_framework#test-properties-errors-codes)
* [Understand errors codes for validators](test_framework#test-validators-errors-codes)
* [Understand errors codes for manipulators](test_framework#test-manipulators-errors-codes)
* [Understand errors codes for operators](test_framework#test-operators-errors-codes)
* [Understand errors codes for adapters](test_framework#test-adapters-errors-codes)
* [Understand errors codes for timer](test_framework#test-timer-errors-codes)
* [Understand errors codes for state](test_framework#test-state-errors-codes)
* [Understand errors codes for template](test_framework#test-templates-errors-codes)
* [Understand errors codes for logger](test_framework#test-logger-errors-codes)

# Test executor errors codes

|Error Code|Description|
|:--------:|---------|
|ERR_TE_500|Generic error during the execution of the script.|
|ERR_TE_000|Generic error during the execution of the test.|
|ERR_TE_001|Generic error during the execution of the test case.|
|ERR_TE_002|Wrong time passed as argument in the global wait function, an integer is expected.|
|ERR_TE_003|Wrong time passed as argument in the test case wait function, an integer is expected.|

# Step errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_STP_001|Step <id> already started|
|ERR_STP_002|Step <id> cancelled|
|ERR_STP_003|Test system pause - unknown response <rsp>|
|ERR_STP_004|Test system error on pause action|
|ERR_STP_005|Step <id> not started|

# Breakpoint errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_BKP_001|Breakpoint cancelled|
|ERR_BKP_002|System breakpoint- unknown response <rsp>|
|ERR_BKP_003|System error on breakpoint action|

# Test properties errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_PRO_001|Inputs or outputs type unknown. This error can only happen when a new type exists on the client but not on the test library.|
|ERR_PRO_002|The description key passed as argument does not exists. |
|ERR_PRO_003|The agent name passed as argument does not exists. |
|ERR_PRO_004|The input passed as argument does not exists. |
|ERR_PRO_005|Input alias with the same input name. |
|ERR_PRO_006|The output passed as argument does not exists. |
|ERR_PRO_007|Output alias with the same output name. |
|ERR_PRO_008|The description key passed as argument does not exists. ERR_PRO_008 is raised only in the context of a test plan or test global|
|ERR_PRO_009|The agent name passed as argument does not exists. ERR_PRO_009 is raised only in the context of a test plan or test global|
|ERR_PRO_010|The input passed as argument does not exists. ERR_PRO_010 is raised only in the context of a test plan or test global|
|ERR_PRO_011|Input alias with the same input name. ERR_PRO_011 is raised only in the context of a test plan or test global|
|ERR_PRO_012|The output passed as argument does not exists. ERR_PRO_012 is raised only in the context of a test plan or test global|
|ERR_PRO_013|Output alias with the same output name. ERR_PRO_013 is raised only in the context of a test plan or test global|
|ERR_PRO_014|Main input alias with the same input name, raised only in the context of a test plan or test global.|
|ERR_PRO_015|Main output alias with the same output name, raised only in the context of a test plan or test global.|
|ERR_PRO_016|The project of the shared environment test does not exists or the project is not authorized for the user.|
|ERR_PRO_017|The shared environment test passed as argument does not exists.|
|ERR_PRO_018|The sub-shared environment test passed as argument does not exists.|
|ERR_PRO_019|The output passed as argument does not exists.|
|ERR_PRO_020|The input passed as argument does not exists.|
|ERR_PRO_021|The input passed as argument does not exists. ERR_PRO_021 is raised only in the context of a test plan or test global|
|ERR_PRO_022|The output passed as argument does not exists. ERR_PRO_022 is raised only in the context of a test plan or test global|
|ERR_PRO_023|Bad excel data passed on argument|
|ERR_PRO_024|Worksheet does not exists on excel file|
|ERR_PRO_025|Row or column ID are missing in excel file|

# Test validators errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_VAL_001|String validator, a string is expected on all functions.|
|ERR_VAL_002|String validator, a string is expected on all functions.|
|ERR_VAL_003|String validator, a string is expected on all functions.|
|ERR_VAL_004|String validator, a string is expected on all functions.|
|ERR_VAL_005|String validator, a string is expected on all functions.|

# Test manipulators errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_MAN_001||

# Test operators errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_OP_001|No conditions defined (AND/OR) when a list is passed as argument on the contain operator.|
|ERR_OP_002|No conditions defined (AND/OR) when a list is passed as argument on the not contain operator.|
|ERR_OP_003|An integer value is expected for the greater than operator.|
|ERR_OP_004|An integer value is expected for the greater than operator.|
|ERR_OP_005|An integer value is expected for the lower than operator.|
|ERR_OP_006|An integer value is expected for the lower than operator.|
|ERR_OP_007|An integer value is expected for the not greater than operator.|
|ERR_OP_008|An integer value is expected for the not greater than operator.|
|ERR_OP_009|An integer value is expected for the not lower than operator.|
|ERR_OP_010|An integer value is expected for the not lower than operator.|

# Test adapters errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_ADP_001|Template message expected but a bad type is passed on argument to log an event sent by an adapter.|
|ERR_ADP_002|Template message expected but a bad type is passed on argument to log an event received on the adapter.|
|ERR_ADP_003|Unable to read the template message passed on argument in the send/received events. These errors should not be happened, if it's the case, please to raise a ticket.|
|ERR_ADP_004|Unable to read the template message passed on argument in the send/received events. These errors should not be happened, if it's the case, please to raise a ticket.|
|ERR_ADP_005|Generic error raised on send/received functions. These errors should not be happened, if it's the case, please to raise a ticket.|
|ERR_ADP_006|Generic error raised on send/received functions. These errors should not be happened, if it's the case, please to raise a ticket.|
|ERR_ADP_007|Bad value passed to initialize the timer on the received function. An integer is expected.|
|ERR_ADP_008|Generic error raised during the templates comparison. This error should not be happened.|
|ERR_ADP_009|Bad type passed on the received function. A template message or a list of template message is expected.|
|ERR_ADP_010|No conditions defined (AND/XOR) on received events function. Conditions is used when several events is passed as argument. When the XOR condition is True then all events passed as argument must not be received before the timeout. When the AND condition is True then all events passed as argument must be received before the timeout.|
|ERR_ADP_011|Bad parent type. Test case expected on the initialization of the adapter|

# Test timer errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_TMR_001|Bad parent type. Adapter expected on the initialization of the timer|
|ERR_TMR_002|Integer or float expected to initialize the timer|

# Test state errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_STA_001|Bad parent type. Adapter expected on the initialization of the state|

# Test templates errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_TPL_001|Bad type on the name of template layer. Types expected: string, Unicode, Any, Starts with, Not Starts with, Ends with, Not Ends with, Contains, Not Contains, Greater Than, Lower Than, RegEx, Not RegEx, Not greater than, Not lower than|
|ERR_TPL_002|Bad type on the key name of template layer. Types expected: string, Unicode, Integer, Any, Starts with, Not Starts with, Ends with, Not Ends with, Contains, Not Contains, Greater Than, Lower Than, RegEx, Not RegEx, Not greater than, Not lower than|
|ERR_TPL_003|Bad type on the data of template layer. Types expected: string, Unicode, Integer, Any, Starts with, Not Starts with, Ends with, Not Ends with, Contains, Not Contains, Greater Than, Lower Than, RegEx, Not RegEx, Not greater than, Not lower than, Template layer|
|ERR_TPL_004|Bad type on add layer in a template message. A template layer is expected.|
|ERR_TPL_005|Unknown template layer to remove in a template message.|
|ERR_TPL_006|Template compare : list expected but %s passed on template received|
|ERR_TPL_007|Template compare : list expected but %s passed on template expected|
|ERR_TPL_008|Template compare : tuple expected but %s passed on template expected|
|ERR_TPL_009|Template compare : tuple expected but %s passed on template received|
|ERR_TPL_010|Template compare : dict expected but %s passed on template expected|
|ERR_TPL_011|Template compare : dict expected but %s passed on template received|
|ERR_TPL_012|Template incorrect: dict key unknown|
|ERR_TPL_013|Template incorrect: dict value unknown|
|ERR_TPL_014|Value unknown received %s compare with the template %s|
|ERR_TPL_015|Template compare : expected key type unknown|
|ERR_TPL_016|Template compare : not expected key type unknown|
|ERR_TPL_017|Template layer message or layer expected|
|ERR_TPL_018|Template layer name unknown|

# Test logger errors codes 

|Error Code|Description|
|:--------:|---------|
|ERR_LOG_001|Bad type passed on template comparison function. A list is expected on the template received.|
|ERR_LOG_002|Bad type passed on template comparison function. A list is expected on the template.|
|ERR_LOG_003|Bad type passed to compare templates, a tuple (key, value) is expected on the template received.|
|ERR_LOG_004|Bad type passed to compare templates, a tuple (key, value) is expected on the template.|
|ERR_LOG_005|Bad type passed to compare templates, a dictionary is expected on the template.|
|ERR_LOG_006|Bad type passed to compare templates, a dictionary is expected on the template received.|