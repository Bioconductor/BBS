#!/bin/bash

BBS_CENTRAL_RDIR="/home/biocbuild/public_html/BBS/2.1/bioc"

REPOS_ROOT="$HOME/PACKAGES/2.1/bioc"
SRC_CONTRIB="$REPOS_ROOT/src/contrib"
WIN_CONTRIB="$REPOS_ROOT/bin/windows/contrib/2.6"
MAC_CONTRIB="$REPOS_ROOT/bin/macosx/universal/contrib/2.6/"

## We delibarately use R-2.7 to work around the following problem with graph/biocViews
## in BioC 2.1:
##   Error in if (object@edgemode == "undirected" && length(objEdges) > 0) { :
##     missing value where TRUE/FALSE needed
##   Calls: getBiocSubViews ... anyStrings -> identical -> validityMethod -> validGraph
##   Execution halted
R="$HOME/bin/R-2.7"

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

echo "Updating repo with packages from pitt..."
echo "library('buildBioC'); BBSupdateRepos('$BBS_CENTRAL_RDIR/nodes/pitt', '$MAC_CONTRIB', 'mac.binary')"| $R --slave

