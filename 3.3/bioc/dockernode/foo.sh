#!/bin/bash

echo ""
echo "======================================================================="
echo "STARTING postrun.sh"
echo "-------------------"

. ./config.sh

# Fix perms
cd $BBS_CENTRAL_RDIR
/bin/chmod +r . -R
cd nodes
/usr/bin/find . -type d -exec chmod 755 {} -c \;

set -e # Exit immediately if a simple command exits with a non-zero status.
####$BBS_HOME/BBS-make-OUTGOING.py

# Generate STATUS_DB.txt file
#####$BBS_HOME/BBS-make-STATUS_DB.py

# Generate PROPAGATE_STATUS_DB.txt
OUTGOING_DIR=$BBS_CENTRAL_RDIR/OUTGOING
PROPAGATE_STATUS_DB=$BBS_CENTRAL_RDIR/PROPAGATE_STATUS_DB.txt
$BBS_R_CMD -e "source('$BBS_HOME/utils/createPropagationDB.R');createPropagationList('$OUTGOING_DIR', '$PROPAGATE_STATUS_DB', 'bioc')"
