#!/bin/bash
# ========================
# Local settings for derby
# ========================


if [ "$BBS_HOME" == "" ]; then
    export BBS_HOME="/Users/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python"

export BBS_TAR_CMD="/usr/bin/tar"

# With StrictHostKeyChecking=no, ssh will automatically add new host keys
# to the user known hosts files (so it doesn't get stalled waiting for an
# answer when not run interactively).
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_SSH_CMD="/usr/bin/ssh -qi $BBS_RSAKEY -o StrictHostKeyChecking=no"
export BBS_RSYNC_CMD="/usr/bin/rsync -rl --delete --exclude='.svn'"
export BBS_RSYNC_RSH_CMD="$BBS_RSYNC_CMD -e '$BBS_SSH_CMD'"

# Needed only on the "prelim repo builder" node
# i.e. the node performing stage1
#export BBS_SVN_CMD="/usr/bin/svn"

