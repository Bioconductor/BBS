#!/bin/bash
# =======================
# Settings for wellington
# =======================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="wellington"
export BBS_USER="biocbuild"
export BBS_NB_CPU=4
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-2.2-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage9 (BBS-notify.py)

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
export BBS_NOTIFY_NODES="lamb1 wilson2 wellington liverpool:bin pitt:bin"
export BBS_PUBLISHED_REPORT_URL="http://bioconductor.org/checkResults/$BBS_BIOC_VERSION/bioc-LATEST/"

