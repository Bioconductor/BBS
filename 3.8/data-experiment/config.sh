#!/bin/bash
# ===================================================================================
# Settings shared by all the Unix nodes involved in the 3.8-data-experiment subbuilds
# ===================================================================================


export BBS_SUBBUILDS="data-experiment"

# What type of meat? Only 3 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
#   3: git repo containing pkg dirs
export BBS_MEAT0_TYPE=3

# Needed only if BBS_MEAT0_TYPE is 3
export BBS_BIOC_MANIFEST_GIT_REPO_URL="https://git.bioconductor.org/admin/manifest"
export BBS_BIOC_MANIFEST_GIT_BRANCH="master"
export BBS_BIOC_MANIFEST_CLONE_PATH="$BBS_WORK_TOPDIR/manifest"

# Needed if BBS_MEAT0_TYPE is 1 or 3
export BBS_BIOC_MANIFEST_FILE="data-experiment.txt"

# Where is the fresh meat to be stored by prerun (stage1)
export BBS_MEAT0_RHOST="malbec1.bioconductor.org"
export BBS_MEAT0_RUSER="biocbuild"
export BBS_MEAT0_RDIR="/home/biocbuild/bbs-3.8-data-experiment/MEAT0"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=1

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"

# Where are the gitlog files stored by prerun (stage1)
export BBS_GITLOG0_RHOST=$BBS_MEAT0_RHOST
export BBS_GITLOG0_RUSER=$BBS_MEAT0_RUSER
export BBS_GITLOG0_RDIR="/home/biocbuild/bbs-3.8-data-experiment/GITLOG0"

# Local gitlog copy
export BBS_GITLOG_PATH="$BBS_WORK_TOPDIR/gitlog"

wd1=$(pwd)
cd ..
. ./config.sh
cd "$wd1"
