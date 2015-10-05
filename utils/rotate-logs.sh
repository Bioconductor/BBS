#!/usr/bin/env bash

###
### Script to rotate build logs on Ubuntu & Mac OS X
### TODO: Ensure functionality on OS X
###

set -e

# TODO: Remove this next line, it's only here for initial debugging
# set -x

TOTAL_BUILD_NODES=4

function verifyBuildFinished {
  cd /home/biocbuild/public_html/BBS/3.2/bioc/nodes
  nodes_finished=$(find . -maxdepth 2 -type f -exec ls -1 {} \;|grep -c "BBS_EndOfRun")
  if [ "${nodes_finished}" -eq "${TOTAL_BUILD_NODES}" ]; then
    # 0 = true
    return 0
  else
    echo "The build has not finished on all nodes.  ${nodes_finished} of ${TOTAL_BUILD_NODES} completed."
    echo "Can not continue"
    # 1 = false
    return 1
  fi
}

function rotateLog {
  cd /home/biocbuild/bbs-3.2-bioc/log
  mkdir -p log-archives
  hn=$(hostname)
  archive_file="log-archives/${hn}-$(date '+%Y%m%d').log"
  mv "${hn}.log" "${archive_file}"
  touch "${hn}.log"
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
