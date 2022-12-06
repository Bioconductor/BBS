#!/bin/bash
# ======================
# Settings for nebbiolo2
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo2"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.17-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=42        # 72 cores are available
export BBS_BUILD_NB_CPU=28  # 72 cores are available
export BBS_CHECK_NB_CPU=34  # 72 cores are available

# Central build node is nebbiolo1 at DFCI.
export BBS_CENTRAL_RHOST="nebbiolo1"
export BBS_RSH_CMD="ssh -F /home/biocbuild/.ssh/config"
export BBS_CENTRAL_ROOT_URL="http://155.52.207.165"
export BBS_PRODUCT_TRANSMISSION_MODE="asynchronous"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"


# -----------------------------------------------------------------------------
# Do not use $BBS_R_HOME/library to instal packages
# This setup is required by _R_CHECK_SUGGESTS_ONLY_=true

# STAGE2 should NOT install anything in $BBS_R_HOME/library so we set R_LIBS
# to point to a separate library folder.
# IMPORTANT: Make sure to create the Rlibs folder on nebbiolo2 before starting
# the builds on this machine. Otherwise STAGE2 will ignore the folder and will
# install packages in $BBS_R_HOME/library!
export R_LIBS="$BBS_WORK_TOPDIR/Rlibs"
export R_ENVIRON_USER="$BBS_HOME/$BBS_BIOC_VERSION/bioc/nebbiolo2/Renviron.bioc"

