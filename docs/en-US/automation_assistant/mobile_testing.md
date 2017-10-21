---
name: Mobile testing
---

# Mobile testing

* [Introduction](mobile_testing#introduction)
* [Deploy a adb agent for android](mobile_testing#deploy-a-adb-agent-for-android)
* [Interact with a android mobile](mobile_testing#interact-with-a-android-mobile)

## Introduction

This part enables to interact with mobile phone. Follow the next chapter to start the mobile agent and write a simple test.

|Action Name|Description|
|-----:|:-----|
|**Basic functions**||
|WAKE UP AND UNLOCK|Wake up and unlock the device|
|REBOOT|Reboot the device|
|SLEEP|Go to sleep|
|**Texts**||
|TYPE SHORTCUT|Type shortcut on device|
|TYPE TEXT ON XML ELEMENT|Type text on ui element|
|GET TEXT FROM XML ELEMENT|Get text from the ui element|
|**Elements**||
|CLEAR XML ELEMENT|Clear the text in the ui element|
|CLICK ON XML ELEMENT|Click on the ui element|
|LONG CLICK ON XML ELEMENT|Long click on the ui element|
|WAIT AND CLICK ON XML ELEMENT|Wait ui element to appear on mobile screen and click on it|
|**Tap**||
|CLICK TO POSITION|Click on position x,y|
|DRAG FROM POSITION|Drag from position x1,y1 to x2,y2|
|SWIPE FROM POSITION|Swipe from position x1,y1 to x2,y2|

## Deploy a adb agent for android

0. Install usb mobile drivers on your computer if missing.

1. Connect your mobile phone to your computer throught USB. Activate the debug mode and set the usb mode to `transfer files` or `MTP`

2. On the same computer, deploy the toolbox and execute it

3. Select the `adb` type, specify the name of the agent and deploy-it

4. A RSA connection warning will appears on your phone number to accept the connection. Accept the warning on the toolbox.

5. The image of the mobile phone appears on the mobile preview windows. From this preview, you can:

- See the UI content of your device with XML 
- Navigate on your device from your computer
- Retrieve a screen of your device.

    ![](/docs/images/aa_mob_preview.png)

## Interact with a android mobile

1. Connect the remote test server and from the welcome page of the client, click on the `New Mobile Test` link 

2. Select the `WAKE UP AND UNLOCK` actions to wake up the mobile device.

3. Select the `CLICK ON XML ELEMENT` and specify text with the value `Phone`. At this step, your test will be as below:

    ![](/docs/images/aa_mobile_step1.png)

4. Compose the number `#125#` as below and save the ouput in the cache

    ![](/docs/images/aa_mob_steps.png)
