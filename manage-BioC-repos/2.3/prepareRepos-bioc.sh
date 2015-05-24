#!/bin/sh

SCRIPT_HOME="$HOME/manage-BioC-repos/2.3"

$SCRIPT_HOME/prepareRepos.sh $SCRIPT_HOME/prepareRepos-bioc.config

. $SCRIPT_HOME/prepareRepos-bioc.config

VOCAB_SQLITE="biocViewsVocab.sqlite"
VOCAB_PATH="/home/biocadmin/R-2.8/library/biocViews/data/$VOCAB_SQLITE"

rm -f $VIEW_ROOT/biocViews/$VOCAB_SQLITE
sqlite3 $VOCAB_PATH .dump | sqlite $VIEW_ROOT/biocViews/$VOCAB_SQLITE
