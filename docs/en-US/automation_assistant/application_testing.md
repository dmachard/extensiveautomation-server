---
name: Application testing
---

# Application testing

* [Introduction](application_testing#introduction)
* [Take the control of the keyboard](application_testing#take-the-control-of-the-keyboard)
* [Detect visual pattern on screen](application_testing#detect-visual-pattern-on-screen)
* [Detect word on screen](application_testing#detect-word-on-screen)
* [Take the control of the mouse](application_testing#take-the-control-of-the-mouse)

## Introduction

This part enables to interact with applications in your Windows environnement.
Deploy a `sikulix-server` agent before to start this procedure, follow the [first usage](http://documentations.extensivetesting.org/docs/toolbox_deployment/first_connection) page to deploy this type of agent.
Follow the next chapter to write a simple test to simulate keyboard, move the mouse, detect visual patterns and words on the screen.

|Action Name|Description|
|-----:|:-----|
|**Mouse**||
|CLICK ON POSITION|Click on the position (x,y)|
|DOUBLE CLICK ON POSITION|Double click on the position (x,y)|
|RIGHT CLICK ON POSITION|Right click on the position (x,y)|
|MOUSE WHEEL DOWN|Mouse wheel down|
|MOUSE WHEEL UP|Mouse wheel up|
|MOVE TO POSITION|Move to the position (x,y)|
|**Keyboard**||
|TYPE TEXT|Simulate keyboard and type text|
|TYPE PATH|Simulate keyboard and type text path|
|TYPE PASSWORD|Simulate keyboard and type password|
|GET TEXT FROM CLIPBOARD|Get text from clipboard|
|KEYBOARD SHORTCUT|Simulate keyboard interactions|
|**Words**||
|CLICK ON WORD|Detect the word on the screen and click on it|
|DOUBLE CLICK ON WORD|Detect the word on the screen and double click on it|
|RIGHT CLICK ON WORD|Detect the word on the screen and right click on it|
|WAIT WORD|Search the word until it appears|
|WAIT AND CLICK ON WORD|Search the word until it appears and click on it|
|**Images**||
|CLICK ON IMAGE|Detect the visual pattern on the screen and click on it|
|DOUBLE CLICK ON IMAG|Detect the visual pattern on the screen and double click on it|
|RIGHT CLICK ON IMAGE|Detect the visual pattern on the screen and right click on it|
|WAIT IMAGE|Search the visual pattern until the image appears|
|WAIT AND CLICK ON IMAGE|Search the visual pattern until the image appears and click on it|
|HOVER MOUSE ON|Detect the visual pattern on the screen and mouve the cursor on it|
|DRAG IMAGE AND DROP TO|Detect the visual pattern on the screen and drop it to the position (x,y)|

## Take the control of the keyboard

1. Connect the remote test server and from the welcome page of the client, click on the `New Application Test` link 

2. Select the `KEYBOARD SHORTCUT` and configure-it `WIN+R` keys, choose the `WIN` value in the first combolist and the letter `R` in the latest combo.

3. Choose the `TYPE TEXT` and configure-it with the value `notepad`

4. Choose `KEYBOARD SHORTCUT` and configure-it with the `ENTER` value (latest column). At this step you have the following steps in your test.

    ![](/docs/images/aa_app_steps1.png)

5. To continue this test, we will maximize the notepad windows. Select the `KEYBOARD SHORTCUT` and configure-it `ALT+space` keys and add this action in your test

6. Choose `KEYBOARD SHORTCUT` again and configure-it with the `DOWN` action and repeat-it 4 times.

7. Choose `KEYBOARD SHORTCUT` and configure-it with the `ENTER` value. At this step you have the following steps in your test.

    ![](/docs/images/aa_app_steps2.png)

8. Add the three following steps in your test to open a specific text file.

    ![](/docs/images/aa_app_steps3.png)

## Detect visual pattern on screen

1. Connect the remote test server and from the welcome page of the client, click on the `New Application Test` link 

2. Select the `WAIT AND CLICK ON IMAGE` action. Click on the button "Capture Visual Pattern" and press `Ctrl+F1` when you are ready to capture a region of your screen.

    ![](/docs/images/aa_app_img1.png)

3. Type the text "calc" and simulate the key `ENTER` to validate.

    ![](/docs/images/aa_app_img2.png)

4. Add the following steps as below, capture each images for `1 + 2 =`

    ![](/docs/images/aa_app_img3.png)
 
5. Simulate the keys `CTRL+C` to put the result in the clipboard

6. Select the `GET TEXT FROM CLIPBOARD` action and specify the key to save the content in the cache

    ![](/docs/images/aa-app-clipboard.png)

7. Finally, check the value saved in the cache by using the basic `CHECKING IF VALUE` action

    ![](/docs/images/aa_app_img4.png)

## Detect word on screen

1. Connect the remote test server and from the welcome page of the client, click on the `New Application Test` link 

2. Select the `WAIT WORD` action and specify the word to find on the screen. You can also configure the area to make the research of this word. Don't hesitate to provide this area to improve the find.

    ![](/docs/images/aa_app_word1.png)

3. Configure your test as below and execute-it

    ![](/docs/images/aa_app_word2.png)

## Take the control of the mouse

1. Connect the remote test server and from the welcome page of the client, click on the `New Application Test` link 

2. Select the `CLICK ON POSITION` action. Click on the button `Capture Mouse Positin` and press `Ctrl+F1` when you are ready to capture the position of your mouse.

3. Select the `MOVE TO POSITION` action and configure-it as before.

4. Select the `MOUSE WHEEL UP` and specify the number of run to execute

    ![](/docs/images/aa_app_mouse.png)