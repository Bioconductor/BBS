#!/bin/bash
# ================================================================
# Settings shared by all the Unix nodes involved in the 2.1 builds
# ================================================================


# Node local settings
. ../nodes/$BBS_NODE/local-settings.sh

export BBS_BIOC_VERSION="2.1"

export BBS_BIOC_VERSIONED_REPO_PATH="$BBS_BIOC_VERSION/$BBS_MODE"

export BBS_R_CMD="$BBS_R_HOME/bin/R"

export BBS_STAGE2_R_SCRIPT="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/STAGE2.R"

export BBS_CENTRAL_RHOST="lamb1"
export BBS_CENTRAL_RUSER="biocbuild"
export BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"
export BBS_CENTRAL_BASEURL="http://lamb1/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"

