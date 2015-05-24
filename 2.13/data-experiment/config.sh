#!/bin/bash
# ================================================================================
# Settings shared by all the Unix nodes involved in the 2.13-data-experiment builds
# ================================================================================


export BBS_MODE="data-experiment"

# TODO change this:
export BBS_BIOC_MANIFEST_FILE="bioc-data-experiment.2.13.manifest"

# What type of meat? Only 2 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
export BBS_MEAT0_TYPE=1

# Where is it?
export BBS_MEAT0_RHOST="zin1"
export BBS_MEAT0_RUSER="biocbuild"
export BBS_MEAT0_RDIR="/home/biocbuild/bbs-2.13-data-experiment/MEAT0"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=1

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"


wd1=`pwd`
cd ..
. ./config.sh
cd "$wd1"
