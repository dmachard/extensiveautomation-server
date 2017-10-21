---
name: Introduction
---

# Introduction

## Testing with snippets approach

Use generic tests is useful to reduce the maintenance of your tests. No knowledges in scripting are required.
Use these tests is strongly recommended.

## Available test snippets

|Test Name|Description|
|:---|:---------|
|**Do**||
|/Snippets/Do/01_Wait.tux|Make a pause in your test|
|/Snippets/Do/02_Terminate.tux|Abort a test from a testplan or testglobal|
|/Snippets/Do/03_Initialize.tux|Prepare data for your test|
|**Cache Framework**||
|/Snippets/Generic/00_Set_Cache.tux|Add key/value on cache|
|/Snippets/Generic/01_Log_Cache.tux|Display value during the execution of a test according to the key provided|
|/Snippets/Generic/03_Reset_Cache.tux|Remove all key and values from the cache|
|/Snippets/Generic/04_Checking_Cache.tux|Check a value according to the key provided, regex supported|
|/Snippets/Generic/05_Delete_Cache.tux|Delete a value according to the key provided|
|**Network Protocols**||
|/Snippets/Generic/01_Send_SSH.tsx|Enable to send system command though ssh and check result|
|/Snippets/Generic/02_Send_HTTP.tsx|Enable to send http request and check responses with regexp|
|/Snippets/Generic/03_Send_XML.tsx|Enable to send http request with soap content, xpath and regexp are used to check responses|
|/Snippets/Generic/04_Send_JSON.tsx|Enable to send http request with json content, jsonpath and regexp are used to check responses|
|**Generators**||
|/Snippets/Generic/12_Gen_Sha.tux|Generate a sha hash|
|/Snippets/Generic/13_Gen_Md5.tux|Generate a md5 hash|
|**User Interface**||
|/Snippets/UI/01_Win_OpenApp.tux|Open an application on Window|
|/Snippets/UI/02_Win_CloseApp.tux|Close an application on Window|
|/Snippets/UI/03_OpenBrowser.tux|Open a firefox, chrome or internet explorer browser|
|/Snippets/UI/04_CloseBrowser.tux|Close the browser|
|/Snippets/UI/05_MaximizeBrowser.tux|Maximize the browser|
|**Verify**||
|/Snippets/Verify/01_Check_XML.tux|Use xpath and regexp to find specific data|
|/Snippets/Verify/01_Check_JSON.tux|Use jsonpath and regexp to find specific data|