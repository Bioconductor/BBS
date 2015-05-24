#!/bin/bash

. ./config.sh

. $BBS_HOME/utils/clean-before-run.sh
. $BBS_HOME/nodes/$BBS_NODE/start-virtual-X.sh
$BBS_HOME/BBS-run.py no-bin
. $BBS_HOME/nodes/$BBS_NODE/stop-virtual-X.sh

# We have to use brute force because some R processes might still be running
# in the background. This will kick out the user BBS is running as!
# Note that there is a Solaris-specific pb with the bbs.jobs.runJob() function
# (see source of the jobs module for more details).
kill -9 -1
