#!/bin/sh

VIEW_ROOT="$HOME/PACKAGES/2.1"
DEST="webadmin@cobra:/extra/www/bioc/packages/2.1"

rsync --delete -ave ssh $VIEW_ROOT/*.html $DEST

rsync --delete -ave ssh $VIEW_ROOT/*.css $DEST
