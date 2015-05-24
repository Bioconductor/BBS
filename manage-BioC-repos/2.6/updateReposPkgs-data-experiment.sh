#!/bin/bash

BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/2.6/data-experiment"

REPOS_ROOT="$HOME/PACKAGES/2.6/data/experiment"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.11"
MAC_LEOPARD_CONTRIB="$REPOS_ROOT/bin/macosx/leopard/contrib/2.11"

R="$HOME/bin/R-2.11"

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------"

echo "Updating repo with packages from wilson1..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/wilson1', '$SRC_CONTRIB', 'source')"| $R --slave

echo "Updating repo with packages from liverpool..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/liverpool', '$WIN_CONTRIB', 'win.binary')"| $R --slave

echo "Updating repo with packages from pelham..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/pelham', '$MAC_LEOPARD_CONTRIB', 'mac.binary.leopard')"| $R --slave
