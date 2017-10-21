---
name: How to use server CLI
---

# How to use the CLI

* [Purpose](howto_cli#purpose)
* [Run a test](howto_cli#run-a-test)

## Purpose

A basic CLI is available in the test server through SSH, this CLI enables to make simple actions as run a test.

## Run a test

1. Connect as root throught SSH on your test server

2. Execute the following command

```bash
[root@xtc ~]# xtctl run Common:/Basics/Do/Wait.tux
SUCCESS
```