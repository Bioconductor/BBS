#!/bin/bash
# ====================
# Settings for wilson2
# ====================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="wilson2"
export BBS_USER="biocbuild"
export BBS_NB_CPU=2
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-2.1-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"

