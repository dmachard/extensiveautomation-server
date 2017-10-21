---
name: Shell Recorder
---

# Shell Recorder

* [Introduction](shell_recorder#introduction)
* [How to install it?](shell_recorder#how-to-install-it)
* [How to use it?](shell_recorder#how-to-install-it)
* [Editing tools](shell_recorder#editing-tools)

## Introduction

The shell recorder plugin is designed for easily importing a sequence of shell commands directly in Extensive Testing to convert it into a test unit.
This allows the user to replay that sequence as he wishes thanks to ExtensiveTesting.

This plugin aims to be the most user-friendly possible to be accessible to people without knowledge in python or even without knowledge in shell at all.

![](/docs/images/plugin_shell_recorder.png)


## How to install it

Like all the other Extensive Testing plugins, simply copy the shell-recorder directory in the plugins directory of your Exensive Testing installation.
At Extensive Testing launch, the shell recorder plugin will be automatically available along with the other installed plugins.

Once logged in, the plugin is available to use at anytime.

## How to use it

The first step is to obtain the shell sequence to be imported.
If it comes from a putty terminal, you can get it from the `Copy all to clipboard` option provided by putty.

In the shell recorder plugin, you can then click on the `Read from clipboard` button to get it.

If the sequence is already in a text file, you can click on the `Read from file` button.

You can then modify the sequence by using various tools described further, or, after having filled in the IP address, login and password parameters, directly import it thanks to the `Import in Extensive Testing` button.

## Editing tools

### Add, erase or change a prompt

The plugin relies on detecting the shell prompts to parse the commands and outputs.
So, it is crucial that they are well detected. If this is not the case, the plugin offers the possibility of manually modifying and erasing the detected prompts if necessary, or adding yours.
All these operations take place in the `detected prompts table`. 

WARNING: Any of these operations will result to a complete reset of the parsing. So any prior editing operations done to the sequence will be lost and will have to be redone.

To modify a detected prompt simply double-click on it in the table.
To erase a prompt, click on it to select it and then, either press the `DEL` key or right-click and click on `Erase selected prompt` in the rigt-click menu.
To add a new prompt, right-click on the table and click on "Insert new prompt". A new line appears. Doucble-click on it to edit it and enter your prompt to be detected.

### Select and filter the expected output

It is possible to filter the output of a command by selecting the text you want to expect as an output in the text view.
When you select some text, it is highlighted (colored in orange) and the rest is ignored (background colored in grey).

It is possible to do the same operation directly in the top table by editing the correponding cell and inserting the text you want as an output in it.

### Modify a command or the expected output

The same things can be done with a command: selection and cell edition.
If when editing, you enter text not matching anything in the original command, it will replace it totally.

All the text, commands and outputs, can be edited directly in the text view by double-clicking on the text to edit.
To go out of the edition mode and save the eventual changes, double-click again outside of the edited area.

### Insert a command

A new command (and its correponding output) can be inserted by right-clicking in the table view and click on "Insert line above" in the right-click menu.
This will result in the creation of a new command and its corresponding output with "[TBD]" as a value.
You will then need to edit it to enter your own values.