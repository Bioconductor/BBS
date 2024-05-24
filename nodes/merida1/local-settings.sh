#!/bin/bash
# ==========================
# Local settings for merida1
# ==========================


if [ -z "$BBS_HOME" ]; then
    export BBS_HOME="/Users/biocbuild/BBS"
fi

export BBS_PYTHON_CMD="/usr/bin/python3"

export BBS_CURL_CMD="/usr/bin/curl"
export BBS_SSH_CMD="/usr/bin/ssh"
export BBS_RSYNC_CMD="/usr/bin/rsync"
export BBS_TAR_CMD="/usr/bin/tar"

export LANG=en_US.UTF-8

