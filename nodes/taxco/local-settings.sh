#!/bin/bash
# ========================
# Local settings for taxco
# ========================


if [ "$BBS_HOME" == "" ]; then
    export BBS_HOME="/Users/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python3"

export BBS_SSH_CMD="/usr/bin/ssh"
export BBS_RSYNC_CMD="/usr/bin/rsync"
export LANG=en_US.UTF-8

# Needed only on a node capable of running STAGE1 (STAGE1 is supported on
# Linux only)
export BBS_TAR_CMD="/usr/bin/tar"
export BBS_GIT_CMD="/usr/bin/git"

