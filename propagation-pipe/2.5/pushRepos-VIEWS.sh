#!/bin/sh

VIEW_ROOT="$HOME/PACKAGES/2.5"
DEST="webadmin@cobra:/extra/www/bioc/packages/2.5"

rsync --delete -ave ssh $VIEW_ROOT/*.html $DEST

rsync --delete -ave ssh $VIEW_ROOT/*.css $DEST
