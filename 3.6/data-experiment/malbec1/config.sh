#!/bin/bash
# ====================
# Settings for malbec1
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="malbec1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.6-data-experiment"
export BBS_R_HOME="/home/biocbuild/bbs-3.6-bioc/R"
export BBS_NB_CPU=8  # 20 cores are available



# Shared settings (by all Unix nodes).

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage6 (must be run on the
# BBS_CENTRAL_RHOST machine).

# FIXME add mac.mavericks.binary:oaxaca/buildbin
#export BBS_OUTGOING_MAP="source:malbec1/buildsrc win.binary:tokay1/buildbin"
export BBS_OUTGOING_MAP="source:malbec1/buildsrc"

# Needed only on the node performing stage7a (BBS-make-STATUS_DB.py) and
# stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

# FIXME add oaxaca:bin
#export BBS_REPORT_NODES="malbec1 tokay1:bin"
export BBS_REPORT_NODES="malbec1"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
export BBS_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/checkResults/$BBS_BIOC_VERSION/data-experiment-LATEST"

