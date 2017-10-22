#!/bin/bash

BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/2.0/bioc"

REPOS_ROOT="$HOME/PACKAGES/2.0/bioc"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.5"

R="$HOME/bin/R-2.5"

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------"

echo "Updating repo with packages from lamb1..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/lamb1', '$SRC_CONTRIB', 'source')"| $R --slave

echo "Updating repo with packages from liverpool..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/liverpool', '$WIN_CONTRIB', 'win.binary')"| $R --slave

echo "Updating repo with packages from lemming..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/lemming', '$WIN_CONTRIB', 'win.binary')"| $R --slave

