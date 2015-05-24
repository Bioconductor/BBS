#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.3"
REPOS_ROOT="$HOME/PACKAGES/2.3/bioc"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.3

$SCRIPT_HOME/pushRepos-VIEWS.sh
