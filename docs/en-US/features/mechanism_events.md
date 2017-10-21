---
name: The Test Events Logger
---

# The Test Events Logger

## Introduction

Events received or sent during the execution of a test are stored in the test result by the **test logger**.
All things that happen during the execution of a test are converted to a event as `template message`. 
These events enables to make a complete analysis of what happened.

Events can be handled only by the adapters. Each adapters contains a queue to store all events.

## Do, watch and compare

The test framework of the solution is based on the following test construction:

1. **Do** an action in your test
2. **Watch** what happens until the end of a **timeout**
3. During this interval, you can **compare** a model provided by the tester with all events received.

## The template message

All events received from the SUT are converted to a template message. Below some explanations about the construction of a template message.
A template message is constructed with one or more `template layer`. A templayer layer is constructed with one ore more key/value. The value can be also a template layer.

![](/docs/images/template_message.png)

## Flexible comparison with operators

Operators can be used to compare templates messages together with a flexible approach.

|Name|Description|
|:---|:----|
|Any|Match anything|
|Contains|Check if a string contains the characters provided|
|Endswith|Check if a string ends with the characters provided|
|Startswith|Check if a string starts with the characters provided|
|GreaterThan|Check if an integer is greater than the value providede|
|LowerThan|Check if an integer is lower than the value provided|
|RegEx|Match a specific regular expression.|

An example of a template message expected by the tester:

![](/docs/images/template_expected.png)
   
