#!/bin/bash
# ================================================================
# Settings shared by all the Unix nodes involved in the 3.9 builds
# ================================================================


# Paths to local commands
# -----------------------

. "../nodes/$BBS_NODE_HOSTNAME/local-settings.sh"

# With StrictHostKeyChecking=no, ssh will automatically add new host keys
# to the user known hosts files (so it doesn't get stalled waiting for an
# answer when not run interactively).
export BBS_SSH_CMD="$BBS_SSH_CMD -qi $BBS_RSAKEY -o StrictHostKeyChecking=no"
export BBS_RSYNC_CMD="$BBS_RSYNC_CMD -rl --delete --exclude='.svn' --exclude='.git'"
export BBS_RSYNC_RSH_CMD="$BBS_RSYNC_CMD -e '$BBS_SSH_CMD'"

export BBS_R_CMD="$BBS_R_HOME/bin/R"


# Variables specifying the version and mode of the current builds
# ---------------------------------------------------------------

export BBS_BIOC_VERSION="3.9"
export BBS_BIOC_GIT_BRANCH="master"
export BBS_BIOC_VERSIONED_REPO_PATH="$BBS_BIOC_VERSION/$BBS_SUBBUILDS"
export BBS_STAGE2_R_SCRIPT="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/STAGE2.R"
export BBS_NON_TARGET_REPOS_FILE="$BBS_HOME/$BBS_BIOC_VERSIONED_REPO_PATH/non_target_repos.txt"

export BBS_CENTRAL_RHOST="malbec2.bioconductor.org"
export BBS_CENTRAL_RUSER="biocbuild"
export BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"
export BBS_CENTRAL_BASEURL="https://$BBS_CENTRAL_RHOST/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"


# Variables specifying the location of the published report
# ---------------------------------------------------------

export BBS_PUBLISHED_REPORT_RELATIVEURL="checkResults/$BBS_BIOC_VERSION/$BBS_SUBBUILDS-LATEST/"
export BBS_PUBLISHED_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/$BBS_PUBLISHED_REPORT_RELATIVEURL"
export BBS_PUBLISHED_REPORT_URL="https://master.bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"


# 'R CMD check' variables
# -----------------------

#export _R_CHECK_TIMINGS_="0"
export _R_CHECK_EXECUTABLES_=false
export _R_CHECK_EXECUTABLES_EXCLUSIONS_=false
export _R_CHECK_LENGTH_1_CONDITION_=package:_R_CHECK_PACKAGE_NAME_,abort,verbose
export _R_CHECK_S3_METHODS_NOT_REGISTERED_=true
