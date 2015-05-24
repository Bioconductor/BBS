#!/bin/bash
# ================================================================
# Settings shared by all the Unix nodes involved in the 2.14 builds
# ================================================================


# Paths to local commands
# -----------------------

. ../nodes/$BBS_NODE_HOSTNAME/local-settings.sh

# With StrictHostKeyChecking=no, ssh will automatically add new host keys
# to the user known hosts files (so it doesn't get stalled waiting for an
# answer when not run interactively).
export BBS_SSH_CMD="$BBS_SSH_CMD -qi $BBS_RSAKEY -o StrictHostKeyChecking=no"
export BBS_RSYNC_CMD="$BBS_RSYNC_CMD -rl --delete --exclude='.svn'"
export BBS_RSYNC_RSH_CMD="$BBS_RSYNC_CMD -e '$BBS_SSH_CMD'"

export BBS_R_CMD="$BBS_R_HOME/bin/R"


# Variables specifying the version and mode of the current builds
# ---------------------------------------------------------------

export BBS_BIOC_VERSION="2.14"
export BBS_BIOC_VERSIONED_REPO_PATH="$BBS_BIOC_VERSION/$BBS_MODE"
export BBS_STAGE2_R_SCRIPT="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/STAGE2.R"
export BBS_NON_TARGET_REPOS_FILE="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/non_target_repos.txt"

export BBS_CENTRAL_RHOST="zin2"
export BBS_CENTRAL_RUSER="biocbuild"
export BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"
export BBS_CENTRAL_BASEURL="http://zin2/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"


# 'R CMD check' variables
# -----------------------

export _R_CHECK_TIMINGS_="0"
export _R_CHECK_EXECUTABLES_=false
export _R_CHECK_EXECUTABLES_EXCLUSIONS_=false

