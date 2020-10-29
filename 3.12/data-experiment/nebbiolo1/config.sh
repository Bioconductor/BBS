#!/bin/bash
# ======================
# Settings for nebbiolo1
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.12-data-experiment"
export BBS_R_HOME="/home/biocbuild/bbs-3.12-bioc/R"
export BBS_NB_CPU=12        # 72 cores are available
export BBS_CHECK_NB_CPU=16  # 72 cores are available

# Source tarballs produced during STAGE3 are BIG and won't be propagated
# so we don't need to push them to the central builder.
export DONT_PUSH_SRCPKGS=1



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"

