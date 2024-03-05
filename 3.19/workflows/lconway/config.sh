#!/bin/bash
# ====================
# Settings for lconway
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="lconway"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.19-workflows"
export BBS_R_HOME="/Library/Frameworks/R.framework/Resources"

# lconway has 48 logical CPUs.
export BBS_NB_CPU=16

# Central build node is nebbiolo1 at DFCI.
export BBS_CENTRAL_RHOST="nebbiolo1"
export BBS_RSH_CMD="ssh -F /Users/biocbuild/.ssh/config"
export BBS_CENTRAL_ROOT_URL="http://155.52.207.165"

# Source tarballs produced during STAGE3 won't be propagated
# so we don't need to push them to the central builder.
export DONT_PUSH_SRCPKGS="1"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
