#!/bin/sh

cd "$HOME/propagation/3.20"

. ./config.sh

REPOS_SUBDIR="books"
REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/$REPOS_SUBDIR"
DESTDIR="webadmin@master.bioconductor.org:/extra/www/bioc/books/$BIOC_VERSION"

cd "$REPOS_ROOT/src/contrib"
$HOME/propagation/BBS-deploy-books.py "$DESTDIR"

