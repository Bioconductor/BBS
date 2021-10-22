#!/bin/bash
# ================================================================================
# Settings shared by all the Unix nodes involved in the 3.14-bioc-longtests builds
# ================================================================================


export BBS_BUILDTYPE="bioc-longtests"


wd1=$(pwd)
cd ..
. ./config.sh
cd "$wd1"


# What type of meat? Only 3 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
#   3: git repo containing pkg dirs
export BBS_MEAT0_TYPE=3

# Needed only if BBS_MEAT0_TYPE is 3
export BBS_BIOC_MANIFEST_GIT_REPO_URL="https://git.bioconductor.org/admin/manifest"
export BBS_BIOC_MANIFEST_GIT_BRANCH="RELEASE_3_14"
export BBS_BIOC_MANIFEST_CLONE_PATH="/home/biocbuild/bbs-3.14-bioc/manifest"

# Needed if BBS_MEAT0_TYPE is 1 or 3
export BBS_BIOC_MANIFEST_FILE="software.txt"

# Where is the fresh meat to be stored by prerun (stage1)
export BBS_MEAT0_RHOST="$BBS_CENTRAL_RHOST"
export BBS_MEAT0_RUSER="$BBS_CENTRAL_RUSER"
export BBS_MEAT0_RDIR="/home/biocbuild/bbs-3.14-bioc/MEAT0"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=1

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"

# Where are the gitlog files stored by prerun (stage1)
export BBS_GITLOG_RHOST="$BBS_CENTRAL_RHOST"
export BBS_GITLOG_RUSER="$BBS_CENTRAL_RUSER"
export BBS_GITLOG_RDIR="$BBS_CENTRAL_RDIR/gitlog"

# Local gitlog copy
export BBS_GITLOG_PATH="$BBS_WORK_TOPDIR/gitlog"

