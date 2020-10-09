#!/bin/bash
# ====================
# Settings for malbec1
# ====================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="malbec1"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-3.12-bioc-testing"
# We use the same R instance that is used for the nightly software
# subbuilds (because it's convenient) but we don't want the bioc-testing
# subbuilds to interfer in any way with the nightly software subbuilds.
# In particular STAGE2 should NOT install anything in
# /home/biocbuild/bbs-3.12-bioc/R/library!
# So we set R_LIBS to point to our own library folder.
# IMPORTANT: Make sure to create the Rlibs folder on malbec1 before
# starting the bioc-testing subbuilds. Otherwise the bioc-testing
# subbuilds will ignore the folder and install packages in
# /home/biocbuild/bbs-3.12-bioc/R/library!
export BBS_R_HOME="/home/biocbuild/bbs-3.12-bioc/R"
export R_LIBS="/home/biocbuild/bbs-3.12-bioc-testing/Rlibs"
export BBS_NB_CPU=2        # 20 cores are available
export BBS_CHECK_NB_CPU=4  # 20 cores are available



# Shared settings (by all Unix nodes).

wd0=$(pwd)
cd ..
. ./config.sh
cd "$wd0"



# Overwrite values set in ../../config.sh and ../config.sh
export BBS_CENTRAL_RHOST="localhost"
export BBS_MEAT0_RHOST="localhost"
export BBS_GITLOG_RHOST="localhost"

# Needed only on the node performing stage6 (must be run on the
# BBS_CENTRAL_RHOST machine).
#

# If you are NOT using a bi-arch builder (i.e. moscato1 or moscato2) to
# create your Windows build products, the following note applies:

# IMPORTANT NOTE: The win.binary mapping must either include the 2
# Windows nodes (win32 and win64) or not be present at all. Temporarily
# dropping a Windows node will allow some single-arch Windows binary
# packages to propagate and to later not be replaced by the bi-arch when
# the dropped node is back.

export BBS_OUTGOING_MAP="source:malbec1/buildsrc win.binary:tokay1/buildbin"

# Needed only on the node performing stage7a (BBS-make-STATUS_DB.py) and
# stage8 (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

export BBS_REPORT_NODES="malbec1 tokay1:bin"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/$BBS_BIOC_VERSION/report.css"
export BBS_REPORT_BGIMG="$BBS_HOME/images/DEVEL3b.png"
export BBS_REPORT_JS="$BBS_HOME/$BBS_BIOC_VERSION/report.js"
#export BBS_REPORT_MOTD="Happy new year to all Bioconductor developers!"

# Needed only on the node performing stage9 (BBS-notify.py)

# TODO: when BBS_NOTIFY_NODES is not defined then take all the build nodes
export BBS_NOTIFY_NODES="malbec1"
