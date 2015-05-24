#!/bin/bash
# ==================
# Settings for lamb1
# ==================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE="lamb1"
export BBS_USER="biocbuild"
export BBS_NB_CPU=2
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-2.1-biocLite"
export BBS_R_HOME="/home/biocbuild/bbs-2.1-bioc/R"


# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

export BBS_REPORT_NODES="lamb1 liverpool:bin"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_DEST_DIR="webadmin@cobra:/extra/www/bioc/checkResults/$BBS_BIOC_VERSION/biocLite-LATEST"

