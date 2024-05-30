#!/bin/bash
# ======================
# Settings for kjohnson1
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="kjohnson1"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.20-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Resources"

# kjohnson1 has 10 cores available.
export BBS_NB_CPU=7
export BBS_BUILD_NB_CPU=5
export BBS_CHECK_NB_CPU=6
export BBS_EXTRA_CHECK_OPTIONS="--no-vignettes"

# Central build node is bbscentral2 on Jetstream2.
export BBS_CENTRAL_RHOST="bbscentral2"
export BBS_RSH_CMD="ssh -F /Users/biocbuild/.ssh/config"
export BBS_CENTRAL_ROOT_URL="http://149.165.154.78"
export BBS_PRODUCT_TRANSMISSION_MODE="asynchronous"

# Source tarballs produced during STAGE3 won't be propagated
# so we don't need to push them to the central builder.
export DONT_PUSH_SRCPKGS="1"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
