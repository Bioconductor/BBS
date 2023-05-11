#!/usr/bin/env bash
# ===================================
# Settings for kunpeng1 (Linux ARM64)
# ===================================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="kunpeng1"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.18-bioc"
export BBS_R_HOME="$HOME/R-devel_2023-03-12_r83975-bin"
export R_LIBS="$BBS_R_HOME/site-library"
export BBS_NB_CPU=24         # 32 cores are available
export BBS_BUILD_NB_CPU=10   # 32 cores are available
export BBS_CHECK_NB_CPU=10   # 32 cores are available

# Central build node is nebbiolo1 at DFCI.
#export BBS_CENTRAL_RHOST="nebbiolo1"
export BBS_CENTRAL_RHOST="localhost"
export BBS_RSH_CMD="ssh -F /home/biocbuild/.ssh/config"
#export BBS_CENTRAL_ROOT_URL="http://155.52.207.165"
export BBS_CENTRAL_ROOT_URL="http://$BBS_CENTRAL_RHOST"
export BBS_PRODUCT_TRANSMISSION_MODE="asynchronous"

export BBS_BUILD_TIMEOUT=2400
export BBS_CHECK_TIMEOUT=2400

# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



# -----------------------------------------------------------------------------
# The variables below control postrun.sh so only need to be defined on the
# central node

# Control propagation:
#export BBS_OUTGOING_MAP="source:nebbiolo1/buildsrc win.binary:palomino3/buildbin mac.binary:merida1/buildbin"
#export BBS_FINAL_REPO="file://home/biocpush/PACKAGES/$BBS_BIOC_VERSION/bioc"

# Control generation of the report:
#export BBS_REPORT_NODES="nebbiolo1 palomino3:bin merida1:bin"
export BBS_REPORT_NODES="kunpeng1"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
#export BBS_REPORT_MOTD="Happy new year to all Bioconductor developers!"

# Control where to publish the report:
#export BBS_PUBLISHED_REPORT_RELATIVEURL="checkResults/$BBS_BIOC_VERSION/$BBS_BUILDTYPE-LATEST/"
#export BBS_PUBLISHED_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/$BBS_PUBLISHED_REPORT_RELATIVEURL"


# -----------------------------------------------------------------------------
# The variables below control stage7-notify.sh so only need to be defined on
# the central node

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
#export BBS_NOTIFY_NODES="nebbiolo1"
#export BBS_PUBLISHED_REPORT_URL="https://master.bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"


