#!/bin/bash
# ==================
# Settings for taxco
# ==================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="taxco"
export BBS_USER="biocbuild"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.13-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=7        # 8 cores are available
export BBS_CHECK_NB_CPU=7  # 8 cores are available

export BBS_CENTRAL_RHOST="localhost"
export BBS_CENTRAL_ROOT_URL="file:/Users/biocbuild/public_html"



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



export BBS_MEAT0_RDIR="/Users/biocbuild/bbs-3.13-bioc/MEAT0"
export BBS_CENTRAL_RDIR="/Users/biocbuild/public_html/BBS/$BBS_BIOC_VERSIONED_REPO_PATH"
export BBS_GITLOG_RDIR="$BBS_CENTRAL_RDIR/gitlog"


# -----------------------------------------------------------------------------
# The variables below control postrun.sh so only need to be defined on the
# central node

# Control generation of the report:
export BBS_REPORT_NODES="taxco"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
export BBS_REPORT_MOTD="These are experimental builds on Apple's new arm64 arch. See <A href="https://github.com/Bioconductor/BBS/blob/master/Doc/BigSur-arm64-builds.md">here</A> for more information."

# Control where to publish the report:
export BBS_PUBLISHED_REPORT_RELATIVEURL="checkResults/$BBS_BIOC_VERSION/taxco/$BBS_BUILDTYPE-LATEST/"
export BBS_PUBLISHED_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/$BBS_PUBLISHED_REPORT_RELATIVEURL"

