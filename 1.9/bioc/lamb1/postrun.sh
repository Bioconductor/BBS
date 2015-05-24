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
/bin/chmod g+w */buildsrc */buildbin -c

# Generate and publish the report
set -e # Exit immediately if a simple command exits with a non-zero status.
$BBS_HOME/BBS-report.py
REPORT_DIRNAME=`/usr/bin/dirname $BBS_REPORT_PATH`
REPORT_BASENAME=`/usr/bin/basename $BBS_REPORT_PATH`
cd "$REPORT_DIRNAME"
/bin/tar zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
/bin/mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
/usr/bin/rsync --delete -ave ssh "$BBS_REPORT_PATH/" "$BBS_REPORT_DEST_DIR/"

