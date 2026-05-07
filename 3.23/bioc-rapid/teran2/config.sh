#!/bin/bash
# ===================
# Settings for teran2
# ===================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_HOME="/home/rapidbuild/BBS"

export BBS_NODE_HOSTNAME="teran2"
export BBS_USER="rapidbuild"
export BBS_WORK_TOPDIR="/home/rapidbuild/bbs-3.23-bioc-rapid"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export R_LIBS="$BBS_R_HOME/site-library"

# teran2 has 16 logical CPUs.
export BBS_NB_CPU=10
export BBS_BUILD_NB_CPU=9
export BBS_CHECK_NB_CPU=13
export BBS_BIOCCHECK_NB_CPU=13

export BBS_CENTRAL_RHOST="localhost"
export BBS_CENTRAL_ROOT_URL="http://$BBS_CENTRAL_RHOST"

# Source tarballs produced during STAGE3 won't be propagated so we don't
# need to push them to the products-in/ folder on the central builder.
export DONT_PUSH_SRCPKGS="1"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



# -----------------------------------------------------------------------------
# The variables below control postrun.sh so only need to be defined on the
# central node

# Control generation of the report:
export BBS_REPORT_NODES="teran2:bioccheck"
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
#export BBS_NOTIFY_NODES="teran2"
#export BBS_PUBLISHED_REPORT_URL="https://bioconductor.org/$BBS_PUBLISHED_REPORT_RELATIVEURL"

