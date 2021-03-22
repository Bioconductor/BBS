#!/bin/bash
# ====================
# Settings for merida1
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="merida1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.12-bioc-longtests"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=4  # 24 cores are available

export BBS_CENTRAL_RHOST="malbec1.bioconductor.org"
export BBS_MEAT0_RHOST="malbec1.bioconductor.org"
export BBS_GITLOG_RHOST="malbec1.bioconductor.org"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
