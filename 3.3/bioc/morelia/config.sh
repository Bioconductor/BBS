#!/bin/bash
# =================
# Settings for morelia
# =================



#set -x # Print commands and their arguments as they are executed.

export BBS_DEBUG="0"

export BBS_NODE_HOSTNAME="morelia"
export BBS_USER="biocbuild"
export BBS_RSAKEY="/Users/biocbuild/.BBS/id_rsa"
export BBS_WORK_TOPDIR="/Users/biocbuild/bbs-3.3-bioc"
export BBS_R_HOME="/Library/Frameworks/R.framework/Versions/Current/Resources"
export BBS_NB_CPU=4 # 8 cores are available

export RCYTOSCAPE_PORT_OVERRIDE="5000"
export RCYTOSCAPE_HOST_OVERRIDE="taipan"
export RCYTOSCAPE3_PORT_OVERRIDE="9300"
export RCYTOSCAPE3_HOST_OVERRIDE="taipan"

export GENE_E_URL="http://taipan:9998"

## for ensemblVEP and rsbml
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/usr/local/lib:/usr/local/mysql/lib


# Shared settings (by all Unix nodes)

wd0=`pwd`
cd ..
. ./config.sh
cd "$wd0"

export BROWSERVIZ_BROWSER="phantomjs $BBS_HOME/utils/headless_browser.js "
