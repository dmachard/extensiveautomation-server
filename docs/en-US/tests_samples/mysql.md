---
name: MySQL example
---

# MySQL example

* [Introduction](mysql#introduction)
* [Adapter configuration](mysql#adapter-configuration)
* [Make connection and disconnection](mysql#make-connection-and-disconnection)
* [Execute sql query](mysql#execute-sql-query)

## Introduction

This sample show how to use the MySQL client adapter. 
The following explanations are based on the sample available on `/Samples/Tests_Adapters/15_Database.tsx`

## Adapter configuration

1. Configure your adapter in the prepare section of your test

    ```python
    self.ADP_MYSQL = SutAdapters.Database.MySQL(
                                            parent=self, 
                                            host=input('HOST_DST'), 
                                            user=input('MYSQL_LOGIN'),
											password=input('MYSQL_PWD'), 
                                            debug=input('DEBUG'), 
                                            verbose=input('VERBOSE'),
											agent=agent('AGENT_DB'), 
                                            agentSupport=input('SUPPORT_AGENT')
                                        )
    ```
    
    with the following parameters

    |Input|Type|Value|
    |:---|---:|:----:|
    |DEBUG|boolean|False|
    |VERBOSE|boolean|False|
    |MYSQL_LOGIN|string|admin|
    |MYSQL_PWD|string|admin|
    |HOST_DST|string|192.168.1.1|
    |SUPPORT_AGENT|boolean|False|

## Make connection and disconnection

1. In the definition part, copy/paste the following lines to make connection. You need to provide the database

    ```python
    self.ADP_MYSQL.connect(dbName=input('MYSQL_DB'), timeout=input('TIMEOUT'))
    ```
    
2. Copy/paste the following line to make a disconnection from your machine

    ```python
    self.ADP_MYSQL.disconnect()
    ```
    
## Execute sql query

1. Copy/paste the following lines to execute a sql query in the table.

    ```python
    query = 'SELECT id FROM `%s-users` WHERE login="admin"' % input('TABLE_PREFIX')
    self.ADP_MYSQL.query(query=query)
    rsp = self.ADP_MYSQL.hasReceivedRow(timeout=input('TIMEOUT'))
    ```