#!/bin/sh

cd "$HOME/propagation-pipe/3.13"

. ./config.sh
REPOS_ROOT="$HOME/PACKAGES/$BIOC_VERSION/books"

R_EXPR="library(tools)"
R_EXPR="$R_EXPR; write_PACKAGES('$REPOS_ROOT/src/contrib')"

$Rscript -e "$R_EXPR"

chmod +r "$REPOS_ROOT" -Rc

echo "DONE."
