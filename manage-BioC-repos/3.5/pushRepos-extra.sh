#!/bin/sh

cd "$HOME/manage-BioC-repos/3.5"

. ./config.sh

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/extra"
DEST="webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION/extra"

rsync --delete -ave ssh $REPOS_ROOT/src $REPOS_ROOT/bin $REPOS_ROOT/manuals $REPOS_ROOT/REPOSITORY $REPOS_ROOT/SYMBOLS $REPOS_ROOT/VIEWS $REPOS_ROOT/vignettes $REPOS_ROOT/citations $REPOS_ROOT/news $REPOS_ROOT/licenses $REPOS_ROOT/readmes $REPOS_ROOT/install $DEST

