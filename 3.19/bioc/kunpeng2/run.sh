#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/clean-before-run.sh

$BBS_PYTHON_CMD $BBS_HOME/BBS-run.py no-bin

# We have to use brute force because some R processes might still be running
# in the background. This will kick out the user BBS is running as!
sleep 60  # wait 1 min before the kill
kill -9 -1