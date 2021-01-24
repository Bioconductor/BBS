#!/bin/bash
# ===================
# Settings for machv2
# ===================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="machv2"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.13-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=14        # 24 cores are available
export BBS_CHECK_NB_CPU=18  # 24 cores are available

export BBS_CENTRAL_RHOST="malbec2.bioconductor.org"
export BBS_MEAT0_RHOST="malbec2.bioconductor.org"
export BBS_GITLOG_RHOST="malbec2.bioconductor.org"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
