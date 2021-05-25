#!/bin/bash
# =================================
# Settings for using Rtrunk on zin2
# =================================



#set -x  # print commands and their arguments as they are executed

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="zin2"
# If not explicitly set here, BBS_NODE_ID will be set to BBS_NODE_HOSTNAME.
# If explicitly set here, must be of the form "<BBS_NODE_HOSTNAME>-xxx".
# Needs to be set only when more than 1 build are running on the same host and
# are "linked" together (i.e. they use the same meat and send their results to
# the same central place where they will be merged in the same build report).
# Must be unique amongst the builds that are linked together.
export BBS_NODE_ID="zin2-Rtrunk"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/home/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/home/biocbuild/bbs-cran-Rtrunk"
export BBS_R_HOME="$BBS_WORK_TOPDIR/R"
export BBS_NB_CPU=3


export RCYTOSCAPE_PORT_OVERRIDE="8023"
export RCYTOSCAPE_HOST_OVERRIDE="wilson1"
export GENE_E_URL="http://zin2:9991"

export R_TEXI2DVICMD=/home/biocbuild/BBS/utils/ourtexi2dvi

# Shared settings (by all Unix nodes).

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"



# Needed only on the node performing stage6b (must be run on the
# BBS_CENTRAL_RHOST machine).
#

# If you are NOT using a bi-arch builder (i.e. moscato1 or moscato2) to
# create your Windows build products, the following note applies:

# IMPORTANT NOTE: The win.binary mapping must either include the 2
# Windows nodes (win32 and win64) or not be present at all. Temporarily
# dropping a Windows node will allow some single-arch Windows binary
# packages to propagate and to later not be replaced by the bi-arch when
# the dropped node is back.

export BBS_OUTGOING_MAP="source:zin2-Rtrunk/buildsrc"

# Needed only on the node performing stage6d (BBS-report.py)
#
# IMPORTANT: BBS-report.py will treat BBS_REPORT_PATH as a _local_ path so it
# must be run on the BBS_CENTRAL_RHOST machine.

export BBS_REPORT_NODES="zin2-Rtrunk zin2-Rshallow"
export BBS_REPORT_PATH="$BBS_CENTRAL_RDIR/report"
export BBS_REPORT_CSS="$BBS_HOME/cran/report.css"
export BBS_REPORT_JS="$BBS_HOME/cran/report.js"
export BBS_REPORT_DEST_DIR="webadmin@master.bioconductor.org:/extra/www/bioc/checkResults/cran-RshallowRtrunk/"
export BBS_PUBLISHED_REPORT_URL="http://master.bioconductor.org/checkResults/cran-RshallowRtrunk/"
#export BBS_NOTIFY_NODES="zin2"
