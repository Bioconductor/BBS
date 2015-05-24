#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.1"
REPOS_ROOT="$HOME/PACKAGES/2.1/data/experiment"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.1/data

$SCRIPT_HOME/pushRepos-VIEWS.sh
