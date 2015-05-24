#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.6"
REPOS_ROOT="$HOME/PACKAGES/2.6/bioc"

rsync --delete -ave ssh $REPOS_ROOT webadmin@master.bioconductor.org:/extra/www/bioc/packages/2.6

$SCRIPT_HOME/pushRepos-VIEWS.sh
