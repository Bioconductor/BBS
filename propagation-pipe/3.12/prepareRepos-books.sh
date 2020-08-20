#!/bin/sh

cd "$HOME/propagation-pipe/3.12"

. ./config.sh

R_SCRIPT="library(tools)"
R_SCRIPT="$R_SCRIPT; write_PACKAGES('$HOME/PACKAGES/$BIOC_VERSION/src/contrib')"

echo "$R_SCRIPT" | $R --slave

chmod +r "$REPOS_ROOT" -Rc

echo "DONE."
