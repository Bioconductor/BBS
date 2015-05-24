#!/bin/bash

set -e  # Exit immediately if a simple command exits with a non-zero status

SRC_TOPDIR=biocbuild@compton:/Builds/packages/BIOC.new/bin/2.1
DEST_TOPDIR=~/PACKAGES/2.1

if [ "$1" != "test" ]; then
    DRYRUN=""
else
    DRYRUN="--dry-run"
fi

echo "###"
echo "### SCRIPT WAS CALLED WITH: $0 $*"
echo "### STARTED WORKING AT: `date`"
echo "###"
echo ""

rsync $DRYRUN --delete -rtlv -e ssh "$SRC_TOPDIR/bioc/tiger-universal/bin/2.6/" "$DEST_TOPDIR/bioc/bin/macosx/universal/contrib/2.6/"

rsync $DRYRUN --delete -rtlv -e ssh "$SRC_TOPDIR/data/annotation/tiger-universal/bin/2.6/" "$DEST_TOPDIR/data/annotation/bin/macosx/universal/contrib/2.6/"

rsync $DRYRUN --delete -rtlv -e ssh "$SRC_TOPDIR/data/experiment/tiger-universal/bin/2.6/" "$DEST_TOPDIR/data/experiment/bin/macosx/universal/contrib/2.6/"

rsync $DRYRUN --delete -rtlv -e ssh "$SRC_TOPDIR/extra/tiger-universal/bin/2.6/" "$DEST_TOPDIR/extra/bin/macosx/universal/contrib/2.6/"

echo ""
echo "###"
echo "### ENDED WORKING AT: `date`"
echo "###"
echo ""

if [ "$1" != "test" ]; then
	cat <<-EOD
	Now you must run:
	
	  cd ~/manage-BioC-repos/2.1
	  ./prepareRepos-bioc.sh && ./pushRepos-bioc.sh
	  ./prepareRepos-data-annotation.sh && ./pushRepos-data-annotation.sh
	  ./prepareRepos-data-experiment.sh && ./pushRepos-data-experiment.sh
	  ./prepareRepos-extra.sh && ./pushRepos-extra.sh

	in order to propagate the new Mac binary packages to cobra.
	EOD
fi

