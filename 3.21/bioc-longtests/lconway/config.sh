#!/bin/bash
# ====================
# Settings for lconway
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="lconway"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.21-bioc-longtests"
export BBS_R_HOME="/Library/Frameworks/R.framework/Resources"

# lconway has 48 logical CPUs.
export BBS_NB_CPU=8

# Central build node is bbscentral2 on Jetstream2.
export BBS_CENTRAL_RHOST="bbscentral2"
export BBS_RSH_CMD="ssh -F /Users/biocbuild/.ssh/config"
export BBS_CENTRAL_ROOT_URL="http://149.165.152.87"
export BBS_PRODUCT_TRANSMISSION_MODE="asynchronous"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
