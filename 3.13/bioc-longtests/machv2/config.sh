#!/bin/bash
# ===================
# Settings for machv2
# ===================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="machv2"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.13-bioc-longtests"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=4  # 24 cores are available

# rex3 is not in the DNS so we use its IP address
export BBS_CENTRAL_RHOST="155.52.173.35"
export BBS_MEAT0_RHOST="155.52.173.35"
export BBS_GITLOG_RHOST="155.52.173.35"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
