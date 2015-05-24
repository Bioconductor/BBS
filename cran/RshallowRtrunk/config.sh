#!/bin/bash
# ========================================================================
# Settings shared by all the Unix nodes participating to the
# cran-RshallowRtrunk builds
# ========================================================================


export BBS_MODE="cran"

# What type of meat? Only 2 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
export BBS_MEAT0_TYPE=2

# Where is it?
export BBS_MEAT0_RHOST="zin2"
export BBS_MEAT0_RUSER="biocbuild"
export BBS_MEAT0_RDIR="/home/biocbuild/bbs-cran-Rtrunk/MEAT0"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=0

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"


wd1=`pwd`
cd ..
. ./config.sh
cd "$wd1"


export BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/cran-RshallowRtrunk"
export BBS_CENTRAL_BASEURL="http://zin2/BBS/cran-RshallowRtrunk"

