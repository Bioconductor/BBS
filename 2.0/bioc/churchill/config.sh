#!/bin/bash
# ======================
# Settings for churchill
# ======================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="churchill"
export BBS_NB_CPU=4
export BBS_WORK_TOPDIR="/loc/biocbuild/bbs-2.0-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"

