#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/clean-before-run.sh

VIRTUALX_OUTPUT_FILE="$BBS_WORK_TOPDIR/log/virtual-X.out"
. $BBS_HOME/utils/start-virtual-X.sh
$BBS_HOME/BBS-run.py STAGE2 STAGE3
. $BBS_HOME/utils/stop-virtual-X.sh

# We have to use brute force because some R processes might still be running
# in the background. This will kick out the user BBS is running as!
kill -9 -1
