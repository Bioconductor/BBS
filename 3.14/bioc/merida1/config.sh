#!/bin/bash
# ====================
# Settings for merida1
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="merida1"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.14-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Resources"
export BBS_NB_CPU=14        # 24 cores are available
export BBS_CHECK_NB_CPU=16  # 24 cores are available

# Central build node is nebbiolo2 at DFCI (ssh connections must be made via
# jump host ada.dfci.harvard.edu, see BBS_RSH_CMD below).
export BBS_CENTRAL_RHOST="155.52.47.146"

# When used with StrictHostKeyChecking=no, ssh will automatically add new
# host keys to the user known hosts files (so it doesn't get stalled waiting
# for an answer when not run interactively).
export BBS_RSH_CMD="/usr/bin/ssh -q -o StrictHostKeyChecking=no -J biocbuild@ada.dfci.harvard.edu"

export BBS_CENTRAL_ROOT_URL="http://155.52.207.166"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"
