#!/bin/bash
# ======================
# Settings for nebbiolo2
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo2"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.17-bioc-testing"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
# STAGE2 should NOT install anything in $BBS_R_HOME/library!
# We set R_LIBS to point to our own library folder.
# IMPORTANT: Make sure to create the Rlibs folder on nebbiolo2 before
# starting the bioc-testing builds. Otherwise the bioc-testing
# builds will ignore the folder and will install packages in
# $BBS_R_HOME/library!
export R_LIBS="$BBS_WORK_TOPDIR/Rlibs"
export BBS_NB_CPU=32        # 72 cores are available
export BBS_CHECK_NB_CPU=40  # 72 cores are available

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

# Control generation of the report:
export BBS_REPORT_NODES="nebbiolo2"
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
#export BBS_NOTIFY_NODES="nebbiolo2"
#export BBS_PUBLISHED_REPORT_URL="https://master.bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"

