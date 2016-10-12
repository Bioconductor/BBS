#!/bin/bash
# ==================
# Settings for lamb1
# ==================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE="lamb1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-2.8-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=4


export RCYTOSCAPE_PORT_OVERRIDE="4000"
export RCYTOSCAPE_HOST_OVERRIDE="wilson1"


# Shared settings (by all Unix nodes).

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage6 (must be run on the
# BBS_CENTRAL_RHOST machine).
#
# IMPORTANT NOTE: The win.binary mapping must either include the 2
# Windows nodes (win32 and win64) or not be present at all. Temporarily
# dropping a Windows node will allow some single-arch Windows binary
# packages to propagate and to later not be replaced by the bi-arch when
# the dropped node is back.

export BBS_OUTGOING_MAP="source:lamb1/buildsrc win.binary:liverpool/buildbin+gewurz/buildbin mac.binary.leopard:pelham/buildbin"


# Needed only on the node performing stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

export BBS_REPORT_NODES="lamb1 liverpool:bin gewurz:bin pelham:bin"
#export BBS_SVNCHANGELOG_URL="http://fgc.lsi.umich.edu/cgi-bin/blosxom.cgi"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
export BBS_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/checkResults/$BBS_BIOC_VERSION/bioc-LATEST"

# Needed only on the node performing stage9 (BBS-notify.py)

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
export BBS_NOTIFY_NODES="lamb1 liverpool:bin gewurz:bin pelham:bin"
#export BBS_NOTIFY_NODES="$BBS_REPORT_NODES"
export BBS_PUBLISHED_REPORT_URL="http://master.bioconductor.org/checkResults/$BBS_BIOC_VERSION/bioc-LATEST/"
