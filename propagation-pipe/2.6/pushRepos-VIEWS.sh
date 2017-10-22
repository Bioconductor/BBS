#!/bin/sh

VIEW_ROOT="$HOME/PACKAGES/2.6"
DEST="webadmin@master.bioconductor.org:/extra/www/bioc/packages/2.6"

rsync --delete -ave ssh $VIEW_ROOT/*.html $DEST

rsync --delete -ave ssh $VIEW_ROOT/*.css $DEST
