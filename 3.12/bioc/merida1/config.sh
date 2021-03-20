#!/bin/bash
# ====================
# Settings for merida1
# ====================



#set -x  # Print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="merida1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.12-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=14        # 24 cores are available
export BBS_CHECK_NB_CPU=16  # 24 cores are available

# We use malbec1 internal IP address (DMZ-IP)
export BBS_CENTRAL_RHOST="172.29.0.3"
export BBS_MEAT0_RHOST="172.29.0.3"
export BBS_GITLOG_RHOST="172.29.0.3"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
