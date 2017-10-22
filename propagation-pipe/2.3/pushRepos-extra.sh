#!/bin/sh

REPOS_ROOT="$HOME/PACKAGES/2.3/extra"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.3
