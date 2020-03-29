#!/bin/bash
# =========================
# Local settings for machv2
# =========================


if [ "$BBS_HOME" == "" ]; then
    export BBS_HOME="/Users/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python"

export BBS_SSH_CMD="/usr/bin/ssh"
export BBS_RSYNC_CMD="/usr/bin/rsync"
export LANG=en_US.UTF-8

