#!/bin/bash

this_script=$(basename "$0")
echo "<<< Now starting $this_script at $(date) >>>"
cd "$HOME/manage-BioC-repos/3.3"

. ./config.sh

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/bioc"


DEST="webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION/bioc"

rsync --delete -ave ssh $REPOS_ROOT/bin $REPOS_ROOT/manuals $REPOS_ROOT/REPOSITORY $REPOS_ROOT/src $REPOS_ROOT/SYMBOLS $REPOS_ROOT/VIEWS $REPOS_ROOT/vignettes $REPOS_ROOT/readmes $REPOS_ROOT/news $REPOS_ROOT/install $REPOS_ROOT/licenses $REPOS_ROOT/citations $DEST

echo "<<< Now exiting $this_script at $(date) >>>"
