#!/bin/sh

# start the program
python /home/extensive/extensiveautomation.py --start

# tailf on process
tail -f /home/extensive/ea/var/logs/output.log
