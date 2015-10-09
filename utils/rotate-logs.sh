#!/usr/bin/env bash

###
### Script to rotate build logs on Ubuntu & Mac OS X
### TODO: Ensure functionality on OS X
###

set -e

# TODO: Remove this next line, it's only here for initial debugging
# set -x

: "${BBS_BIOC_VERSION:?"The environment variable 'BBS_BIOC_VERSION' must be set and non-empty"}"
HN=$(hostname)

function verifyBuildFinished {
  cd "$HOME"/public_html/BBS/"${BBS_BIOC_VERSION}"/bioc/nodes
  node_finished=$(find . -maxdepth 2 -type f -exec ls -1 {} \;|grep "BBS_EndOfRun"| grep -c "${HN}")
  if [ "${node_finished}" -eq 1 ]; then
    # 0 = true
    return 0
  else
    echo "The build has not finished on this node.  Can not continue".
    # 1 = false
    return 1
  fi
}

function rotateLog {
  cd "$HOME"/bbs-"${BBS_BIOC_VERSION}"-bioc/log
  mkdir -p log-archives
  archive_file="log-archives/${HN}-$(date '+%Y-%b').log"
  mv "${HN}.log" "${archive_file}"
  touch "${HN}.log"
  if ! [ -f "${archive_file}.gz" ]; then
    gzip "${archive_file}"
    echo "Finished log rotation"
    exit 0
  else
    echo "Archived log file already exists: '$(pwd)/${archive_file}.gz'.  Cannot continue."
    exit 1
  fi
}

function begin {
  if [ "$(whoami)" != "biocbuild" ]; then
    echo "This script must be run as the 'biocbuild' user"
    exit 1
  fi

  if verifyBuildFinished; then
    rotateLog
  fi
}

begin
