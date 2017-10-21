@echo off

set ADB_HOME=%~dp0

"%ADB_HOME%\adb.exe" kill-server
"%ADB_HOME%\adb.exe" -a -P 5037 fork-server server