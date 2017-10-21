---
name: Web testing
---

# Web testing

* [Introduction](web_testing#introduction)
* [Write a test](web_testing#write-a-test)
* [Use the internal web browser](web_testing#use-the-internal-web-browser)
* [Use the Selenium IDE plugin](web_testing#use-the-selenium-ide-plugin)

## Introduction

This part enables to interact with web browsers.
Deploy a `selenium-server` agent before to start this procedure, follow the [first usage](http://documentations.extensivetesting.org/docs/toolbox_deployment/first_connection) page to deploy this type of agent.
Follow the next chapter to write a simple test.

|Action Name|Description|
|-----:|:-----|
|**Browser**||
|OPEN BROWSER|Open browser on the desktop and load the url|
|CLOSE BROWSER|Close the current browser on the desktop|
|MAXIMIZE BROWSER|Maximize the browser|
|**Actions**||
|REFRESH PAGE|Refresh the current page|
|GO BACK|Go back|
|GO FORWARD|Go forward|
|ACCEPT ALERT|Accept the javascript alert|
|DISMISS ALERT|Dismiss the javascript alert|
|CLOSE WINDOW|Close the current window|
|SWITCH TO NEXT WINDOW|Switch to the next window|
|SWITCH TO FRAME|Switch to the frame|
|**Elements**||
|WAIT HTML ELEMENT|Wait html element to appear on the page|
|WAIT AND CLICK ON HTML ELEMENT|Wait html element to appear on the page and click on it|
|HVOER ON HTML ELEMENT|Move the mouse on the html element|
|CLICK ON HTML ELEMENT|Click on the html element|
|DOUBLE CLICK ON HTML ELEMENT|Double click on the html element|
|CLEAR TEXT ON HTML ELEMENT|Clear the text on the html element|
|SELECT ITEM BY TEXT|Select item according to the text (for combolist or list)|
|SELECT ITEM BY VALUE|Select item according to the value attribute (for combolist or list)|
|**Text**||
|GET TEXT ALERT|Get the text in the javascript alert|
|GET TEXT FROM HTML ELEMENT|Get the text of the html element|
|GET PAGE TITLE|Get the title of the web page|
|GET PAGE URL|Get the url|
|GET PAGE CODE SOURCE|Get the source of the web page|
|**Keyboards**||
|TYPE KEYBOARD SHORTCUT|Type key shorcut on html element|
|TYPE TEXT ON HTML ELEMENT|Type text on html element|

## Write a test

1. Connect the remote test server and from the welcome page of the client, click on the `New Web Test` link 

2. Select the `OPEN BROWSER` action and specify the browser type to use and the url to load

    ![](/docs/images/aa_web_step1.png)

3. Add the `MAXIMIZE BROWSER` action to your test (this step is optional)

4. Select the `TYPE TEXT ON HTML ELEMENT`, specify the name of the element `q` and the text to type `extensive testing`

    ![](/docs/images/aa_web_step1.png)

5. Select the `WAIT HTML ELEMENT` action, search the element `BY ID` and specify the value `resultStats`

6. Select the `GET TEXT FROM HTML ELEMENT` action to retrieve the value and save it in the cache.

7. Add the `LOG MESSAGE` from framework action to display the text in log. Your test will be as below

    ![](/docs/images/aa_web_step3.png)

9. Finally, select the `CLOSE BROWSER` action to terminate your test.

## Use the internal web browser

You can use the internal web browser to find html elements more easily and preload elements in the automation assistant.
The browser can be opened from the the `OPEN BROWSER` action

![](/docs/images/aa_web_browser.png)

Loads the web site and make right click on the page to show the html element id, you can also read the code source 

## Use the Selenium IDE plugin

Install and use the plugin `Selenium IDE` to import user actions and generate automatically the test for the automation assistant.
