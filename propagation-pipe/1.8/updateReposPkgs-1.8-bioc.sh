#!/bin/bash

BBS_CENTRAL_PATH="/home/biocbuild/public_html/BBS/bioc/1.8d"

REPOS_ROOT="$HOME/PACKAGES/1.8/bioc"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.3"

R="$HOME/bin/R-2.3"

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------"

echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_PATH/nodes/gopher5', '$SRC_CONTRIB', 'source')"| $R --slave
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_PATH/nodes/lemming', '$WIN_CONTRIB', 'win.binary')"| $R --slave
