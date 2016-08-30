#!/bin/bash
# ==========================
# Local settings for malbec1
# ==========================

# FIXME - parameterize this as much as possible
# maybe use 'which' to find locations of programs
# but note that 'which' relies on the PATH which
# may be set incorrectly in crontab.

if [ "$BBS_HOME" == "" ]; then
    export BBS_HOME="/home/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python"

export BBS_SSH_CMD="/usr/bin/ssh"
export BBS_RSYNC_CMD="/usr/bin/rsync"

# Needed only on a node capable of running STAGE1 (STAGE1 is supported on
# Linux only)
export BBS_SVN_CMD="/usr/bin/svn"
export BBS_TAR_CMD="/bin/tar"

