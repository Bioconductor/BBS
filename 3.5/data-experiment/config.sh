#!/bin/bash
# ================================================================================
# Settings shared by all the Unix nodes involved in the 3.5-data-experiment builds
# ================================================================================


export BBS_MODE="data-experiment"

# What type of meat? Only 3 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
#   3: git repo containing pkg dirs
export BBS_MEAT0_TYPE=3

# Needed only if BBS_MEAT0_TYPE is 3
export BBS_BIOC_MANIFEST_GIT_REPO_URL="https://git.bioconductor.org/admin/manifest"
export BBS_BIOC_MANIFEST_GIT_BRANCH="RELEASE_3_5"

# Needed if BBS_MEAT0_TYPE is 1 or 3
export BBS_BIOC_MANIFEST_FILE="dataexperiment.txt"

# Where is the fresh meat to be stored by prerun (stage1)
export BBS_MEAT0_RHOST="malbec2"
export BBS_MEAT0_RUSER="biocbuild"
export BBS_MEAT0_RDIR="/home/biocbuild/bbs-3.5-data-experiment/MEAT0"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=1

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"


wd1=$(pwd)
cd ..
. ./config.sh
cd "$wd1"
