#!/bin/bash
# =================
# Settings for pelham
# =================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="pelham"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-2.12-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=4

export RCYTOSCAPE_PORT_OVERRIDE="7000"
export RCYTOSCAPE_HOST_OVERRIDE="wilson1"

## for ensemblVEP and rsbml
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/usr/local/lib:/usr/local/mysql/lib

# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"
