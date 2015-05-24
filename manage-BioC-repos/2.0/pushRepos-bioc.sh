#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.0"
REPOS_ROOT="$HOME/PACKAGES/2.0/bioc"

rsync --delete -ave ssh $REPOS_ROOT webadmin@cobra:/extra/www/bioc/packages/2.0

$SCRIPT_HOME/pushRepos-VIEWS.sh
