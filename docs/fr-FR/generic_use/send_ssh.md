---
name: SSH Commands
---

# SSH Commands

## Introduction

Use generic tests is useful to reduce the maintenance of your tests. No knowledges in scripting are required.
Take a look to the file `/Self Testing/SYSTEM/000_System.tpx` for a complete sample.

## Execute the sample in 5 steps

1. Connect to the web interface and go the menu `Tests > Project variables` to configure test environment. 

2. Edit the variable `SAMPLE_NODE` and update the key `SSH_DEST_PWD` with the password of your test server

3. From the client, open the test `/Self Testing/SYSTEM/000_System.tpx`

4. Select the environment 

5. And run-it


## Send SSH commands

1. Create a new test plan and insert as child the test `/Snippets/Protocols/01_Send_SSH.tsx`

    ![](/docs/images/generic_ssh_testplan.png)
    
2. From the test inputs, locate the parameter `COMMANDS` and edit-it

3. This parameters enable to send ssh commands and check outputs (block of 3 lines). You can repeat this block as many times as you want.

    ![](/docs/images/generic_ssh_cmds.png)

    '''
    - line 1: description of the commands
    - line 2: the command to execute
    - line 3: check what to find on the screen (optional)
    - line 4: block separator, empty line
    '''
    
4. From the test inputs, locate the parameter `SERVERS` and select the remote server to execute ssh commands.
The server parameter must be a shared parameter (or a list of shared parameters)  with the following mandatory keys:


    - SSH_DEST_HOST
    - SSH_DEST_PORT
    - SSH_DEST_LOGIN
    - SSH_DEST_PWD

