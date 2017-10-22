#!/bin/sh

REPOS_ROOT="$HOME/PACKAGES/2.6/extra"

rsync --delete -ave ssh $REPOS_ROOT webadmin@master.bioconductor.org:/extra/www/bioc/packages/2.6
