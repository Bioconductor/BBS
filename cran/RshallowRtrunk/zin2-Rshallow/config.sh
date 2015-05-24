#!/bin/bash
# ===================================
# Settings for using Rshallow on zin2
# ===================================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="zin2"
# If not explicitly set here, BBS_NODE_ID will be set to BBS_NODE_HOSTNAME.
# If explicitly set here, must be of the form "<BBS_NODE_HOSTNAME>-xxx".
# Needs to be set only when more than 1 build are running on the same host and
# are "linked" together (i.e. they use the same meat and send their results to
# the same central place where they will be merged in the same build report).
# Must be unique amongst the builds that are linked together.
export BBS_NODE_ID="zin2-Rshallow"  
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-cran-Rshallow"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=3


export RCYTOSCAPE_PORT_OVERRIDE="8023"
export RCYTOSCAPE_HOST_OVERRIDE="wilson1"
export GENE_E_URL="http://zin2:9991"

export R_TEXI2DVICMD=/home/biocbuild/BBS/utils/ourtexi2dvi

# Shared settings (by all Unix nodes).

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"
