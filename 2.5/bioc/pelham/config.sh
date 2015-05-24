#!/bin/bash
# ===================
# Settings for pelham
# ===================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="pelham"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-2.5-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/2.10/Resources"
export BBS_NB_CPU=4



# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"
