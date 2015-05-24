#!/bin/bash
# ======================
# Settings for gladstone
# ======================



#set -x # Print commands and their arguments as they are executed.

#export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="gladstone"


# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"


# Needed only on the node performing stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path.

export BBS_REPORT_NODES="gladstone"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/cran/report.css"

