#!/bin/sh

cd "$HOME/manage-BioC-repos/3.2"

. ./config.sh

REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/extra"

echo "ATTENTION: **NOT** pushing files to website (yet)"

#rsync --delete -ave ssh $REPOS_ROOT webadmin@master.bioconductor.org:/extra/www/bioc/packages/$BIOC_VERSION
