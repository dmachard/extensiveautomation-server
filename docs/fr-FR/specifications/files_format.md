---
name: Files format definition
---

# Files format

Tests files are stored in zipped XML file. 
Several types of test exists

* [Common XML structure](files_format#common-xml-structure)
* [The Test Abstract Xml](files_format#the-test-abstract-xml)
* [The Test Unit Xml](files_format#the-test-unit-xml)
* [The Test Suite Xml](files_format#the-test-suite-xml)
* [The Test Plan Xml](files_format#the-test-plan-xml)
* [The Test Global Xml](files_format#the-test-global-xml)

## Common XML structure

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
	<properties>
		<descriptions>...</descriptions>
		<inputs-parameters>...</inputs-parameters>
		<outputs-parameters>...</ outputs -parameters>
	</properties>
</file>
```
    
## The Test Abstract Xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
    <properties>...</properties>
    <teststeps>
        <steps>
            <step>
                <id>1</id>
                <description>
                    <type>string</type>
                    <value>step description</value>
                </description>
                <summary>
                    <type>string</type>
                    <value>step sample</value>
                </summary>
                <expected>
                    <type>string</type>
                    <value>result expected</value>
                </expected>
            </step>
        </steps>
    </teststeps>
    <testadapters><adapters /></testadapters>
    <testlibraries><libraries /></testlibraries>
    <testactions>
        <actions>
            <action>
                <item-id>1</item-id>
                <item-text>Start</item-text>
                <item-type>2</item-type>
                <item-data />
                <pos-y>1750.0</pos-y>
                <pos-x>2000.0</pos-x>
            </action>
        </actions>
    </testactions>
    <testaborted><aborted /></testaborted>
    <testdefinition><![CDATA[pass]]></testdefinition>
    <testdevelopment>1448190709.095677</testdevelopment>
</file>
```

## The Test Unit Xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
    <properties>....</properties>
    <testdefinition><![CDATA[pass]]></testdefinition>
    <testdevelopment>1448190694.813723</testdevelopment>
</file>
```

## The Test Suite Xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
    <properties>...</properties>
    <testdefinition><![CDATA[pass]]></testdefinition>
    <testexecution><![CDATA[pass]]></testexecution>
    <testdevelopment>1448190717.236711</testdevelopment>
</file>
```

## The Test Plan Xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
    <properties>...</properties>
    <testplan id="0">
        <testfile>
            <id>1</id>
            <color />
            <file>Common:Defaults/testunit.tux</file>
            <enable>2</enable>
            <extension>tux</extension>
            <alias />
            <type>remote</type>
            <parent>0</parent>
            <properties>....</properties>
            <description />
        </testfile>
    </testplan>
    <testdevelopment>1448190725.096519</testdevelopment>
</file>
```

## The Test Global Xml

```xml
<?xml version="1.0" encoding="utf-8" ?>
<file>
    <properties>...</properties>
    <testplan id="0">
        <testfile>
            <id>1</id>
            <color />
            <file>Common:Defaults/testplan.tpx</file>
            <enable>2</enable>
            <extension>tpx</extension>
            <alias />
            <type>remote</type>
            <parent>0</parent>
            <properties>...</properties>
            <description />
        </testfile>
    </testplan>
    <testdevelopment>1448190733.690697</testdevelopment>
</file>
```