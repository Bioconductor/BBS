#!/bin/bash
# ====================
# Settings for biocgpu
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="biocgpu"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.21-bioc-gpu"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export R_LIBS="$BBS_R_HOME/site-library"

# biocgpu has 8 logical CPUs but only 1 GPU so for now we err on the side
# of caution and set BBS_BUILD_NB_CPU and BBS_CHECK_NB_CPU to 1. This way
# each package gets exclusive access to the GPU during 'R CMD build'
# and 'R CMD check'.
export BBS_NB_CPU=5
export BBS_BUILD_NB_CPU=1
export BBS_CHECK_NB_CPU=1

# Central build node is bbscentral1 on Jetstream2.
export BBS_CENTRAL_RHOST="bbscentral1"
export BBS_RSH_CMD="ssh -F /home/biocbuild/.ssh/config"
export BBS_CENTRAL_ROOT_URL="http://149.165.171.124"
export BBS_PRODUCT_TRANSMISSION_MODE="asynchronous"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
