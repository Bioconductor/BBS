#!/bin/bash
# ======================================================================
# Settings shared by all the Unix nodes involved in the 2.2-mybbs builds
# ======================================================================


export BBS_MODE="bioc"

export BBS_BIOC_MANIFEST_FILE="bioc_2.2.manifest"

# What type of meat? Only 2 types are supported:
#   1: svn repo (contains pkg dirs)
#   2: CRAN-style local repo containing .tar.gz pkgs
export BBS_MEAT0_TYPE=1

# Where is it?
#export BBS_MEAT0_RHOST="gladstone"
#export BBS_MEAT0_RUSER="biocbuild"
#export BBS_MEAT0_RDIR="/home/biocbuild/bioc-trunk-Rpacks"

# Triggers a MEAT0 update at beginning of prerun (stage1)
export BBS_UPDATE_MEAT0=0

# Local meat copy
export BBS_MEAT_PATH="$BBS_WORK_TOPDIR/meat"


# Node local settings
. ../../nodes/$BBS_NODE/local-settings.sh

export BBS_BIOC_VERSION="2.2"

#export BBS_BIOC_VERSIONED_REPO_PATH="$BBS_BIOC_VERSION/$BBS_MODE"

export BBS_R_CMD="$BBS_R_HOME/bin/R"

export BBS_STAGE2_R_SCRIPT="$BBS_HOME/$BBS_BIOC_VERSION/bioc/STAGE2.R"

export BBS_CENTRAL_RDIR="/home/$USER/public_html/BBS/$BBS_BUILD_LABEL"
export BBS_CENTRAL_BASEURL="http://$BBS_NODE/~$USER/BBS/$BBS_BUILD_LABEL"

