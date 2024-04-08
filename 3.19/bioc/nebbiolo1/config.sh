#!/bin/bash
# ======================
# Settings for nebbiolo1
# ======================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="nebbiolo1"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.19-bioc"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export R_LIBS="$BBS_R_HOME/site-library"

# nebbiolo1 has 72 logical CPUs.
export BBS_NB_CPU=24
export BBS_BUILD_NB_CPU=16
export BBS_CHECK_NB_CPU=24

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
export BBS_OUTGOING_MAP="source:nebbiolo1/buildsrc win.binary:palomino3/buildbin mac.binary.big-sur-x86_64:lconway/buildbin"
export BBS_FINAL_REPO="file://home/biocpush/PACKAGES/$BBS_BIOC_VERSION/bioc"

# Control generation of the report:
export BBS_REPORT_NODES="nebbiolo1 palomino3:bin lconway:bin kunpeng2 kjohnson3:foreign"
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

