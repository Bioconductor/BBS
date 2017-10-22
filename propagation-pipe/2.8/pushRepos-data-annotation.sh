#!/bin/sh

cd "$HOME/manage-BioC-repos/2.8"

. ./config.sh

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/data/annotation"



DEST="webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION/data/annotation"

rsync --delete -ave ssh $REPOS_ROOT/bin $REPOS_ROOT/manuals $REPOS_ROOT/REPOSITORY $REPOS_ROOT/src $REPOS_ROOT/SYMBOLS $REPOS_ROOT/VIEWS $REPOS_ROOT/vignettes $DEST

