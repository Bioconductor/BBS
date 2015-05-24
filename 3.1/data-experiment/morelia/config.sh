#!/bin/bash
# =================
# Settings for morelia
# =================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="morelia"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.1-data-experiment"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=7 # 8 cores are available



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"
