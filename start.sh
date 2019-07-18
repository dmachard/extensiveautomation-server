#!/bin/sh

# start the program
python /home/extensive/extensiveautomation --start

# tailf on process
tail -f /home/extensive/Var/Logs/output.log
