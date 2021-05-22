#!/bin/bash

echo ""
echo "======================================================================="
this_script=$(basename "$0")
echo "<<< Now starting $this_script at $(date) >>>"
echo "-------------------"

# Adapted from : http://stackoverflow.com/a/246128/320399
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
. "${script_dir}"/config.sh

# Fix perms
cd "$BBS_CENTRAL_RDIR"
chmod +r . -R
find products-in -type d -exec chmod 755 {} -c \;

set -e # Exit immediately if a simple command exits with a non-zero status.

# Generate BUILD_STATUS_DB.txt file
$BBS_PYTHON_CMD $BBS_HOME/BBS-make-BUILD_STATUS_DB.py

# Generate and publish HTML report
$BBS_PYTHON_CMD $BBS_HOME/BBS-report.py no-alphabet-dispatch
REPORT_DIRNAME=$(dirname "$BBS_REPORT_PATH")
REPORT_BASENAME=$(basename "$BBS_REPORT_PATH")
cd "$REPORT_DIRNAME"
tar zcf "$REPORT_BASENAME.tgz" "$REPORT_BASENAME"
mv "$REPORT_BASENAME.tgz" "$BBS_REPORT_PATH"
# No more --delete here, too dangerous!
$BBS_RSYNC_CMD -ave 'ssh -o StrictHostKeyChecking=no' "$BBS_REPORT_PATH/" "$BBS_PUBLISHED_REPORT_DEST_DIR/"
