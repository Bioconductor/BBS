#!/bin/bash
# ======================
# Settings for nebbiolo1
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.12-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=27        # 72 cores are available
export BBS_CHECK_NB_CPU=36  # 72 cores are available



# Shared settings (by all Unix nodes).

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"

