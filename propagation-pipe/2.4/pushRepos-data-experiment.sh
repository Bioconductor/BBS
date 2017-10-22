#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.4"
REPOS_ROOT="$HOME/PACKAGES/2.4/data/experiment"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.4/data

$SCRIPT_HOME/pushRepos-VIEWS.sh
