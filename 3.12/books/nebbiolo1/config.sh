#!/bin/bash
# ======================
# Settings for nebbiolo1
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.12-books"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=8  # 72 cores are available

export BBS_CENTRAL_RHOST="localhost"
export BBS_MEAT0_RHOST="localhost"
export BBS_GITLOG_RHOST="localhost"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage6 (must be run on the
# BBS_CENTRAL_RHOST machine).

export BBS_OUTGOING_MAP="source:nebbiolo1/buildsrc"

# Needed only on the node performing stage7a (BBS-make-STATUS_DB.py) and
# stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

export BBS_REPORT_NODES="nebbiolo1"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
#export BBS_REPORT_MOTD="Happy new year to all Bioconductor developers!"

# Where to publish the report
export BBS_PUBLISHED_REPORT_RELATIVEURL="checkResults/$BBS_BIOC_VERSION/$BBS_SUBBUILDS-LATEST/"
export BBS_PUBLISHED_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/$BBS_PUBLISHED_REPORT_RELATIVEURL"


# Needed only on the node performing stage9 (BBS-notify.py)

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
#export BBS_NOTIFY_NODES="nebbiolo1"
#export BBS_PUBLISHED_REPORT_URL="https://master.bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"

