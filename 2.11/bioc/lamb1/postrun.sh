#!/bin/bash

echo ""
echo "======================================================================="
echo "STARTING postrun.sh"
echo "-------------------"

. ./config.sh

# Fix the perms
cd $BBS_CENTRAL_RDIR
/bin/chmod +r . -R
cd nodes
/usr/bin/find . -type d -exec chmod 755 {} -c \;

set -e # Exit immediately if a simple command exits with a non-zero status.
$BBS_HOME/BBS-make-OUTGOING.py

# Generate and publish the report
$BBS_HOME/BBS-report.py
REPORT_DIRNAME=`/usr/bin/dirname $BBS_REPORT_PATH`
REPORT_BASENAME=`/usr/bin/basename $BBS_REPORT_PATH`
cd "$REPORT_DIRNAME"
/bin/tar zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
/bin/mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
# No more --delete here, too dangerous!
/usr/bin/rsync -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_REPORT_DEST_DIR/"
