#!/bin/bash

BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/2.3/data-experiment"

REPOS_ROOT="$HOME/PACKAGES/2.3/data/experiment"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.8"
MAC_UNIVERSAL_CONTRIB="$REPOS_ROOT/bin/macosx/universal/contrib/2.8"
MAC_LEOPARD_CONTRIB="$REPOS_ROOT/bin/macosx/leopard/contrib/2.8"

R="$HOME/bin/R-2.8"

echo ""
echo "========================================================================"
/bin/date
echo "------------------------------------"

echo "Updating repo with packages from wilson2..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/wilson2', '$SRC_CONTRIB', 'source')"| $R --slave

echo "Updating repo with packages from liverpool..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/liverpool', '$WIN_CONTRIB', 'win.binary')"| $R --slave

echo "Updating repo with packages from pitt..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/pitt', '$MAC_UNIVERSAL_CONTRIB', 'mac.binary.universal')"| $R --slave

echo "Updating repo with packages from pelham..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/pelham', '$MAC_LEOPARD_CONTRIB', 'mac.binary.leopard')"| $R --slave
