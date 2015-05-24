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
$BBS_HOME/BBS-make-OUTGOING.py

# Generate STATUS_DB.txt file
$BBS_HOME/BBS-make-STATUS_DB.py

# Generate PROPAGATE_STATUS_DB.txt
OUTGOING_DIR=$BBS_CENTRAL_RDIR/OUTGOING
PROPAGATE_STATUS_DB=$BBS_CENTRAL_RDIR/PROPAGATE_STATUS_DB.txt
INTERNAL_REPOS=/home/biocadmin/PACKAGES/$BBS_BIOC_VERSIONED_REPO_PATH/
$BBS_R_CMD -e "source('$BBS_HOME/utils/createPropagationDB.R');createPropagationList('$OUTGOING_DIR', '$PROPAGATE_STATUS_DB', 'data/experiment', '$INTERNAL_REPOS')"


# Generate and publish HTML report
$BBS_HOME/BBS-report.py no-alphabet-dispatch
REPORT_DIRNAME=`/usr/bin/dirname $BBS_REPORT_PATH`
REPORT_BASENAME=`/usr/bin/basename $BBS_REPORT_PATH`
cd "$REPORT_DIRNAME"
/bin/tar zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
/bin/mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
# No more --delete here, too dangerous!
/usr/bin/rsync -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_REPORT_DEST_DIR/"
