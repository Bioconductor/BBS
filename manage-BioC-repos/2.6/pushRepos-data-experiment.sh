#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.6"
REPOS_ROOT="$HOME/PACKAGES/2.6/data/experiment"

rsync --delete -ave ssh $REPOS_ROOT webadmin@master.bioconductor.org:/extra/www/bioc/packages/2.6/data

$SCRIPT_HOME/pushRepos-VIEWS.sh
