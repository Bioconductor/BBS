#!/bin/sh

cd "$HOME/manage-BioC-repos/2.7"

. ./config.sh

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/data/annotation"

rsync --delete -ave ssh $REPOS_ROOT webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION/data

. ./pushRepos-VIEWS.sh
