#!/bin/sh

cd "$HOME/propagation-pipe/3.6"

. ./config.sh
. ./prepareRepos-bioc.config
. ./prepareRepos.sh

VOCAB_SQLITE="biocViewsVocab.sqlite"
VOCAB_PATH="/home/biocadmin/R-3.4/library/biocViews/extdata/$VOCAB_SQLITE"

rm -f $VIEW_ROOT/biocViews/$VOCAB_SQLITE
sqlite3 $VOCAB_PATH .dump | sqlite $VIEW_ROOT/biocViews/$VOCAB_SQLITE
