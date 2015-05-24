#!/bin/sh

VIEW_ROOT="$HOME/PACKAGES/1.9"
DEST="webadmin@cobra:/extra/www/bioc/packages/1.9"

rsync --delete -ave ssh $VIEW_ROOT/*.html $DEST

rsync --delete -ave ssh $VIEW_ROOT/*.css $DEST
