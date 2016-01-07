#!/bin/bash

this_script=$(basename "$0")
echo "<<< Now starting $this_script at $(date) >>>"

cd "$HOME/manage-BioC-repos/3.3"

. ./config.sh
. ./prepareRepos-bioc.config
. ./prepareRepos.sh

VOCAB_SQLITE="biocViewsVocab.sqlite"
VOCAB_PATH="/home/biocadmin/R-3.3/library/biocViews/extdata/$VOCAB_SQLITE"

rm -f $VIEW_ROOT/biocViews/$VOCAB_SQLITE
sqlite3 $VOCAB_PATH .dump | sqlite $VIEW_ROOT/biocViews/$VOCAB_SQLITE

echo "<<< Now exiting $this_script at $(date) >>>"

