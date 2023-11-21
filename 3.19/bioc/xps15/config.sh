#!/bin/bash
# ==================================
# Settings for xps15 (external node)
# ==================================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="xps15"
export BBS_WORK_TOPDIR="/home/hpages/bbs-3.19-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export R_LIBS="$BBS_R_HOME/site-library"

# xps15 has 20 logical CPUs.
export BBS_NB_CPU=10

export BBS_PRODUCT_TRANSMISSION_MODE="none"

# Central build node is nebbiolo1 at DFCI.
export BBS_CENTRAL_ROOT_URL="http://155.52.207.165"

# Source tarballs produced during STAGE3 won't be propagated so
# we don't need to make them available to the central builder.
export DONT_PUSH_SRCPKGS="1"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
