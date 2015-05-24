#!/bin/bash
# =================================================================
# Settings shared by all the Unix nodes involved in the CRAN builds
# =================================================================


export BBS_MODE="cran"

export BBS_STAGE2_R_SCRIPT="$BBS_HOME/cran/mybbs/$BBS_NODE_HOSTNAME/STAGE2.R"

# What type of meat? Only 2 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
export BBS_MEAT0_TYPE=2

# Where is it?
export BBS_MEAT0_RHOST="gladstone"
export BBS_MEAT0_RUSER="biocbuild"
export BBS_MEAT0_RDIR="/home/biocbuild/cran-pkgs"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=0

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"


wd1=`pwd`
cd ..
. ./config.sh
cd "$wd1"

