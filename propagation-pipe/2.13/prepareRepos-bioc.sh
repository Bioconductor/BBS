#!/bin/sh

cd "$HOME/manage-BioC-repos/2.13"

. ./config.sh
. ./prepareRepos-bioc.config
. ./prepareRepos.sh

VOCAB_SQLITE="biocViewsVocab.sqlite"
VOCAB_PATH="/home/biocadmin/R-3.0/library/biocViews/data/$VOCAB_SQLITE"

rm -f $VIEW_ROOT/biocViews/$VOCAB_SQLITE
sqlite3 $VOCAB_PATH .dump | sqlite $VIEW_ROOT/biocViews/$VOCAB_SQLITE
