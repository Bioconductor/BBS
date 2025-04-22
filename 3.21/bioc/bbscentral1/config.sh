#!/bin/bash
# ========================
# Settings for bbscentral1
# ========================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="bbscentral1"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.21-bioc"
export BBS_R_HOME="/home/biocbuild/R/R-4.5"
export R_LIBS="$BBS_R_HOME/site-library"

export BBS_CENTRAL_RHOST="localhost"
export BBS_CENTRAL_ROOT_URL="http://$BBS_CENTRAL_RHOST"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



# -----------------------------------------------------------------------------
# The variables below control postrun.sh so only need to be defined on the
# central node

# Control propagation:
export BBS_OUTGOING_MAP="source:nebbiolo1/buildsrc win.binary:palomino7/buildbin mac.binary.big-sur-x86_64:merida1/buildbin mac.binary.big-sur-arm64:kjohnson1/buildbin"
export BBS_FINAL_REPO="file://home/biocpush/PACKAGES/$BBS_BIOC_VERSION/bioc"

# Control generation of the report:
export BBS_REPORT_NODES="nebbiolo1 palomino7:bin merida1:bin kjohnson1:bin kunpeng2"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
#export BBS_REPORT_MOTD="Happy new year to all Bioconductor developers!"

# Control where to publish the report:
export BBS_PUBLISHED_REPORT_RELATIVEURL="checkResults/$BBS_BIOC_VERSION/$BBS_BUILDTYPE-LATEST/"
export BBS_PUBLISHED_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/$BBS_PUBLISHED_REPORT_RELATIVEURL"


# -----------------------------------------------------------------------------
# The variables below control stage7-notify.sh so only need to be defined on
# the central node

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
export BBS_NOTIFY_NODES="nebbiolo1"
export BBS_PUBLISHED_REPORT_URL="https://bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"

