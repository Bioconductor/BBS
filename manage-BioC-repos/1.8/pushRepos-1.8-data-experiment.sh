#!/bin/sh

REPOS_ROOT="$HOME/PACKAGES/1.8/data/experiment"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/1.8/data

$HOME/bin/pushRepos-1.8-VIEWS.sh
