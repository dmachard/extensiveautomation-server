---
name: Test Properties
---

# Test Inputs

Can be used to make your test configurable. The name of a input is always in upper case and unique.

List of available type of test inputs:

|Type|Description|Usage|
|:---|:---------|:------|
|str|contains a string value||
|text|contains a text value||
|pwd|contains a string value for password||
|custom|text value with customizable variables||
|list|contains a list of string||
|bool|contains a boolean value||
|hex|contains a hexa value||
|none|contains a null value||
|alias|make a link with internal test inputs||
|shared|contains a project variables||
|list-shared|enables to get project variables and make a list||
|cache|enables to get data stored in the cache according to the key||
|int|contains a integer value||
|float|contains a float value||
|dataset|enable to embed a dataset||
|remote-image|enables to embed a remote image, select image from the remote test repository||
|local-image|enables to embed a local image, only png file||
|snapshot-image|take a screenshot and embed it||
|local-file|enables to embed a local file||
|date|value with date format ||
|time|value with time format ||
|date-time|value with date and time format||
|self-ip|contains all ips of the test server||
|self-mac|contains all mac of the test server||
|self-eth|contains all interfaces of the test server||
|json|json value||

# Test outputs

As the same of the test inputs

# Read inputs/outputs from a test

From your test, inputs or outputs can be read with the accessor `input(...)` or `output(...)`.

# Display inputs/outputs in test report

Inputs or outputs can be logged in the test report. It is can be necessary for tracabillity. 
To do that, prefix your variable with the following names

|Prefix|Purpose|
|:---|:---------|
|SUT_|Describe version of your sut|
|DATA_|Describe some important data|
|USER_|Describe personal data|

Example in test properties

![](/docs/images/inputs_sut.png)

Example in a test report

![](/docs/images/report_inputs.png)


