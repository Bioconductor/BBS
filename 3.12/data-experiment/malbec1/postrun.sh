#!/bin/bash

echo ""
echo "======================================================================="
echo "STARTING postrun.sh"
echo "-------------------"

. ./config.sh

# Fix perms
cd $BBS_CENTRAL_RDIR
chmod +r . -R
find products-in -type d -exec chmod 755 {} -c \;

set -e # Exit immediately if a simple command exits with a non-zero status.

$BBS_PYTHON_CMD $BBS_HOME/BBS-make-OUTGOING.py

# Generate BUILD_STATUS_DB.txt file
$BBS_PYTHON_CMD $BBS_HOME/BBS-make-BUILD_STATUS_DB.py

# Generate PROPAGATION_STATUS_DB.txt
OUTGOING_DIR=$BBS_CENTRAL_RDIR/OUTGOING
PROPAGATION_STATUS_DB=$BBS_CENTRAL_RDIR/PROPAGATION_STATUS_DB.txt
INTERNAL_REPOS=/home/biocadmin/PACKAGES/$BBS_BIOC_VERSIONED_REPO_PATH/
$BBS_RSCRIPT_CMD --vanilla -e "source('$BBS_HOME/utils/createPropagationDB.R');createPropagationList('$OUTGOING_DIR', '$PROPAGATION_STATUS_DB', 'data/experiment', '$INTERNAL_REPOS')"

# Generate and publish HTML report
$BBS_PYTHON_CMD $BBS_HOME/BBS-report.py
REPORT_DIRNAME=$(dirname $BBS_REPORT_PATH)
REPORT_BASENAME=$(basename $BBS_REPORT_PATH)
cd "$REPORT_DIRNAME"
tar zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
# No more --delete here, too dangerous!
$BBS_RSYNC_CMD -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_PUBLISHED_REPORT_DEST_DIR/"
