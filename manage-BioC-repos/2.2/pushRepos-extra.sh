#!/bin/sh

REPOS_ROOT="$HOME/PACKAGES/2.2/extra"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.2
