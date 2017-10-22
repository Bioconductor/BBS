#!/bin/sh

cd "$HOME/manage-BioC-repos/3.6"

. ./config.sh

VIEW_ROOT="$HOME/PACKAGES/$BIOC_VERSION"
DEST="webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION"

#rsync --delete -ave ssh $VIEW_ROOT/*.html $DEST

#rsync --delete -ave ssh $VIEW_ROOT/*.css $DEST
