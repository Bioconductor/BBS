#!/bin/bash

BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/1.9/bioc"

REPOS_ROOT="$HOME/PACKAGES/1.9/bioc"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.4"

R="$HOME/bin/R-2.4"

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------"

echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/lamb1', '$SRC_CONTRIB', 'source')"| $R --slave
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/lemming', '$WIN_CONTRIB', 'win.binary')"| $R --slave
