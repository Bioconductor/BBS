#!/bin/bash
# ==================
# Settings for derby
# ==================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="derby"
export BBS_NB_CPU=2
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-2.0-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Resources"



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"

